# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:25:37 2025

@author: dg208
"""
import numpy as np
import pandas as pd
import re
from matplotlib import pyplot as plt
from scipy.optimize import curve_fit
from pump_probe_analysis import ta


def fit_xcorr(filename, delay_stage_passes=4, dt_default=0.077):
    """
    Fit pulse width of cross-correlation measurement.

    Parameters
    ----------
    filename : str
        Full path of xcorr measurement.
    delay_stage_passes : int, optional
        Multiplier for path length difference intruduced by delay stage. The
        default is 4.
    dt_default : float, optional
        If fit does not converge, this value is returned. The defaut is 0.077

    Returns
    -------
    TYPE
        DESCRIPTION.

    """
    # what are the units of this zscan: mm or ps?
    with open(filename, "r") as f:
        data = f.read()
    match = re.search(r"xUnits = (mm|ps)", data)
    if match:
        units = match.group(1)
    else:
        units = "mm"
        print(f"don't know units of xcorr file {filename}, assumed mm")

    # import data from filename and drop first data point, which is typically
    # bad from lock-in settle time
    df = pd.read_csv(filename, sep="\t", comment="#")
    if units == "mm":
        # assuming 4-pass delay stage
        time = df["pos"].iloc[1:] * 10 / 3 * delay_stage_passes
        xcorr = df["xsig"].iloc[1:]
    if units == "ps":
        time = df["pos"].iloc[1:]
        xcorr = df["xsig"].iloc[1:]

    # correct for offset
    xcorr = xcorr - np.mean(xcorr[:5])
    xcorr = xcorr / np.max(xcorr)
    time = time - time.iloc[0]

    # initial guess for fitting
    guess_t0 = time[np.argmax(xcorr)]

    # fitting
    try:

        def fit_function(t, t0, a0, dt, a1):
            return a0 * ta.decay_instantaneous(
                t - t0, dt, dt
            ) + a1 * ta.decay_infinite(t - t0, dt, dt)

        popt, pcov = curve_fit(
            fit_function, time, xcorr, p0=[guess_t0, 1, 0.5, 0]
        )
    except (RuntimeError, TypeError, ValueError) as e:
        print(f"Fit {filename} failed: {e}")

        figure, ax = plt.subplots(1, 1, figsize=(4, 3))
        ax.scatter(time, xcorr)
        ax.plot(time, fit_function(time, *popt))
        popt = [0, 0, dt_default, 0]

    return np.abs(popt[2])
