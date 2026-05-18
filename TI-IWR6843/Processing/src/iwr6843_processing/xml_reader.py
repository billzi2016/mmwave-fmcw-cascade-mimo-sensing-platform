from pathlib import Path
import xml.etree.ElementTree as et


def parse_xml(xml_path: str | Path) -> tuple[float, float, float, float, int, int, float, int]:
    """解析 TI 雷达参数 XML。"""
    root = et.parse(Path(xml_path)).getroot()

    profile_cfg = root.find(".//apiname_profile_cfg")
    frame_cfg = root.find(".//apiname_frame_cfg")

    if profile_cfg is None or frame_cfg is None:
        raise ValueError(f"未在 XML 中找到 profile/frame 配置：{xml_path}")

    freq_slope = float(profile_cfg.find('.//param[@name="freqSlopeConst"]').get("value")) * 1e12
    ramp_end_time = float(profile_cfg.find('.//param[@name="rampEndTime"]').get("value"))
    sample_rate = float(profile_cfg.find('.//param[@name="digOutSampleRate"]').get("value")) * 1e3
    start_freq = float(profile_cfg.find('.//param[@name="startFreqConst"]').get("value")) * 1e9
    n_samples = int(profile_cfg.find('.//param[@name="numAdcSamples"]').get("value"))

    frame_count = int(frame_cfg.find('.//param[@name="frameCount"]').get("value"))
    periodicity = float(frame_cfg.find('.//param[@name="periodicity"]').get("value")) * 1e-3
    n_chirps = int(frame_cfg.find('.//param[@name="loopCount"]').get("value"))

    return freq_slope, ramp_end_time, sample_rate, start_freq, n_samples, frame_count, periodicity, n_chirps
