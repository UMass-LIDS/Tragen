from collections import defaultdict
from random import choices
from util import *
import numpy as np
import copy

    
class SZ_dst:
    def __init__(self, i_file, min_val, max_val):
        f = open(i_file, "r")
        self.all_keys = defaultdict(int)
        l = f.readline()
        sum_count = 0

        total_pr = 0
        for l in f:
            l = l.strip().split(" ")

            if len(l) == 1:
                continue
            else:
                key = int(float(l[0]))
                val = float(l[1])
                if key >= min_val and key <= max_val:
                    self.all_keys[key] += val                                
                    total_pr += val
                    
        p_keys = list(self.all_keys.keys())
        vals = []
        for k in p_keys:
            vals.append(self.all_keys[k])
        sum_vals = sum(vals)
        vals = [float(x)/sum_vals for x in vals]        
        self.p_keys = p_keys
        self.pr = vals

                
    def sample_keys(self, n):
        return choices(self.p_keys, weights=self.pr,k=n)

                    

class SampleFootPrint:
    def __init__(self, fd, hr_type, min_val, max_val):
        self.sd_keys = []
        self.sd_vals = []
        self.sd_index = defaultdict(lambda : 0)
        self.SD = defaultdict(lambda : 0)        

        f = open(i_file, "r")
        l = f.readline()
        l = l.strip().split(" ")
        if hr_type == "bhr":
            bytes_miss = float(l[-1])
            bytes_req = float(l[1])
            self.SD[-1] = float(bytes_miss)/bytes_req
        else:
            reqs_miss = float(l[-2])
            reqs = float(l[0])
            self.SD[-1] = float(reqs_miss)/reqs                    
            self.sd_index[-1] = 0

        total_pr = 0
        for l in f:
            l = l.strip().split(" ")
            sd = int(l[1])
            self.SD[sd] += float(l[2])        
            total_pr += float(l[2])
            
        self.sd_keys = list(self.SD.keys())
        self.sd_keys.sort()

        i = 1
        for sd in self.sd_keys:
            self.sd_vals.append(self.SD[sd])
            self.sd_index[sd] = i
            i += 1            
                            
    def sample_keys(self, obj_sizes, sampled_sds, n):
        return choices(self.sd_keys, weights = self.sd_vals, k = n)
    
