# -*- coding: utf-8 -*-
"""
Created on Mon Jun 16 13:52:56 2025

@author: dg208
"""
from scipy.special import erf
import numpy as np


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

def phasor(time_delays, ta_curve, freq):
    """
    Compute phasor coordinate pair for TA curve.

    Parameters
    ----------
    time_delays : list of numbers
        PP time delays.
    ta_curve : list of numbers
        TA values corresponding to time delays.
    freq : number
        Phasor frequency.

    Returns
    -------
    phasor_coor : tuple of numbers
        Phasor coordinates.

    """
    omega = freq * 2 * np.pi
    sin = np.sin(time_delays * omega)
    cos = np.cos(time_delays * omega)
    
    norm = np.sum(np.abs(ta_curve))
    phasor_coor = np.array(
        [
            np.dot(cos, ta_curve) / norm,
            np.dot(sin, ta_curve) / norm,
        ]
    )
    
    return phasor_coor