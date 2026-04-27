# FAST-LIVO2 建图流程修复记录

> 日期: 2026-04-24
> 板子: D-Robotics RDK S100P
> ROS2: Humble

---

## 问题 1: Livox MID360 初始化失败

**现象**: `bind failed → Failed to init livox lidar sdk`

**原因**: `MID360_config.json` 中 `host_net_info` IP 错误配置为 `192.168.1.5`，实际板子 eth1 地址为 `192.168.1.50`。雷达 IP 应为 `192.168.1.135`。

**修复** (`livox_ros_driver2/config/MID360_config.json`):
```diff
- host_net_info IP: 192.168.1.5  → 192.168.1.50 (板子 eth1 实际地址)
- lidar_configs[0].ip: 192.168.1.12 → 192.168.1.135 (雷达实际地址)
```

**Commit**: [livox_ros_driver2@c950aa3](https://github.com/LaoGordon/livox_ros_driver2/commit/c950aa3)

---

## 问题 2: 点云初始化阶段漂移

**现象**: 建图开始时点云随机漂移，有时漂有时不漂，甚至静止时也漂。

**根因**: MID360 倾斜安装 + 初始化阶段前 5+ 帧 LiDAR ICP 全部失败:
```
改前: effective feature: 0, residual: nan  ← 连续5帧
改后: effective feature: 60, residual: 0.02 ← 第1帧即有配准
```

**修复** (`FAST-LIVO2/config/mid360.yaml`):
```diff
- preprocess.filter_size_surf: 0.5 → 0.2  (保留更多特征点)
- lio.min_eigen_value: 0.0025      → 0.001 (降低平面特征门槛)
- preprocess.blind: 0.5            → 0.3   (缩小盲区)
```

**Commit**: [FAST-LIVO2@074c5d4](https://github.com/LaoGordon/FAST-LIVO2/commit/074c5d4)

---

## 备忘

- MID360 通过 eth1 (192.168.1.50) 连接，雷达 IP 192.168.1.135
- RViz 在嵌入式板子上需要 `use_rviz:=False`（无 X 显示）
- D435i IMU 不使用（使用 MID360 内置 IMU，话题 `/livox/imu`）
- 启动后保持机器人静止 3 秒等待 IMU 初始化完成
