import numpy as np
import re
import sys

import snitch.util.sim.data_utils as du

def getABC(up_M,up_N,up_K):
        a_list = [2]*(up_M*up_K)#[x+2 for x in range(5,M*K+5)]#[2]*(M*K)
        b_list = [3]*(up_K*up_N)#[x+2 for x in range(1,K*N+1)]
        c_list = [-1]*(up_M*up_N)
        a = np.reshape(a_list, (up_M,up_K))
        b = np.reshape(b_list, (up_K,up_N))
        c = np.reshape(c_list, (up_M,up_N))
        return a,b,c
    