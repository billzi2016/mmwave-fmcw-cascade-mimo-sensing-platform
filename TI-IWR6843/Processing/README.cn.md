# TI-IWR6843 Processing

该目录为 TI IWR6843 毫米波雷达离线处理工程代码。

## 目录说明

- `main.py`：处理入口
- `src/iwr6843_processing/`：处理模块
- `requirements.txt`：运行依赖

## 处理链路

1. 读取目录中的 `xml` 参数文件
2. 读取目录中的 `bin` 原始采样文件
3. 拆帧并重建虚拟天线数据
4. 执行距离 FFT、多普勒 FFT、AoA 角度 FFT
5. 直接生成点云并导出 `h5` / `npz`

## 运行方式

```bash
python main.py --input-dir /path/to/raw_data --output-dir /path/to/output
```

可选参数：

- `--workers`：指定进程数，默认使用 CPU 核数的一半
- `--windows`：指定窗函数，默认 `blackmanharris`

## 输出结果

每个 `bin` 文件会按窗函数导出一个 `h5` 文件，内容包括：

- `range_profiles`
- `speed_profiles`
- `angle_profiles`
- `points_frames`
- `param`

同时会额外导出一个点云结果文件：

- `*_points.npz`
