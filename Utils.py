"""
Simple utility functions 

"""

import os
import shutil
import numpy as np

def mkdir(dirname, recreate=False) :
    if recreate and os.path.exists(dirname) : 
        shutil.rmtree(dirname)
    if not os.path.exists(dirname) :
        os.makedirs(dirname)


def np_loadtxt(filename, suffix=".dat") :
    npyname = filename.replace(suffix, ".npy")
    if os.path.exists(npyname) :
        return np.load(npyname)
    else :
        loaded = np.loadtxt(filename)
        np.save(npyname, loaded)
        return loaded
        


