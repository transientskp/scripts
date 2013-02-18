#!/usr/bin/env python
import math

def gaussian_convolve(maj1, min1, pa1, maj2, min2, pa2):
    """
    Gaussian convolution.

    Position angles must be in radians; axis lengths can be in any units,
    obviously provided that they are consistent.

    Based on Miriad's Gaufac in miriad/subs/gaupar.for.
    """
    cospa1 = cos(pa1)
    cospa2 = cos(pa2)
    sinpa1 = sin(pa1)
    sinpa2 = sin(pa2)

    alpha = (maj1 * cospa1)**2 + (min1 * sinpa1)**2 + \
            (maj2 * cospa2)**2 + (min2 * sinpa2)**2
    beta =  (maj1 * sinpa1)**2 + (min1 * cospa1)**2 + \
            (maj2 * sinpa2)**2 + (min2 * cospa2)**2
    gamma = 2 * ((min1**2 - maj1**2) * sinpa1 * cospa1 +
                 (min2**2 - maj2**2) * sinpa2 * cospa2)

    s = alpha + beta
    t = math.sqrt((alpha-beta)**2 + gamma**2)
    major = math.sqrt(0.5 * (s + t))
    minor = math.sqrt(0.5 * (s - t))
    if abs(gamma) + abs(alpha - beta) == 0:
        posangle = 0.0
    else:
        posangle = 0.5 * math.atan2(-gamma, alpha - beta)

    return major, minor, posangle


def gaussian_deconvolve(maj1, min1, pa1, maj2, min2, pa2):
    """
    Gaussian deconvolution. We deconvolve maj2/min2/pa2 from maj1/min1/pa1.

    Position angles must be in radians; axis lengths can be in any units,
    obviously provided that they are consistent.

    Raises Exception on failure, or on a point-like source.

    Based on Miriad's GauDfac in miriad/subs/gaupar.for.
    """
    cospa1 = cos(pa1)
    cospa2 = cos(pa2)
    sinpa1 = sin(pa1)
    sinpa2 = sin(pa2)

    alpha = (maj1 * cospa1)**2 + (min1 * sinpa1)**2 - \
            (maj2 * cospa2)**2 - (min2 * sinpa2)**2
    beta =  (maj1 * sinpa1)**2 + (min1 * cospa1)**2 - \
            (maj2 * sinpa2)**2 - (min2 * cospa2)**2
    gamma = 2 * ((min1**2 - maj1**2) * sinpa1 * cospa1 -
                 (min2**2 - maj2**2) * sinpa2 * cospa2)

    s = alpha + beta
    t = math.sqrt((alpha - beta)**2 + gamma**2)
    limit = 0.1 * min(maj1, min1, maj2, min2)**2
    if alpha < 0 or beta < 0 or s < t:
        if 0.5 * (s - t) < limit and alpha > -limit and beta > -limit:
            raise Exception("Result is point-like")
        else:
            raise Exception("Illegal result")
    else:
        major = math.sqrt(0.5 * (s + t))
        minor = math.sqrt(0.5 * (s - t))
        if abs(gamma) + abs(alpha-beta) == 0:
            posangle = 0.0
        else:
            posangle = 0.5 * math.atan2(-gamma, alpha - beta)

    return major, minor, posangle
