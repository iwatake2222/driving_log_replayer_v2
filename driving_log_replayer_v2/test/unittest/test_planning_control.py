# Copyright (c) 2024 TIER IV.inc
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

from typing import Literal

from pydantic import ValidationError
import pytest
from tier4_metric_msgs.msg import Metric
from tier4_metric_msgs.msg import MetricArray

from driving_log_replayer_v2.planning_control import KinematicCondition
from driving_log_replayer_v2.planning_control import LaneCondition
from driving_log_replayer_v2.planning_control import LaneInfo
from driving_log_replayer_v2.planning_control import LeftRight
from driving_log_replayer_v2.planning_control import MetricCondition
from driving_log_replayer_v2.planning_control import Metrics
from driving_log_replayer_v2.planning_control import MinMax
from driving_log_replayer_v2.planning_control import PlanningControlScenario
from driving_log_replayer_v2.scenario import load_sample_scenario


def test_scenario() -> None:
    scenario: PlanningControlScenario = load_sample_scenario(
        "planning_control",
        PlanningControlScenario,
    )
    assert scenario.ScenarioName == "sample_planning_control"
    assert scenario.Evaluation.Conditions.MetricConditions[0].condition_type == "all_of"


def test_min_max_validation() -> None:
    with pytest.raises(ValidationError):
        MinMax(min=3.0, max=1.0)


def test_left_right_validation() -> None:
    with pytest.raises(ValidationError):
        LeftRight(left=-3.0, right=1.0)


def test_left_right_match_condition() -> None:
    left_right = LeftRight(left=1.0, right=1.0)
    assert left_right.match_condition(0.5)
    assert left_right.match_condition(2.0) is False
    assert left_right.match_condition(-2.0) is False


def test_lane_info_match_condition() -> None:
    lane_info = LaneInfo(id=1, s=1.0, t=LeftRight(left=1.0, right=1.0))
    assert lane_info.match_condition((1, 2.0, 0.5), start_condition=True)
    assert lane_info.match_condition((2, 2.0, 0.5), start_condition=True) is False
    assert lane_info.match_condition((1, 0.5, 0.5), start_condition=True) is False
    assert lane_info.match_condition((1, 2.0, 3.0), start_condition=True) is False
    assert lane_info.match_condition((1, 2.0, 3.0))  # if goal t is not used


def test_lane_condition_started_ended() -> None:
    lane_condition = LaneCondition(
        start=LaneInfo(id=1, s=1.0, t=LeftRight(left=1.0, right=1.0)),
        end=LaneInfo(id=2, s=2.0),
    )
    assert lane_condition.started is False
    assert lane_condition.ended is False
    assert lane_condition.is_started((1, 0.5, 0.5)) is False
    assert lane_condition.is_started((1, 2.0, 0.5))
    assert lane_condition.is_started((2, 2.0))  # Once True, do not change.
    assert lane_condition.is_ended((2, 1.0, 1.0)) is False
    assert lane_condition.is_ended((2, 3.0, 1.0))


def test_kinematic_state_match_condition() -> None:
    kinematic_condition = KinematicCondition(
        vel=MinMax(min=0.0, max=1.0),
        acc=MinMax(min=0.0, max=2.0),
        jerk=MinMax(min=0.0, max=3.0),
    )
    assert kinematic_condition.match_condition((0.5, 1.0, 2.0))
    assert kinematic_condition.match_condition((2.0, 1.0, 2.0)) is False
    assert kinematic_condition.match_condition((0.5, -1.0, 2.0)) is False
    assert kinematic_condition.match_condition((0.5, 1.0, -1.0)) is False


def create_condition(condition_type: Literal["any_of", "all_of"]) -> MetricCondition:
    return MetricCondition(
        topic="/control/autonomous_emergency_braking/metrics",
        name="decision",
        value="brake",
        condition_type=condition_type,
        lane_condition=LaneCondition(
            start=LaneInfo(id=1, s=1.0, t=LeftRight(left=1.0, right=1.0)),
            end=LaneInfo(id=2, s=2.0),
        ),
        kinematic_condition=KinematicCondition(
            vel=MinMax(min=0.0, max=1.0),
            acc=MinMax(min=0.0, max=2.0),
            jerk=MinMax(min=0.0, max=3.0),
        ),
    )


