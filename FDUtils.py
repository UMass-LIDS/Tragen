import random, sys, math, copy
import numpy as np
import scipy as sp
import scipy.signal
import cmath
import numpy.fft as fft
from collections import defaultdict
from scipy.optimize import linprog, brentq
from fd import *


class FDUtils():
    def __init__(self):
        pass

    def cond_prob(self, st):
        for t in st.keys():            
            sum_st = sum([v for v in st[t].values()])            
            for s in st[t].keys():
                st[t][s] = st[t][s]/sum_st if sum_st else 0


    # Floor for st and ss
    def floor(self, t_set, t):
        # Error 
        if len(t_set) < 1:
            return -1
    
        # Only one element in t_set 
        if len(t_set) == 1:
            return t_set[0]

        # Match found
        if t in t_set:
            return t

        # t < min
        if t < t_set[0]:
            return t_set[0]
        # t > max
        if t > t_set[len(t_set) - 1]:
            return t_set[len(t_set) - 1]

        # Floor
        start = 0
        end = len(t_set) - 1
        while start < end:
            middle = (start + end) // 2
            if t_set[middle] > t:
                end = middle
            else:
                start = middle
                if (end - start + 1 == 2):
                    return t_set[start]

    ## perform the convolution operator on the given two footprint descriptors
    def convolve_2d_fft(self, st1, st2, st12, rate1, rate2, sd_gran):
        
        # Determine conditional probabilties of st1 and st2
        st1_cond = copy.deepcopy(st1)
        self.cond_prob(st1_cond)
        st2_cond = copy.deepcopy(st2)
        self.cond_prob(st2_cond)

        t1_set = sorted(set(list(st1.keys())))
        t2_set = sorted(set(list(st2.keys())))
        t12_set = sorted(set(t1_set + t2_set))

        for t in t12_set:
        
            prob_t1 = sum([v for v in st1[t].values()]) if t in st1 else 0
            prob_t2 = sum([v for v in st2[t].values()]) if t in st2 else 0
     
            prob_t12 = (((rate1 / (rate1 + rate2)) * prob_t1) + ((rate2 / (rate1 + rate2)) * prob_t2), 0)

            st1_c = st1_cond[self.floor(sorted(set(st1_cond.keys())), t)]
            st2_c = st2_cond[self.floor(sorted(set(st2_cond.keys())), t)]

            # Convolution using fft
            min_st1_s = int(min(st1_c.keys()))
            max_st1_s = int(max(st1_c.keys()))
            min_st2_s = int(min(st2_c.keys()))
            max_st2_s = int(max(st2_c.keys()))
            
            out_k = set([])
            out_k2 = set([])
            out_k = sorted([i for i in range(min_st1_s + min_st2_s, max_st1_s + max_st2_s + 1, sd_gran)])

            st1_tmp = [st1_c[k] if k in st1_c else 0 for k in range(min_st1_s, max_st1_s + 1, sd_gran)]
            st2_tmp = [st2_c[k] if k in st2_c else 0 for k in range(min_st2_s, max_st2_s + 1, sd_gran)]
        
            st1_fft = fft.fft(st1_tmp, len(st1_tmp) + len(st2_tmp) - 1)
            st2_fft = fft.fft(st2_tmp, len(st1_tmp) + len(st2_tmp) - 1)

            st12_fft = [0 for i in range(len(st1_tmp) + len(st2_tmp) - 1)]

            for i in range(len(st12_fft)):
                st12_fft[i] = st1_fft[i] * st2_fft[i]

            st12_conv = fft.ifft(st12_fft)

            print("convolving for time : ", t," and len : ", len(st12_conv))
        
            for i in range(len(st12_conv)):            
                st12[t][out_k[i]] = float(st12_conv[i]) * prob_t12[0]



