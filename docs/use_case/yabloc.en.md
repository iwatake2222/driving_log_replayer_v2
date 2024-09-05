# Evaluate YabLoc estimation

Evaluate whether Autoware's YabLoc, a camera based pcd-less localization, is working stably.

## Evaluation method

Launching the file executes the following steps:

1. Execute launch of evaluation node (`yabloc_evaluator_node`), `logging_simulator.launch` file and `ros2 bag play` command
2. Autoware receives sensor data input from prepared rosbag and performs localization estimation
3. Evaluation node subscribes to Autoware's output topics, determines whether the outputs meet the criteria, and outputs the results
4. When the playback of the rosbag is finished, Autoware's launch is automatically terminated, and the evaluation is completed.

### Availability of YabLoc

We use the output from `yabloc_monitor` via `/diagnostics` to evaluate whether YabLoc is available.

- `/diagnostics`

## Evaluation Result

The results are calculated for each subscription. The format and available states are described below.

### YabLoc Availability Normal

Information related to the monitored topic is extracted from `/diagnostics` which Component State Monitor outputs. If the most recent information is "OK", it is considered as pass.

### YabLoc Availability Error

The YabLoc availability evaluation output is marked as `Error` when conditions for `YabLoc Availability Normal` are not met.

## Topic name and data type used by evaluation node

Subscribed topics:

| Topic name   | Data type                             |
| ------------ | ------------------------------------- |
| /diagnostics | diagnostic_msgs::msg::DiagnosticArray |

Published topics:

| Topic name | Data type |
| ---------- | --------- |
| N/A        | N/A       |

## Service name and data type used by the evaluation node

| Service name                 | Data type              |
| ---------------------------- | ---------------------- |
| /api/localization/initialize | InitializeLocalization |

## Arguments passed to logging_simulator.launch

- perception: false
- planning: false
- control: false
- pose_source: yabloc
- twist_source: gyro_odom

## About simulation

State the information required to run the simulation.

### Topic to be included in the input rosbag

The following example shows the topic list available in evaluation input rosbag.

| Topic name                                         | Data type                                |
| -------------------------------------------------- | ---------------------------------------- |
| /sensing/camera/traffic_light/camera_info          | sensor_msgs/msg/CameraInfo               |
| /sensing/camera/traffic_light/image_raw/compressed | sensor_msgs/msg/CompressedImage          |
| /sensing/imu/tamagawa/imu_raw                      | sensor_msgs/msg/Imu                      |
| /vehicle/status/velocity_status                    | autoware_vehicle_msgs/msg/VelocityReport |

### Topics that must NOT be included in the input rosbag

| Topic name | Data type               |
| ---------- | ----------------------- |
| /clock     | rosgraph_msgs/msg/Clock |

The clock is output by the --clock option of ros2 bag play, so if it is recorded in the bag itself, it is output twice, so it is not included in the bag.

## About Evaluation

State the information necessary for the evaluation.

### Scenario Format

See [sample](https://github.com/tier4/driving_log_replayer_v2/blob/develop/sample/yabloc/scenario.yaml).

### Evaluation Result Format

See [sample](https://github.com/tier4/driving_log_replayer_v2/blob/develop/sample/yabloc/result.json).

Examples of each evaluation are described below.
**NOTE: common part of the result file format, which has already been explained, is omitted.**

Availability Result example:

```json
{
  "Availability": {
    "Result": { "Total": "Success or Fail", "Frame": "Success, Fail, or Warn" },
    "Info": {}
  }
}
```