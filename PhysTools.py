import numpy as np
import HistTools as HT


def FastEffectiveArea(coszens, log10enes, ngenevts, oneweight, coszenmin, coszenmax, elogbins) :

    cut = (coszens >= coszenmin) & (coszens < coszenmax) & (log10enes >= elogbins[0]) & (log10enes < elogbins[-1])
    solidangle =  2 * np.pi * (coszenmax - coszenmin)
    onew = oneweight[cut]

    high_bin = np.digitize(log10enes[cut], bins=elogbins) 
    low_bin = high_bin - 1
    ebinw = 10**elogbins[high_bin] - 10**elogbins[low_bin]

    weight = onew/ngenevts/solidangle/ebinw/1e4 # 10000: cm2 to m2

    effarea, bins, w2s = HT.make_1D_hist(log10enes[cut], xbins=elogbins, weights=weight)
    print(effarea)

    return effarea, bins, w2s


