# TI-IWR6843 Visualization

该目录为 TI IWR6843 毫米波雷达结果可视化工程代码。

## 目录说明

- `main.py`：可视化入口
- `src/iwr6843_visualization/`：可视化模块
- `requirements.txt`：运行依赖

## 功能范围

1. 读取处理阶段导出的 `h5`
2. 导出距离、速度、AoA 角度热力图
3. 读取或生成点云 `npz`
4. 生成点云静态图或视频

## 并发策略

- 生成图片和 `npz` 时默认使用 CPU 核数的一半进行多进程批处理
- 生成视频时使用单进程顺序执行，并交给 `ffmpeg` 导出

## 输出规则

- `AoA / angle` 默认输出
- `point cloud` 默认输出
- 如果结果中存在 `speed_profiles`，则输出 `speed`
- 如果结果中不存在 `speed_profiles`，则自动跳过 `speed` 可视化

## 运行方式

生成图片和 `npz`：

```bash
python main.py --input-dir /path/to/h5 --output-dir /path/to/output
```

生成视频：

```bash
python main.py --input-dir /path/to/h5 --output-dir /path/to/output --render-video
```
