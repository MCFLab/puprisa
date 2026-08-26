@echo off
echo Generating UI files...
pyside6-uic ui\forms\main_window.ui -o ui\generated\ui_main_window.py
pyside6-uic ui\forms\phasor_window.ui -o ui\generated\ui_phasor_window.py
pyside6-uic ui\forms\noise_window.ui -o ui\generated\ui_noise_window.py
pyside6-uic ui\forms\intensity_threshold_dialog.ui -o ui\generated\dialog_intensity_threshold.py
pyside6-uic ui\forms\colorbar_customrange_dialog.ui -o ui\generated\dialog_colorbar_customrange.py
pyside6-uic ui\forms\background_subtraction_dialog.ui -o ui\generated\dialog_background_subtraction.py
pyside6-uic ui\forms\stack_math.ui -o ui\generated\dialog_stack_math.py
pyside6-uic ui\forms\mask_math.ui -o ui\generated\dialog_mask_math.py
echo Done.
pause