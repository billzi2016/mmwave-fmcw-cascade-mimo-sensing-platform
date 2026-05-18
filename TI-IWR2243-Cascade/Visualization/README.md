# TI-IWR2243-Cascade Visualization

该目录为 TI IWR2243 Cascade 点云可视化与标准化工程代码。

## 功能范围

1. 读取 `Cascade.mat`
2. 提取点云子空间
3. 进行 SNR 权重采样与 DBSCAN 清理
4. 输出固定点数点云 `npz`
5. 导出逐帧点云图片与可选视频

## 运行方式

```bash
python main.py \
  --input-mat /path/to/Cascade.mat \
  --output-dir /path/to/output
```

如果希望统一控制 `speed / angle / point`，优先使用项目根目录下的 `../main.py`。

可选参数：

- `--workers`：绘图进程数，默认使用 CPU 核数的一半
- `--target-points`：每帧保留的点数，默认 `2048`
- `--render-video`：将点云图片交给 `ffmpeg` 合成为视频
- `--export-data-only`：只导出 `npz`，不生成图片
