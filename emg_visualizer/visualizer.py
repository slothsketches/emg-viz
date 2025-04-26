import math
import pathlib
import typing as t

import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import RadioButtons, Slider

from .filters import (
    butter_bandpass_filter,
    gaussian_smooth_filter,
    median_filter,
    wavelet_denoise_filter,
)
from .utils import load_from_sample

cwd = pathlib.Path.cwd()


class PlotVisualizer:
    filters = {
        "Wavelet Denoising": wavelet_denoise_filter,
        "Gaussian Filter": gaussian_smooth_filter,
        "Butterworth Bandpass": butter_bandpass_filter,
        "Median Filter": median_filter,
    }

    __axes: "plt.Axes"

    def __init__(
        self,
        files: t.List[t.Union[pathlib.Path, str]],
        *,
        ncols: int = 2,
        title: t.Optional[str] = "EMG Signal: Raw vs Filtered (Comparison)",
        fs: int = 370,
        sliding_window_size: int = 250,
    ):
        assert files, "At least one data file is required."

        f: t.List[pathlib.Path] = []

        for file_ in files:
            if isinstance(file_, str):
                file_ = pathlib.Path(file_)

            try:
                file_.resolve(True)
                f.append(file_)
            except OSError:
                continue

        assert f, "None of the files specified were resolved."

        self.fs = fs
        self.sliding_window_size = sliding_window_size

        self.__files = f

        self.__raw_lines = []
        self.__filtered_lines = []

        self.__raw_signal = []
        self.__filtered_signals = []

        nrows = math.ceil(len(self.filters) / ncols)

        (self.__figure, self.__axes) = plt.subplots(
            nrows, ncols, figsize=(16, 10), sharex=True
        )

        if len(self.__files) > 1:
            plt.subplots_adjust(left=0.25, bottom=0.2)
        else:
            plt.subplots_adjust(bottom=0.2)

        for ax, name in zip(self.__axes.flat, self.filters):
            ax.set_title(f"{name} vs Raw")
            ax.set_ylabel("Amplitude")
            self.__raw_lines.extend(ax.plot([], [], label="Raw", alpha=0.5))
            self.__filtered_lines.extend(ax.plot([], [], label=name, linewidth=2))
            ax.legend()

        self.__axes[nrows - 1][0].set_xlabel("Time (s)")
        self.__axes[nrows - 1][1].set_xlabel("Time (s)")

        if title is not None:
            plt.suptitle(title, fontsize=16)

        if len(self.__files) > 1:
            self.__radio_axis = plt.axes([0.025, 0.4, 0.18, 0.5])
            self.__radio_widget = RadioButtons(
                self.__radio_axis,
                [f.as_posix() if f.parent != cwd else f.name for f in self.__files],
                active=0,
            )
            self.__radio_axis.set_title("Select file", fontsize=10)
            self.__radio_widget.on_clicked(self.__on_file_changed)
        else:
            self.__radio_axis = None
            self.__radio_widget = None

        if len(self.__files) > 1:
            self.__slider_axis = plt.axes([0.35, 0.08, 0.5, 0.03])
        else:
            self.__slider_axis = plt.axes([0.1, 0.08, 0.8, 0.03])

        self.__slider = Slider(
            self.__slider_axis, "Start at", 0, 1, valinit=0, valstep=1
        )
        self.__slider.on_changed(self.__on_slider_changed)
        self.__on_file_changed(self.__files[0].as_posix())

    @property
    def times(self):
        return np.arange(len(self.__raw_signal)) / self.fs

    def __process_file(self, file: str):
        self.__raw_signal = np.array(list(load_from_sample(file)))
        # TODO  Currently the butter bandpass does not accept
        #       data from the class. A filter adapter may help
        #       in this regard in the future.

        self.__filtered_signals = [
            filter_func(self.__raw_signal) for filter_func in self.filters.values()
        ]

    def __update_plot(self, start_at: int):
        end_at = start_at + self.sliding_window_size

        indexed_time = self.times[start_at:end_at]
        indexed_raw_data = self.__raw_signal[start_at:end_at]

        for i, (line_r, line_f, filtered_signals) in enumerate(
            zip(self.__raw_lines, self.__filtered_lines, self.__filtered_signals)
        ):
            line_r.set_data(indexed_time, indexed_raw_data)
            line_f.set_data(indexed_time, filtered_signals[start_at:end_at])
            self.__axes.flat[i].relim()
            self.__axes.flat[i].autoscale_view()

        self.__figure.canvas.draw_idle()

    def __on_file_changed(self, file: str):
        self.__process_file(file)

        self.__slider.valmax = len(self.__raw_signal) - self.sliding_window_size
        self.__slider.set_val(0)
        self.__slider.ax.set_xlim(self.__slider.valmin, self.__slider.valmax)

        self.__update_plot(0)

    def __on_slider_changed(self, value: int):
        self.__update_plot(value)

    def show(self):
        figure_manager = plt.get_current_fig_manager()

        if figure_manager is not None and hasattr(figure_manager, "window"):
            figure_manager.window.showMaximized()

        plt.show()


if __name__ == "__main__":
    PlotVisualizer(list((cwd / "emg_data").glob("*.txt"))).show()
