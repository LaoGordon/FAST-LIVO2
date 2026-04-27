# FAST-LIVO2 MID360 外参更新 & IMU/LiDAR 时间同步修复

> 日期: 2026-04-27
> 板子: D-Robotics RDK S100P
> ROS2: Humble

---

## 改动 1: 更新相机到雷达外参 Rcl

**文件**: `config/mid360.yaml`

**修改**:
```diff
- Rcl: [-0.00923841, 0.48569887, 0.87407738, -0.99995383, -0.00679900, -0.00679084, 0.00264455, -0.87409976, 0.48573925]
+ Rcl: [-0.004175, -0.999883, -0.014743, 0.577223, 0.009629, -0.816530, 0.816576, -0.011919, 0.577115]
```

Pcl 保持不变: `[0.02199903, 0.03567358, -0.03084671]`

---

## 改动 2: 修复 IMU/LiDAR 时间跳变

**文件**: `include/LIVMapper.h`, `src/LIVMapper.cpp`

### 问题根因

原方案使用 `std::round(last_timestamp_lidar - timestamp)` 对每条 IMU 消息做硬对齐，存在以下缺陷:

1. **Livox 驱动时间戳格式不一致**: MID360 的 Livox ROS2 驱动存在已知 bug，时间戳可能在 epoch 时间 (~17.7 亿秒) 和系统启动时间 (~几百秒) 之间切换
2. **`round()` 无法平滑跟踪**: 偏移变化时 `round()` 产生阶跃响应，导致 IMU 时间戳突变
3. **LiDAR 时间域切换时数据丢失**: 当 LiDAR 时间戳换域，IMU 纠正后的时间戳被误判为 loop-back 而丢弃
4. **原 LiDAR 回调 sync 检测被注释**: 检测到跳变后无处理动作，注释的 `imu_time_offset = timediff_imu_wrt_lidar` 从未执行

### 修复方案

#### LiDAR 回调 (`livox_pcl_cbk`)
- 新增 LiDAR 自身时间戳跳变检测: 相邻两帧 LiDAR 时间差 > 1s 时
- 触发重置动作: 清除 IMU 缓冲、重置偏移初始化标志、清零 `last_timestamp_imu`

```cpp
if (ros_driver_fix_en && last_timestamp_lidar > 0.0 && 
    fabs(cur_head_time - last_timestamp_lidar) > 1.0)
{
    imu_buffer.clear();
    lidar_imu_offset_initialized_ = false;
    last_timestamp_imu = -1.0;
}
```

#### IMU 回调 (`imu_cbk`)
- **替换** `std::round()` 硬对齐 → 指数平滑偏移跟踪 (alpha=0.01)
- 偏移变化 > 5s 时自动重置（应对 LiDAR 时间域切换）
- 每次重置同步清零 `last_timestamp_imu = -1.0`，防止误判 loop-back

```cpp
if (ros_driver_fix_en)
{
    double current_offset = last_timestamp_lidar - raw_imu_time;
    if (!lidar_imu_offset_initialized_) {
        imu_time_offset = std::round(current_offset);  // 首次用 round 快速初始化
        last_timestamp_imu = -1.0;
    } else if (fabs(current_offset - imu_time_offset) > 5.0) {
        imu_time_offset = std::round(current_offset);  // 大跳变时快速重置
        last_timestamp_imu = -1.0;
    } else {
        imu_time_offset = 0.01 * current_offset + 0.99 * imu_time_offset;  // 平滑跟踪
    }
    timestamp += imu_time_offset;
}
```

#### 新增成员变量
```cpp
bool lidar_imu_offset_initialized_ = false;  // LIVMapper.h:106
```

### 向后兼容

- `ros_driver_fix_en=false` 时保持原始行为不变
- 编译通过 (`colcon build --packages-select fast_livo`)

---

## Commit

[FAST-LIVO2@b3385e2](https://github.com/LaoGordon/FAST-LIVO2/commit/b3385e2) — fix: robust IMU-LiDAR time sync + update mid360 camera extrinsic
