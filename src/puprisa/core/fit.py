# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:25:37 2025

@author: dg208
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf
from dataclasses import dataclass

def decay_single(t, tau, tp):
    """
    Compute transient absorption of single exponential decay.

    Parameters
    ----------
    t : float
        time variable [ps].
    tau : float
        Lifetime of the process [ps].
    tp : float
        Pulse width of the process [ps].
        tp = np.sqrt(t_pump**2 + t_probe**2).

    Returns
    -------
    float
        Transient absorbtion value.

    """
    error_func = erf(t / (np.sqrt(2) * tp) - tp / (np.sqrt(2) * tau))
    exp_func = np.exp(-t / tau + tp**2 / (2 * tau**2))

    return 1 / 2 * exp_func * (1 + error_func)

def decay_infinite(t, tp):
    """
    Compute transient absorption value of process with infinite lifetime.

    ----------
    t : float
        time variable [ps].
    tp : float
        Pulse width of the process [ps].

    Returns
    -------
    float
        Transient absorbtion value.

    """
    error_func = erf(t / (np.sqrt(2) * tp))
    return 1 / 2 * (1 + error_func)

def decay_instantaneous(t, tp):
    """
    Compute transient absorption value of an instantaneous process.

    Parameters
    ----------
    t : float
        time variable [ps].
    tp : float
        Pulse width of the process [ps].

    Returns
    -------
    float
        Transient absorbtion value.

    """
    return 1 / np.sqrt(2 * np.pi * tp**2) * np.exp(-(t**2) / 2 / tp**2)

@dataclass
class FitOptions:
    """Contains all user-specified fitting parameters."""
    include_instantaneous: bool = True
    include_exp_decay_1: bool = True
    include_exp_decay_2: bool = False
    include_exp_decay_3: bool = False
    include_exp_decay_inf: bool = False
    pulse_width_option: str = "specify"  # "specify" or "fit"
    pulse_width_fs: float = 100.0        # used when pulse_width_option == "specify"
    t0_option: str = "specify"           # "specify" or "fit"
    time_shift: float = 0.0              # ps, used when t0_option == "specify"
    # Instantaneous component
    A0_init: float = 1.0
    A0_lower: float = -np.inf
    A0_upper: float = np.inf
    # Exponential decay 1
    A1_init: float = 1.0
    A1_lower: float = -np.inf
    A1_upper: float = np.inf
    tau1_init: float = 1.0
    tau1_lower: float = 0.0
    tau1_upper: float = np.inf
    # Exponential decay 2
    A2_init: float = 1.0
    A2_lower: float = -np.inf
    A2_upper: float = np.inf
    tau2_init: float = 10.0
    tau2_lower: float = 0.0
    tau2_upper: float = np.inf
    # Exponential decay 3
    A3_init: float = 1.0
    A3_lower: float = -np.inf
    A3_upper: float = np.inf
    tau3_init: float = 0.1
    tau3_lower: float = 0.0
    tau3_upper: float = np.inf
    # Infinite lifetime component
    A4_init: float = 1.0
    A4_lower: float = -np.inf
    A4_upper: float = np.inf
    # If pulse_width_option == "fit", these are used
    tp_init: float = 0.1            # ps
    tp_lower: float = 1e-4
    tp_upper: float = 100.0
    # If t0_option == "fit", these are used
    t0_init: float = 0.0            # ps, initial guess if fitting
    t0_lower: float = -1.0          # ps, lower bound
    t0_upper: float = 1.0           # ps, upper bound

@dataclass
class FitResult:
    """Result of a curve fitting operation."""
    success: bool
    x: np.ndarray               # original x data
    y: np.ndarray               # original y data
    x_fit: np.ndarray           # dense x for plotting fitted curve
    y_fit: np.ndarray           # fitted curve
    popt: dict                  # parameter name -> fitted value
    perr: dict                  # parameter name -> standard error
    message: str = ""


