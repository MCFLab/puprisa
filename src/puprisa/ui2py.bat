@echo off
echo Generating UI files...
pyside6-uic ui\forms\main_window.ui -o ui\generated\ui_main_window.py
pyside6-uic ui\forms\phasor_window.ui -o ui\generated\ui_phasor_window.py
pyside6-uic ui\forms\intensity_threshold_dialog.ui -o ui\generated\dialog_intensity_threshold.py
pyside6-uic ui\forms\colorbar_customrange_dialog.ui -o ui\generated\dialog_colorbar_customrange.py
pyside6-uic ui\forms\background_subtraction_dialog.ui -o ui\generated\dialog_background_subtraction.py
echo Done.
pause