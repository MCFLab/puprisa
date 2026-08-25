# -*- coding: utf-8 -*-
"""
Created on Wed Jun 25 11:25:37 2025

@author: dg208
"""
import numpy as np
from scipy.optimize import curve_fit
from scipy.special import erf

def decay_single(t, tau, t_pump, t_probe):
    """
    Compute transient absorption of single exponential decay.

    Parameters
    ----------
    t : float
        time variable [ps].
    tau : float
        Lifetime of the process [ps].
    t_pump : float
        Pulse width of pump pulse [ps].
    t_probe : float
        Pulse width of probe pulse [ps].

    Returns
    -------
    float
        Transient absorbtion value.

    """
    tp_squared = t_pump**2 + t_probe**2
    tp = np.sqrt(tp_squared)
    error_fu = erf(t / (np.sqrt(2) * tp) - tp / (np.sqrt(2) * tau))
    exp_fu = np.exp(-t / tau + tp_squared / (2 * tau**2))

    return 1 / 2 * exp_fu * (1 + error_fu)


def decay_infinite(t, t_pump, t_probe):
    """
    Compute transient absorption value of process with infinite lifetime.

    ----------
    t : float
        time variable [ps].
    t_pump : float
        Pulse width of pump pulse [ps].
    t_probe : float
        Pulse width of probe pulse [ps].

    Returns
    -------
    float
        Transient absorbtion value.

    """
    tp_squared = t_pump**2 + t_probe**2
    tp = np.sqrt(tp_squared)
    error_fu = erf(t / (np.sqrt(2) * tp))

    return 1 / 2 * (1 + error_fu)


def decay_instantaneous(t, t_pump, t_probe):
    """
    Compute transient absorption value of an instantaneous process.

    Parameters
    ----------
    t : float
        time variable [ps].
    t_pump : float
        Pulse width of pump pulse [ps].
    t_probe : float
        Pulse width of probe pulse [ps].

    Returns
    -------
    float
        Transient absorbtion value.

    """
    tp_squared = t_pump**2 + t_probe**2
    return (
        1 / np.sqrt(2 * np.pi * tp_squared) * np.exp(-(t**2) / 2 / tp_squared)
    )
