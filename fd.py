from collections import defaultdict
from random import choices
from FDUtils import *


TB = 1000000000

class FD():
    def __init__(self, sd_limit=10*TB, iat_limit=4000000):

        self.sd_limit  = sd_limit
        self.iat_limit = iat_limit

        self.fd_util = FDUtils()
        
        self.no_reqs       = 0
        self.total_bytes   = 0
        self.start_tm      = 0
        self.end_tm        = 0
        self.requests_miss  = 0
        self.bytes_miss     = 0
        self.st            = defaultdict(lambda : defaultdict(float))
        
    def read_from_file(self, f, iat_gran, sd_gran):
        
        l = f.readline()
        l = l.strip().split(" ")

        self.no_reqs      = int(l[0])
        self.total_bytes  = float(l[1])
        self.start_tm     = int(l[2])
        self.end_tm       = int(l[3])
        self.requests_miss = int(l[4])
        self.bytes_miss    = float(l[5])
        self.req_rate     = self.no_reqs/(self.end_tm - self.start_tm)
        self.byte_rate    = self.total_bytes/(self.end_tm - self.start_tm)
        
        for l in f:
            l   = l.strip().split(" ")
            iat = (float(l[0]) // iat_gran) * iat_gran
            sd  = (float(l[1]) // sd_gran) * sd_gran
            pr  = float(l[2])
            self.st[iat][sd] += pr

        self.iat_gran = iat_gran
        self.sd_gran  = sd_gran 
            
    ## convolve oneself with fd2 and store result in fd_res
    def addition(self, fd2, fd_res, hitrate_type):

        print("Computing the traffic model for the traffic mix")
        
        if hitrate_type == "rhr":
            rate1 = self.req_rate
            rate2 = fd2.req_rate
        else:
            rate1 = self.byte_rate
            rate2 = fd2.byte_rate
            
        self.fd_util.convolve_2d_fft(self.st, fd2.st, fd_res.st, rate1, rate2, self.sd_gran)
        fd_res.no_reqs       = self.no_reqs + fd2.no_reqs
        fd_res.total_bytes   = self.total_bytes + fd2.total_bytes
        fd_res.start_tm      = min(self.start_tm, fd2.start_tm)
        fd_res.end_tm        = max(self.end_tm, fd2.end_tm)
        fd_res.requests_miss = self.requests_miss + fd2.requests_miss
        fd_res.bytes_miss    = self.bytes_miss + fd2.bytes_miss
        fd_res.req_rate      = self.req_rate + fd2.req_rate
        fd_res.byte_rate     = self.byte_rate + fd2.byte_rate
        fd_res.shave_off_tail()
            
    def shave_off_tail(self):
        pr = 0
        tail = []
        for t in self.st:
            for s in self.st[t]:
                if s > self.sd_limit or t > self.iat_limit:
                    pr += self.st[t][s]
                    tail.append((t,s))
        for (t,s) in tail:
            del self.st[t][s]
            
        self.requests_miss += pr*self.no_reqs
        self.bytes_miss    += pr*self.total_bytes
                    
    
    def scale(self, scale_factor, iat_gran):
        
        self.no_reqs       *= scale_factor
        self.total_bytes   *= scale_factor
        self.requests_miss *= scale_factor
        self.bytes_miss    *= scale_factor
        self.req_rate      *= scale_factor
        self.byte_rate     *= scale_factor

        st_sub = defaultdict(lambda : defaultdict(float))
        
        for iat in self.st.keys():
            t = float(iat)/scale_factor
            t = (float(t) // iat_gran) * iat_gran
            for sd in self.st[iat].keys():
                st_sub[t][sd] += self.st[iat][sd]
        self.st = st_sub

    
    def setupSampling(self, hr_type, min_val, max_val):
        self.sd_keys = []
        self.sd_vals = []

        SD = defaultdict(lambda :0)
        if hr_type == "bhr":
            SD[-1] = float(self.bytes_miss)/self.total_bytes
        else:
            SD[-1] = float(self.requests_miss)/self.no_reqs

        for t in self.st:
            for s in self.st[t]:
                SD[s] += self.st[t][s]

        self.sd_keys = list(SD.keys())
        self.sd_keys.sort()

        for sd in self.sd_keys:
            self.sd_vals.append(SD[sd])

        print("Finished reading the input models")

            
    def sample(self, n):
        return choices(self.sd_keys, weights=self.sd_vals, k=n)

    
