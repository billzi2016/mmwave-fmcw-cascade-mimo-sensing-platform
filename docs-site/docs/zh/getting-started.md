# 快速开始

这一页用最短路径帮助你理解仓库。

## 仓库结构

代码围绕两套雷达系统组织：

```text
mmwave-fmcw-cascade-mimo-sensing-platform/
├── DEMO/
├── TI-IWR2243-Cascade/
│   ├── Processing/
│   └── Visualization/
├── TI-IWR6843/
│   ├── Processing/
│   └── Visualization/
└── docs-site/
```

`Processing` 目录负责把原始雷达数据处理成结构化数组、热力图和点云数据。`Visualization` 目录负责把处理结果导出为图片、视频和归一化资产。

## 推荐阅读顺序

如果你刚开始看这个项目，可以按这个顺序：

1. 先看 `DEMO/`，了解最终结果长什么样。
2. 看仓库根目录 README，理解两条雷达路径。
3. 根据关注的雷达型号进入对应 Processing README。
4. 根据需要查看 Visualization README。
5. 需要慢一点理解处理链路时，再看这套文档站。

## 最小理解模型

这个项目把原始雷达采样逐步转换成更容易理解的结果：

```text
原始采样
-> 拆帧和通道重建
-> 校准
-> Range FFT
-> Doppler FFT
-> Angle FFT / AoA
-> 热力图和点云
-> 图片、视频、H5、NPZ
```

不需要一开始就理解所有信号处理细节。先弄清输入目录、输出目录和目标结果类型，再逐步深入。

## 在哪里运行命令

每个处理或可视化子项目都有自己的 `main.py`。

- 处理命令通常在 `Processing/` 目录运行。
- 可视化命令通常在 `Visualization/` 目录运行。
- 如果希望一次运行 IWR2243 级联处理和点云可视化，可以使用 `TI-IWR2243-Cascade/main.py`。
