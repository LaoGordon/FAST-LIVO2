# FAST-LIVO2 RCL 外参配置说明

## 文件位置
`~/ws_localization/src/FAST-LIVO2/config/mid360.yaml`

## RCL 含义
在 FAST-LIVO2 源码 (`vio.cpp:58-59`) 中：
```cpp
Rci = Rcl * Rli;
Pci = Rcl * Pli + Pcl;
```
`Rcl` 表示 **LiDAR 坐标系 → Camera 光学坐标系** 的旋转矩阵。

## 坐标系定义
| 坐标系 | X轴 | Y轴 | Z轴 |
|--------|-----|-----|-----|
| LiDAR (mid360) | 前 | 左 | 上 |
| Camera (D435i 光学) | 右 | 下 | 前 |

## 实物安装
- 雷达与相机放置于同一水平面
- 朝向一致（同向前方）
- 无相对旋转

## RCL 推导
由于两者物理姿态一致，仅需处理坐标系定义差异：

| LiDAR | → | Camera |
|-------|---|--------|
| x_lidar (前) | → | z_camera (前) |
| y_lidar (左) | → | -x_camera (右) |
| z_lidar (上) | → | -y_camera (下) |

旋转矩阵（行主序）：

```
[ 0  -1   0 ]     x_camera = -y_lidar
[ 0   0  -1 ]     y_camera = -z_lidar
[ 1   0   0 ]     z_camera =  x_lidar
```

## 最终配置
```yaml
extrin_calib:
  Rcl: [0.0, -1.0, 0.0, 0.0, 0.0, -1.0, 1.0, 0.0, 0.0]
  Pcl: [0.078, 0.0, -0.041]  # 需根据实物测量更新
```

## 参考验证
该值与 `mid360_sim.yaml` 中经验证有效的 RCL 值一致：
```
# mid360_sim.yaml 注释:
#   理论值：[0, 0, 1; -1, 0, 0; 0, -1, 0] ❌ 着色点偏右
#   有效值：[0, -1, 0; 0, 0, -1; 1, 0, 0] ✅
```

## 注意事项
`Pcl` 是 LiDAR → Camera 的平移向量，需根据实物中雷达与相机的实际物理偏移量测量填写。

---

*更新日期: 2026-05-11*
