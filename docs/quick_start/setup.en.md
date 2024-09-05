# Setup

!!! note

    Running the driving_log_replayer_v2 requires some additional steps on top of building and installing Autoware, so make sure that [driving_log_replayer_v2 installation](installation.md) has been completed first before proceeding.

    Sample map: Copyright 2020 TIER IV, Inc.

    Sample Dataset: Copyright 2022 TIER IV, Inc.

## Set up resources

1. Dataset and Map Setup (annotationless_perception, localization, obstacle_segmentation, perception)

   ```shell
   mkdir -p ~/driving_log_replayer_v2
   gdown -O ~/driving_log_replayer_v2/sample_dataset_v2.tar.zst 'https://docs.google.com/uc?export=download&id=1iCoykBBETI_rGfKEFYYb7LFydF-RJVkC'
   tar -I zstd -xvf ~/driving_log_replayer_v2/sample_dataset_v2.tar.zst -C ~/driving_log_replayer_v2/
   gdown -O ~/driving_log_replayer_v2/sample-map-planning.zip 'https://docs.google.com/uc?export=download&id=1499_nsbUbIeturZaDj7jhUownh5fvXHd'
   unzip -d ~/driving_log_replayer_v2/ ~/driving_log_replayer_v2/sample-map-planning.zip
   mv ~/driving_log_replayer_v2/sample-map-planning ~/driving_log_replayer_v2/sample_dataset/map
   ```

   You can also download manually.

   [dataset](https://drive.google.com/file/d/1iCoykBBETI_rGfKEFYYb7LFydF-RJVkC/view)

   [sample-map-planning](https://drive.google.com/file/d/1499_nsbUbIeturZaDj7jhUownh5fvXHd/view)

2. Dataset and Map Setup(yabloc, eagleye, ar_tag_based_localizer)

   ```shell
   gdown -O ~/driving_log_replayer_v2/sample_bag.tar.zst 'https://docs.google.com/uc?export=download&id=17ppdMKi4IC8J_2-_9nyYv-LAfW0M1re5'
   tar -I zstd -xvf ~/driving_log_replayer_v2/sample_bag.tar.zst -C ~/driving_log_replayer_v2/
   mv ~/driving_log_replayer_v2/sample_bag/*  ~/driving_log_replayer_v2/
   rmdir ~/driving_log_replayer_v2/sample_bag
   cp -r ~/driving_log_replayer_v2/ar_tag_based_localizer/map ~/driving_log_replayer_v2/eagleye/
   cp -r ~/driving_log_replayer_v2/ar_tag_based_localizer/map ~/driving_log_replayer_v2/yabloc/
   ```

   You can also download manually.

   [bag](https://drive.google.com/file/d/17ppdMKi4IC8J_2-_9nyYv-LAfW0M1re5/view)

3. Copy the sample scenario to the dataset directory

   ```shell
   # Specify the directory where autoware is installed. Change according to your environment.
   AUTOWARE_PATH=$HOME/ros_ws/awf
   # SAMPLE_ROOT=${AUTOWARE_PATH}/src/simulator/driving_log_replayer_v2/sample
   SAMPLE_ROOT=${AUTOWARE_PATH}/src/simulator/driving_log_replayer_v2/sample
   cp ${SAMPLE_ROOT}/annotationless_perception/scenario.yaml ~/driving_log_replayer_v2/annotationless_perception.yaml
   cp ${SAMPLE_ROOT}/ar_tag_based_localizer/scenario.yaml ~/driving_log_replayer_v2/ar_tag_based_localizer.yaml
   cp ${SAMPLE_ROOT}/eagleye/scenario.yaml ~/driving_log_replayer_v2/eagleye.yaml
   cp ${SAMPLE_ROOT}/localization/scenario.yaml ~/driving_log_replayer_v2/localization.yaml
   cp ${SAMPLE_ROOT}/obstacle_segmentation/scenario.yaml ~/driving_log_replayer_v2/obstacle_segmentation.yaml
   cp ${SAMPLE_ROOT}/perception/scenario.yaml ~/driving_log_replayer_v2/perception.yaml
   cp ${SAMPLE_ROOT}/yabloc/scenario.yaml ~/driving_log_replayer_v2/yabloc.yaml
   ```

4. Transform machine learning trained models

   ```shell
   source ~/autoware/install/setup.bash
   ros2 launch autoware_launch logging_simulator.launch.xml map_path:=$HOME/autoware_map/sample-map-planning vehicle_model:=sample_vehicle sensor_model:=sample_sensor_kit
   # Wait until the following file is created in ~/autoware/install/lidar_centerpoint/share/lidar_centerpoint/data
   # - pts_backbone_neck_head_centerpoint_tiny.engine
   # - pts_voxel_encoder_centerpoint_tiny.engine
   # When the file is output, press Ctrl+C to stop launch.
   ```