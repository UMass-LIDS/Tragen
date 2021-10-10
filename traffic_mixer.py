import random, sys, math, copy
import numpy as np
import scipy as sp
import scipy.signal
import cmath
import numpy.fft as fft
from collections import defaultdict
from scipy.optimize import linprog, brentq
from fd import *


## A class that describes the methods to find the traffic model for the traffic mix
class TrafficMixer():
    def __init__(self, args):
        self.availableTcs   = self.available_traffic_classes()        
        self.trafficRatios  = [float(x) for x in args.traffic_ratio.split(":")]
        self.trafficClasses = [str(x) for x in args.traffic_classes.split(":")]

        self.args     = args

        ## The footprint descriptors are computed at the granularity of 200s for IAT
        ## and 200MB for Stack distance.
        self.iat_gran = 200
        self.sd_gran  = 200000

        ## Recompute the traffic ratios based on the available traffic rate
        trafficRatios  = []
        trafficClasses = []
        i = 0
        for t in self.trafficClasses:

            if t in self.availableTcs:
                trafficClasses.append(t)
                if args.hitrate_type == "rhr":
                    trafficRatios.append(self.trafficRatios[i]/self.availableTcs[t][0])
                elif args.hitrate_type == "bhr":
                    trafficRatios.append(self.trafficRatios[i]/self.availableTcs[t][1])
            i += 1
            
        self.trafficRatios  = trafficRatios
        self.trafficClasses = trafficClasses
        
        self.object_weight_vector()        
        self.readFDs()
        self.scale()
        self.mix()


    ## Read footprint descriptors from file
    def readFDs(self):
        self.FDs = []

        for i in range(len(self.trafficClasses)):
            fd = FD()

            if self.args.hitrate_type == "rhr":
                f  = open("FOOTPRINT_DESCRIPTORS/" + self.trafficClasses[i] + "/footprint_desc_all.txt", "r")
            else:
                f  = open("FOOTPRINT_DESCRIPTORS/" + self.trafficClasses[i] + "/byte_footprint_desc_all.txt", "r")

            fd.read_from_file(f, self.iat_gran, self.sd_gran)
            self.FDs.append(fd)
            

    ## Scale the footprint descriptor based on the traffic volume specified by the user
    def scale(self):
        for i in range(len(self.trafficClasses)):
            self.FDs[i].scale(self.trafficRatios[i], self.iat_gran)

    ## Compute the traffic models for the traffic mix
    def mix(self):
        if len(self.trafficClasses) == 1:
            self.FD_mix = self.FDs[0]
            return
        
        for i in range(len(self.trafficClasses) - 1):
            if i == 0:
                fd_prev_iter = FD()
                self.FDs[i].addition(self.FDs[i+1], fd_prev_iter, self.args.hitrate_type)
            else:
                fd_new = FD()
                fd_prev_iter.addition(self.FDs[i+1], fd_new, self.args.hitrate_type)
                fd_prev_iter = fd_new

        self.FD_mix = fd_prev_iter

    ## Output a vector that finds the ratio of the number of objects per traffic class
    ## that is to be present in the synthetic trace
    def object_weight_vector(self):
        self.weight_vector = []

        def find_uniqrate(f):
            urate = 0
            l = f.readline()
            for l in f:
                l = l.strip().split(" ")
                iat = int(l[0])
                sd  = int(l[1])
                rt = float(sd)/(iat + 100)
                pr = float(l[2])
                urate += pr * rt
            return urate

        for i in range(len(self.trafficClasses)):
            f = open("FOOTPRINT_DESCRIPTORS/" + self.trafficClasses[i] + "/footprint_desc_all.txt", "r")            
            U = find_uniqrate(f)
            f.close()

            f = open("FOOTPRINT_DESCRIPTORS/" + self.trafficClasses[i] + "/iat_sz_all.txt", "r")
            avg_obj_sz = 0
            for l in f:
                l = l.strip().split(" ")
                if len(l) >= 2:
                    sz = float(l[0])
                    pr = float(l[1])
                    avg_obj_sz += (sz*pr)

            self.weight_vector.append(float(U)/avg_obj_sz)

        normalizing_factor = sum(self.weight_vector)
        self.weight_vector = [float(x)/normalizing_factor for x in self.weight_vector]


    ## Print the available traffic classes
    def available_traffic_classes(self):
        availableTcs = defaultdict()
        f = open("FOOTPRINT_DESCRIPTORS/available_fds.txt", "r")
        for l in f:
            l = l.strip().strip().split(",")
            tc = l[1]
            volume = float(l[3])
            req_rate = float(l[4])
            availableTcs[tc] = ((req_rate, volume))
        return availableTcs
