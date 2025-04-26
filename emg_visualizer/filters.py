import numpy as np
import pywt
from scipy.ndimage import gaussian_filter1d
from scipy.signal import butter, filtfilt, medfilt

SignalType = np.ndarray[float]


def wavelet_denoise_filter(
    signal: SignalType, wavelet: str = "db4", level: int = 3
) -> SignalType:
    coeffs = pywt.wavedec(signal, wavelet, level=level)
    sigma = np.median(np.abs(coeffs[-1])) / 0.6745
    uthresh = sigma * np.sqrt(2 * np.log(len(signal)))
    coeffs_denoised = [pywt.threshold(c, uthresh, mode="soft") for c in coeffs]
    return pywt.waverec(coeffs_denoised, wavelet)[: len(signal)]


def gaussian_smooth_filter(signal: SignalType, sigma: int = 2) -> SignalType:
    return gaussian_filter1d(signal, sigma=sigma)


def butter_bandpass_filter(
    signal: SignalType,
    lowcut: int = 20,
    highcut: int = 150,
    fs: int = 370,
    order: int = 4,
) -> SignalType:
    nyq = 0.5 * fs
    low = lowcut / nyq
    high = highcut / nyq
    b, a = butter(order, [low, high], btype="band")
    return filtfilt(b, a, signal)


def median_filter(signal: SignalType, kernel_size: int = 11) -> SignalType:
    return medfilt(signal, kernel_size=kernel_size)
