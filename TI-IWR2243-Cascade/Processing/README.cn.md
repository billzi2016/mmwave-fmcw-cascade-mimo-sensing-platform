# TI-IWR2243-Cascade Processing

该目录为 TI IWR2243 Cascade 毫米波雷达离线处理工程代码。

## 功能范围

1. 读取 4-chip cascade 原始 bin 数据
2. 完成四片数据拼接、频率校准、相位校准
3. 计算 Range FFT 与 Doppler FFT
4. 生成 `speed` 与 `angle` 热力图数据
5. 导出逐帧图片、聚合 `npz` 与可选视频

## 目录说明

- `main.py`：处理入口
- `src/iwr2243_cascade_processing/`：处理模块
- `requirements.txt`：运行依赖

## 运行方式

```bash
python main.py \
  --input-dir /path/to/raw_capture \
  --output-dir /path/to/output \
  --calibration-file /path/to/calibration.mat
```

如果希望统一控制 `speed / angle / point`，优先使用项目根目录下的 `../main.py`。

可选参数：

- `--workers`：处理进程数，默认使用 CPU 核数的一半
- `--frame-limit`：限制处理帧数
- `--range-limit`：热力图显示的距离上限，默认 `2.5`
- `--disable-speed`：关闭 `speed` 输出，仅保留 `angle`
- `--export-data-only`：只导出 `npz`，不生成图片
- `--render-video`：将逐帧图片交给 `ffmpeg` 合成为视频

## 输出结果

每个采集批次会输出一个独立目录，包含：

- 可选 `speed.h5`
- `angle.npz`
- `speed_heatmap/`
- `angle_heatmap/`
- 可选 `speed_heatmap.mp4`
- 可选 `angle_heatmap.mp4`
