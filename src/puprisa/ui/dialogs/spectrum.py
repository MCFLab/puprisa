# puprisa/ui/dialogs/spectrum_dialog.py
"""Non-modal dialog for FFT / PSD / RIN spectral analysis of ROI curves."""
from __future__ import annotations

import csv
from pathlib import Path

import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import QDialog, QFileDialog, QMessageBox

from puprisa.core.phasor import compute_fft, compute_psd
from puprisa.model.curve_manager import CurveManager
from puprisa.model.stack_manager import StackManager
from puprisa.ui.generated.dialog_spectrum import Ui_spectrumDialog


class SpectrumDialog(QDialog):
    def __init__(
        self,
        curve_manager: CurveManager,
        stack_manager: StackManager,
        parent=None,
        space: str = "pixel",
    ):
        super().__init__(parent)
        self.ui = Ui_spectrumDialog()
        self.ui.setupUi(self)

        self._curve_manager = curve_manager
        self._stack_manager = stack_manager
        self._space = space

        self._last_results: list[dict] = []
        self._last_mode: str = "fft"
        self._last_y_label: str = ""
        self._last_freq_label: str = "Frequency (1/ps)"

        # 按钮信号
        self.ui.calculateButton.clicked.connect(self._calculate)
        self.ui.viewButton.clicked.connect(self._view_standalone)
        self.ui.exportButton.clicked.connect(self._export_data)
        self.ui.exitButton.clicked.connect(self.close)

        # 默认选中 FFT
        self.ui.fftButton.setChecked(True)

        # 初始化画布
        self._setup_figure()

    # ------------------------------------------------------------------
    # 画布初始化
    # ------------------------------------------------------------------
    def _setup_figure(self) -> None:
        fig = self.ui.spectrumCanvas.figure
        fig.clear()
        self._ax = fig.add_subplot(111)
        fig.set_constrained_layout(True)
        self.ui.spectrumCanvas.draw_idle()

    # ------------------------------------------------------------------
    # 模式判断
    # ------------------------------------------------------------------
    def _get_current_mode(self) -> str:
        if self.ui.psdButton.isChecked():
            return "psd"
        if self.ui.rinButton.isChecked():
            return "rin"
        return "fft"  # 默认 fft

    # ------------------------------------------------------------------
    # 计算主流程
    # ------------------------------------------------------------------
    def _calculate(self) -> None:
        curves = self._curve_manager.compute_curves(
            space=self._space,
            normalize=False,   # RIN 必须使用未归一化数据
        )
        if not curves:
            QMessageBox.warning(self, "Spectrum", "No visible ROIs available.")
            return

        mode = self._get_current_mode()
        y_label, title = self._label_and_title(mode)

        results: list[dict] = []
        freq_units_seen: set[str] = set()

        for curve in curves:
            x = np.asarray(curve.x, dtype=np.float64)
            y = np.asarray(curve.y, dtype=np.float64)

            # 输入检查
            if len(x) < 4:
                QMessageBox.warning(
                    self,
                    "Spectrum",
                    f"ROI '{curve.label}' has too few points ({len(x)}) "
                    f"for spectral analysis. Skipping.",
                )
                continue
            if not np.all(np.isfinite(y)):
                QMessageBox.warning(
                    self,
                    "Spectrum",
                    f"ROI '{curve.label}' contains non-finite values. Skipping.",
                )
                continue

            # 获取该曲线所属 stack 的 PPS 实例
            stack_item = None
            if self._stack_manager is not None:
                stack_item = self._stack_manager.get_item_by_id(curve.stack_id)

            axis_unit = "ps"
            freq_unit = "1/ps"
            if stack_item is not None:
                pps = stack_item.pps
                axis_unit = pps.get_axis_unit()
                try:
                    # 时间轴：利用 PPS.get_phasor_unit 获得频率单位
                    freq_unit = pps.get_phasor_unit()
                except ValueError:
                    # 空间轴（z）等：直接使用倒数单位
                    freq_unit = f"1/{axis_unit}"

            freq_units_seen.add(freq_unit)

            try:
                if mode == "fft":
                    freqs, spectrum = compute_fft(y, x)
                elif mode == "psd":
                    freqs, spectrum = compute_psd(
                        y, x, normalize=False, db=True
                    )
                else:  # rin
                    freqs, spectrum = compute_psd(
                        y, x, normalize=True, db=True
                    )
            except ValueError as exc:
                QMessageBox.warning(
                    self,
                    "Spectrum",
                    f"Error for ROI '{curve.label}': {exc}",
                )
                continue

            results.append({
                "curve": curve,
                "freqs": freqs,
                "spectrum": spectrum,
                "axis_unit": axis_unit,
                "freq_unit": freq_unit,
            })

        if not results:
            return

        self._last_results = results
        self._last_mode = mode
        self._last_y_label = y_label

        # 如果所有曲线频率单位一致，使用它；否则警告并使用第一个
        if len(freq_units_seen) == 1:
            freq_unit = next(iter(freq_units_seen))
        else:
            freq_unit = results[0]["freq_unit"]
            QMessageBox.warning(
                self,
                "Spectrum",
                "Multiple axis units detected. Frequency labels may be misleading.",
            )
        self._last_freq_label = f"Frequency ({freq_unit})"

        self._update_plot(results, y_label, title, self._last_freq_label)
        self._update_text(results, mode, freq_unit)

    # ------------------------------------------------------------------
    # 绘图
    # ------------------------------------------------------------------
    def _update_plot(
        self,
        results: list[dict],
        y_label: str,
        title: str,
        freq_label: str,
    ) -> None:
        ax = self._ax
        ax.clear()

        for res in results:
            curve = res["curve"]
            ax.plot(
                res["freqs"],
                res["spectrum"],
                color=curve.color,
                label=curve.label,
            )

        ax.set_xlabel(freq_label)
        ax.set_ylabel(y_label)
        ax.set_title(title)
        ax.grid(True, alpha=0.3)

        if results:
            ax.legend(fontsize=8, loc="best")

        self.ui.spectrumCanvas.draw_idle()

    # ------------------------------------------------------------------
    # 结果文本
    # ------------------------------------------------------------------
    def _update_text(self, results: list[dict], mode: str, freq_unit: str) -> None:
        lines = []
        for res in results:
            curve = res["curve"]
            freqs = res["freqs"]
            spectrum = res["spectrum"]
            y = np.asarray(curve.y)

            mean_y = float(np.mean(y))
            std_y = float(np.std(y))

            if mode == "fft":
                # 排除直流分量，找正频率峰值
                pos = freqs > 0
                if np.any(pos):
                    idx = int(np.argmax(spectrum[pos]))
                    peak_freq = float(freqs[pos][idx])
                    peak_val = float(spectrum[pos][idx])
                else:
                    peak_freq, peak_val = 0.0, 0.0

                lines.append(
                    f"{curve.label}:\n"
                    f"  mean          = {mean_y:.4e}\n"
                    f"  std           = {std_y:.4e}\n"
                    f"  peak freq     = {peak_freq:.4e} {freq_unit}\n"
                    f"  peak amplitude = {peak_val:.4e} a.u."
                )

            elif mode == "psd":
                if len(spectrum) > 0:
                    idx = int(np.argmax(spectrum))
                    peak_freq = float(freqs[idx])
                    peak_val = float(spectrum[idx])
                else:
                    peak_freq, peak_val = 0.0, 0.0

                lines.append(
                    f"{curve.label}:\n"
                    f"  mean       = {mean_y:.4e}\n"
                    f"  std        = {std_y:.4e}\n"
                    f"  peak freq  = {peak_freq:.4e} {freq_unit}\n"
                    f"  peak PSD   = {peak_val:.2f} dB"
                )

            else:  # rin
                if len(spectrum) > 0:
                    idx = int(np.argmax(spectrum))
                    peak_freq = float(freqs[idx])
                    peak_val = float(spectrum[idx])
                else:
                    peak_freq, peak_val = 0.0, 0.0

                if abs(mean_y) > 1e-12:
                    rel_std = std_y / abs(mean_y)
                else:
                    rel_std = float("nan")

                lines.append(
                    f"{curve.label}:\n"
                    f"  mean       = {mean_y:.4e}\n"
                    f"  std        = {std_y:.4e}\n"
                    f"  rel_std    = {rel_std:.4e}\n"
                    f"  peak freq  = {peak_freq:.4e} {freq_unit}\n"
                    f"  peak RIN   = {peak_val:.2f} dBc/Hz"
                )

        self.ui.resultText.setPlainText("\n\n".join(lines))

    # ------------------------------------------------------------------
    # View: 独立 Matplotlib 窗口
    # ------------------------------------------------------------------
    def _view_standalone(self) -> None:
        if not self._last_results:
            QMessageBox.warning(self, "Spectrum", "Please calculate first.")
            return

        import matplotlib.pyplot as plt

        fig, ax = plt.subplots(figsize=(6, 4), layout="constrained")
        for res in self._last_results:
            curve = res["curve"]
            ax.plot(
                res["freqs"],
                res["spectrum"],
                color=curve.color,
                label=curve.label,
            )

        ax.set_xlabel(self._last_freq_label)
        ax.set_ylabel(self._last_y_label)
        ax.set_title(f"{self._last_mode.upper()} Spectrum")
        ax.grid(True, alpha=0.3)
        ax.legend(fontsize=8, loc="best")
        fig.show()

    # ------------------------------------------------------------------
    # Export: CSV
    # ------------------------------------------------------------------
    def _export_data(self) -> None:
        if not self._last_results:
            QMessageBox.warning(self, "Spectrum", "Please calculate first.")
            return

        default_name = f"{self._last_mode}_spectrum.csv"
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Export Spectrum Data",
            default_name,
            "CSV Files (*.csv);;All Files (*)",
        )
        if not path:
            return

        try:
            freqs = self._last_results[0]["freqs"]
            with open(path, "w", newline="") as f:
                writer = csv.writer(f)

                header = ["Frequency"]
                for res in self._last_results:
                    header.append(
                        f"{self._last_mode}_{res['curve'].label}"
                    )
                writer.writerow(header)

                for i, freq in enumerate(freqs):
                    row = [freq]
                    for res in self._last_results:
                        row.append(res["spectrum"][i])
                    writer.writerow(row)
        except (OSError, ValueError) as exc:
            QMessageBox.critical(
                self, "Spectrum", f"Export failed:\n{exc}"
            )

    # ------------------------------------------------------------------
    # 辅助
    # ------------------------------------------------------------------
    @staticmethod
    def _label_and_title(mode: str) -> tuple[str, str]:
        if mode == "fft":
            return "Amplitude (a.u.)", "FFT Amplitude Spectrum"
        if mode == "psd":
            return "PSD (dB)", "Power Spectral Density"
        return "RIN PSD (dBc/Hz)", "Relative Intensity Noise (RIN)"