def fit_curve(x: np.ndarray, y: np.ndarray, options: FitOptions) -> FitResult:
    """
    Perform the fitting according to the given options.
    Parameters
    ----------
    x, y : np.ndarray
        Data points to fit.
    options : FitOptions
        User-defined fitting configuration.
    Returns
    -------
    FitResult
    """
    fitfunc = {
        "inst": options.include_instantaneous,
        "exp1": options.include_exp_decay_1,
        "exp2": options.include_exp_decay_2,
        "exp3": options.include_exp_decay_3,
        "inf": options.include_exp_decay_inf,
    }
    if not any(fitfunc.values()):
        return FitResult(False, x, y, np.array([]), np.array([]), {}, {}, "No fitting components selected")

    # Initial parameters and bounds
    param_names = []
    p0 = []
    lower = []
    upper = []
    def add_param(name, init, lo, hi):
        param_names.append(name)
        p0.append(init)
        lower.append(lo)
        upper.append(hi)

    if options.pulse_width_option == "specify":
        pulse_width = options.pulse_width_fs / 1000.0
    else:  # "fit"
        add_param("tp", options.tp_init, options.tp_lower, options.tp_upper)
        pulse_width = None
    if options.t0_option == "specify":
        t0_fixed = options.time_shift
    else:  # "fit"
        add_param("t0", options.t0_init, options.t0_lower, options.t0_upper)
        t0_fixed = None

    if fitfunc["inst"]:
        add_param("A0", options.A0_init, options.A0_lower, options.A0_upper)
    if fitfunc["exp1"]:
        add_param("A1", options.A1_init, options.A1_lower, options.A1_upper)
        add_param("tau1", options.tau1_init, options.tau1_lower, options.tau1_upper)
    if fitfunc["exp2"]:
        add_param("A2", options.A2_init, options.A2_lower, options.A2_upper)
        add_param("tau2", options.tau2_init, options.tau2_lower, options.tau2_upper)
    if fitfunc["exp3"]:
        add_param("A3", options.A3_init, options.A3_lower, options.A3_upper)
        add_param("tau3", options.tau3_init, options.tau3_lower, options.tau3_upper)
    if fitfunc["inf"]:
        add_param("A4", options.A4_init, options.A4_lower, options.A4_upper)

    def model_func(t, *params):
        idx = 0
        if options.pulse_width_option == "fit":
            tp = params[idx]; idx += 1
        else:
            tp = pulse_width
        if options.t0_option == "fit":
            t0 = params[idx]; idx += 1
        else:
            t0 = t0_fixed
        t_shifted = t - t0
        total = np.zeros_like(t, dtype=float)
        if fitfunc["inst"]:
            A0 = params[idx]; idx += 1
            total += A0 * decay_instantaneous(t_shifted, tp)
        if fitfunc["exp1"]:
            A1 = params[idx]; idx += 1
            tau1 = params[idx]; idx += 1
            total += A1 * decay_single(t_shifted, tau1, tp)
        if fitfunc["exp2"]:
            A2 = params[idx]; idx += 1
            tau2 = params[idx]; idx += 1
            total += A2 * decay_single(t_shifted, tau2, tp)
        if fitfunc["exp3"]:
            A3 = params[idx]; idx += 1
            tau3 = params[idx]; idx += 1
            total += A3 * decay_single(t_shifted, tau3, tp)
        if fitfunc["inf"]:
            A4 = params[idx]; idx += 1
            total += A4 * decay_infinite(t_shifted, tp)
        return total
    bounds = (np.array(lower, dtype=float), np.array(upper, dtype=float))
    try:
        popt, pcov = curve_fit(model_func, x, y, p0=p0, bounds=bounds)
        perr = np.sqrt(np.diag(pcov))
        x_fit = np.linspace(np.min(x), np.max(x), 500)
        y_fit = model_func(x_fit, *popt)
        popt_dict = {name: val for name, val in zip(param_names, popt)}
        perr_dict = {name: err for name, err in zip(param_names, perr)}
        return FitResult(True, x, y, x_fit, y_fit, popt_dict, perr_dict)
    except Exception as exc:
        return FitResult(False, x, y, np.array([]), np.array([]), {}, {}, str(exc))