def create_metric_msg(
    *,
    is_started: bool = True,
    is_ended: bool = False,
    match_kinematic_state: bool = True,
) -> tuple[MetricArray, MetricArray]:
    aeb_metric = Metric(name="decision", unit="", value="brake")

    lane_id = Metric(name="ego_lane_info/lane_id", value="1" if is_ended is False else "2")
    lane_s = Metric(name="ego_lane_info/s", value="2.0" if is_started else "1.0")
    lane_t = Metric(name="ego_lane_info/t", value="0.5")

    ks_vel = Metric(name="kinematic_state/vel", value="0.5" if match_kinematic_state else "2.0")
    ks_acc = Metric(name="kinematic_state/acc", value="1.0")
    ks_jerk = Metric(name="kinematic_state/jerk", value="2.0")

    aeb_metric = MetricArray(metric_array=[aeb_metric])
    control_evaluator_metric = MetricArray(
        metric_array=[lane_id, lane_s, lane_t, ks_vel, ks_acc, ks_jerk]
    )
    return aeb_metric, control_evaluator_metric


def test_metrics_not_started() -> None:
    condition = create_condition("any_of")
    evaluation_item: Metrics = Metrics(name="control_0", condition=condition)
    aeb_metric, control_metric = create_metric_msg(is_started=False)
    assert evaluation_item.set_frame(aeb_metric, control_metric) is None


def test_metrics_finished() -> None:
    condition = create_condition("any_of")
    evaluation_item: Metrics = Metrics(name="control_0", condition=condition)
    aeb_metric, control_metric = create_metric_msg(is_started=False)
    assert evaluation_item.set_frame(aeb_metric, control_metric) is None


def test_metrics_success_any_of() -> None:
    condition = create_condition("any_of")
    evaluation_item: Metrics = Metrics(name="control_0", condition=condition)
    aeb_metric, control_metric = create_metric_msg()
    frame_dict = evaluation_item.set_frame(aeb_metric, control_metric)
    assert evaluation_item.success is True
    assert frame_dict == {
        "Result": {"Total": "Success", "Frame": "Success"},
        "Info": {
            "TotalPassed": 1,
            "Decision": "brake",
            "LaneInfo": (1, 2.0, 0.5),
            "KinematicState": (0.5, 1.0, 2.0),
        },
    }
    aeb_metric, control_metric = create_metric_msg(match_kinematic_state=False)
    frame_dict = evaluation_item.set_frame(
        aeb_metric, control_metric
    )  # any_of is OK if one of them succeeds.
    assert evaluation_item.success is True
    assert frame_dict == {
        "Result": {"Total": "Success", "Frame": "Fail"},
        "Info": {
            "TotalPassed": 1,
            "Decision": "brake",
            "LaneInfo": (1, 2.0, 0.5),
            "KinematicState": (2.0, 1.0, 2.0),
        },
    }


def test_metrics_fail_any_of() -> None:
    condition = create_condition("any_of")
    evaluation_item: Metrics = Metrics(name="control_0", condition=condition)
    aeb_metric, control_metric = create_metric_msg(match_kinematic_state=False)
    frame_dict = evaluation_item.set_frame(aeb_metric, control_metric)
    assert evaluation_item.success is False
    assert frame_dict == {
        "Result": {"Total": "Fail", "Frame": "Fail"},
        "Info": {
            "TotalPassed": 0,
            "Decision": "brake",
            "LaneInfo": (1, 2.0, 0.5),
            "KinematicState": (2.0, 1.0, 2.0),
        },
    }


def test_metrics_fail_all_of() -> None:
    condition = create_condition("all_of")
    evaluation_item: Metrics = Metrics(name="control_0", condition=condition)
    aeb_metric, control_metric = create_metric_msg()
    frame_dict = evaluation_item.set_frame(aeb_metric, control_metric)
    assert evaluation_item.success is True
    assert frame_dict == {
        "Result": {"Total": "Success", "Frame": "Success"},
        "Info": {
            "TotalPassed": 1,
            "Decision": "brake",
            "LaneInfo": (1, 2.0, 0.5),
            "KinematicState": (0.5, 1.0, 2.0),
        },
    }
    aeb_metric, control_metric = create_metric_msg(match_kinematic_state=False)
    frame_dict = evaluation_item.set_frame(
        aeb_metric, control_metric
    )  # ALL_OF is not allowed if even one fails.
    assert evaluation_item.success is False
    assert frame_dict == {
        "Result": {"Total": "Fail", "Frame": "Fail"},
        "Info": {
            "TotalPassed": 1,
            "Decision": "brake",
            "LaneInfo": (1, 2.0, 0.5),
            "KinematicState": (2.0, 1.0, 2.0),
        },
    }
