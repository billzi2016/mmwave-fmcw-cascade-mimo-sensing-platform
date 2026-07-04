# 雷达概念

这一页介绍代码中反复出现的雷达概念。

如果说 **雷达基础** 是起点，那么这一页就是把基础概念连接到仓库里的配置参数和代码模块。

## FMCW

FMCW 雷达发射频率随时间变化的 chirp。目标回波与发射信号混频后，会得到和目标距离相关的拍频。

在代码中，这表现为一串 ADC 采样。Range FFT 会把这些采样转换为距离 bin。

## 距离

距离表示目标离雷达的远近。在仓库里，距离会出现在：

- `range_profiles`，
- 距离热力图，
- 速度图和角度图的距离坐标轴，
- H5 元数据中的距离换算参数。

## Doppler

Doppler 描述目标相对雷达的运动。多个 chirp 让系统可以观察相位随时间的变化。Doppler FFT 会把这种变化转换为速度 bin。

速度热力图展示能量在距离和速度上的分布。

## AoA 和角度

AoA 用于估计信号来自哪个方向。代码使用虚拟天线组构建角度谱。

角度热力图展示不同距离和角度上的响应强度。在点云链路中，角度估计会和距离结合，计算 x、y、z 坐标。

## 虚拟阵列

虚拟阵列由 TX/RX 组合形成。它能提供更多空间采样点。

这一点在 IWR2243 Cascade 路径里尤其重要，因为多个芯片会拼接成更大的感知孔径。

## 点云

雷达点云是一组估计出的目标点。本仓库中的点云行通常包含：

- x，
- y，
- z，
- 强度或 SNR，
- 有时还包含速度或其他诊断字段。

点云看起来更直观，但它依赖前面的多个步骤：拆帧、FFT、候选点选择、角度估计和坐标转换。

## 配置参数用白话怎么理解

雷达代码里参数很多，第一次看会很乱。但大多数参数其实都在回答几类问题。

### 采样参数

这些参数定义原始信号如何采集：

- `num_adc_samples` 或 `n_samples`：一个 chirp 里采多少个 ADC 点。
- `adc_sample_rate` 或 `sample_rate`：ADC 采样速度。
- `start_frequency_hz` 或 `start_freq`：雷达载频。
- `chirp_slope_hz_per_s` 或 `freq_slope`：chirp 频率随时间变化的速度。
- `chirp_ramp_end_time_s` 或 `ramp_end_time`：chirp ramp 持续时间。

这些参数会影响距离计算。例如采样率和 chirp slope 会参与拍频到距离的换算。

### Chirp 和帧参数

这些参数定义重复测量如何组织：

- `nchirp_loops` 或 `n_chirps`：一帧里重复多少个 chirp。
- `num_chirps_in_loop`：一个 loop 中使用多少个 TX 槽位。
- `frame_periodicity_s` 或 `periodicity`：帧与帧之间的时间间隔。

Doppler 处理需要重复 chirp。没有重复 chirp，就不能用同样方式估计目标速度。

### 天线参数

这些参数定义空间感知布局：

- `num_tx` 或 `n_tx`：发射通道数。
- `num_rx` 或 `n_rx`：接收通道数。
- `rx_for_mimo`：级联 MIMO 处理使用的 RX 重排顺序。
- `ANTENNA_86`：IWR2243 级联角度热力图使用的虚拟天线映射。
- `radar_matrix`：IWR6843 角度和点云路径使用的虚拟天线分组。

这些参数影响角度估计。通道顺序错了，图可能仍然不为空，但空间含义会错。

### FFT 参数

这些参数定义输出分辨率和数组形状：

- `range_fft_size` 或 `range_fft_n`：沿 ADC 采样维的 FFT 点数。
- `doppler_fft_size` 或 `speed_fft_n`：沿 chirp 维的 FFT 点数。
- `angle_fft_size` 或 `angle_fft_n`：沿虚拟天线维的 FFT 点数。

更大的 FFT 点数可以得到更细的 bin，但不会凭空创造新的物理信息。它主要改变频率网格和输出形状。

### 显示和过滤参数

这些参数控制输出是否易读：

- `range_limit_m`：热力图显示的最大距离。
- `target_points`：每帧点云固定点数。
- `threshold_percentile`：点云强度筛选百分位。
- `speed_cut`：零速度附近显示的速度范围比例。
- `render_video`：是否导出 MP4 视频。
- `export_data_only` 或 `export_assets_only`：是否跳过图片/视频，只保存数据。

这些参数不改变原始采集，主要影响保存和显示结果。

## IWR2243 Cascade 的配置有什么不同

IWR2243 Cascade 路径有更多多设备配置，因为四个雷达芯片要被当成一个更大的感知系统。

重要配置包括：

- `num_devices = 4`：期望有四个芯片。
- `num_rx_per_device = 4`：每个设备贡献四路接收通道。
- 总 RX 通道数是 `num_devices * num_rx_per_device`。
- `tx_to_enable` 定义处理链使用的 TX 顺序。
- `rx_for_mimo` 把通道重排成期望的 MIMO 布局。
- 校准参数控制频率和相位修正。

因此级联路径在 FFT 前会花更多代码处理文件分组、通道重排和校准。

## IWR6843 的配置有什么不同

IWR6843 路径从一个 XML 文件和一个或多个 BIN 文件开始。许多重要采集参数来自 XML，而不是大型静态级联配置。

重要配置包括：

- XML 提供频率斜率、采样率、起始频率、采样点数、帧数和 chirp 数。
- `ProcessingConfig` 提供 FFT 点数、点云数量、角度搜索设置和窗函数。
- `frame_extractor.py` 定义原始 LVDS 采样如何变成虚拟天线数据。
- `radar_matrix` 定义角度处理使用哪些虚拟天线组合。

这条路径因为是单设备，整体更容易跟读，但拆帧仍然依赖精确的数据布局假设。

## 为什么不要随便改参数

很多参数和硬件采集设置绑定。如果某个值描述的是采集时雷达如何配置的，采集后随便改它，会让解析或物理换算变错。

比较适合实验的参数：

- 输出目录，
- 帧数限制，
- 是否渲染视频，
- 距离显示上限，
- 点云目标点数，
- 可视化阈值。

需要谨慎修改的参数：

- 采样率，
- chirp slope，
- ADC 采样点数，
- chirp 数，
- TX/RX 映射，
- 校准矩阵。

不确定时，先检查数组形状和输出文件，再考虑改物理参数。
