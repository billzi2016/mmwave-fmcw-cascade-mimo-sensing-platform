import numpy as np


def norm(data: np.ndarray) -> np.ndarray:
    """做最大最小值归一化，并兼容常量数组。"""
    data_min = np.min(data)
    data_max = np.max(data)
    if data_max == data_min:
        return np.zeros_like(data, dtype=np.float32)
    return (data - data_min) / (data_max - data_min)
