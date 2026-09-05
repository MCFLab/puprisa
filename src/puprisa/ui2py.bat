@echo off
echo Generating UI files...

pyside6-uic ui\forms\main_window.ui -o ui\generated\ui_main_window.py
pyside6-uic ui\forms\phasor_window.ui -o ui\generated\ui_phasor_window.py

pyside6-uic ui\forms\stack_math_dialog.ui -o ui\generated\dialog_stack_math.py
pyside6-uic ui\forms\colorbar_customrange_dialog.ui -o ui\generated\dialog_colorbar_customrange.py
pyside6-uic ui\forms\phasor_alpha_dialog.ui -o ui\generated\dialog_phasor_alpha.py

pyside6-uic ui\forms\bgsub_first_last_dialog.ui -o ui\generated\dialog_bgsub_first_last.py
pyside6-uic ui\forms\bgsub_fixed_value_dialog.ui -o ui\generated\dialog_bgsub_fixed_value.py
pyside6-uic ui\forms\bgsub_neg_delay_dialog.ui -o ui\generated\dialog_bgsub_neg_delay.py

pyside6-uic ui\forms\mask_from_intensity_threshold_dialog.ui -o ui\generated\dialog_mask_from_intensity_threshold.py
pyside6-uic ui\forms\mask_from_zero_pixels_dialog.ui -o ui\generated\dialog_mask_from_zero_pixels.py
pyside6-uic ui\forms\mask_math_dialog.ui -o ui\generated\dialog_mask_math.py

pyside6-uic ui\forms\edit_roi_dialog.ui -o ui\generated\dialog_edit_roi.py
pyside6-uic ui\forms\curve_fit_dialog.ui -o ui\generated\dialog_curve_fit.py
pyside6-uic ui\forms\spectrum_dialog.ui -o ui\generated\dialog_spectrum.py

echo Done.
pause