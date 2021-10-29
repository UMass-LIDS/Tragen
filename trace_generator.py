from joint_dst import *
from constants import *
from collections import defaultdict
import datetime
import os
import time
import sys


## A class that defines the functions and objects required to generate a synthetic trace
class TraceGenerator():
    def __init__(self, trafficMixer, args, printBox=None):
        self.trafficMixer = trafficMixer
        self.args = args
        self.log_file = open("OUTPUT/logfile.txt" , "w")
        self.read_obj_size_dst()
        self.read_popularity_dst()
        self.curr_iter = 0
        self.printBox = printBox
        

    ## Generate a synthetic trace
    def generate(self):
        fd = self.trafficMixer.FD_mix

        ## object weight vector
        OWV = self.trafficMixer.weight_vector
        
        trafficClasses = self.trafficMixer.trafficClasses        
        
        fd.setupSampling(self.args.hitrate_type, 0, TB)

        MAX_SD = fd.sd_keys[-1]

        ## sample 70 million objects
        print("Sampling the object sizes that will be assigned to the initial objects in the LRU stack ...")

        if self.printBox != None:
            self.printBox.setText("Sampling initial objects ...")
        
        n_sizes        = []
        sizes          = []
        n_popularities = []
        popularities   = []
        i = -1
        for i in range(len(OWV)-1):
            SZ = self.sz_dsts[trafficClasses[i]]
            n_sizes.extend(SZ.sample_keys(int(70*MIL * OWV[i])))

            P = self.popularity_dsts[trafficClasses[i]]
            n_popularities.extend(P.sample_keys(int(70*MIL * OWV[i])))
            
        SZ = self.sz_dsts[trafficClasses[i+1]]
        n_sizes.extend(SZ.sample_keys(int(70*MIL) - len(n_sizes)))
        P = self.popularity_dsts[trafficClasses[i+1]]
        n_popularities.extend(P.sample_keys(int(70*MIL) - len(n_popularities)))
        
        random.shuffle(n_sizes)
        random.shuffle(n_popularities)        
        sizes.extend(n_sizes)        
        popularities.extend(n_popularities)
        
        ## Now fill the objects such that the stack is 10TB
        total_sz = 0
        total_objects = 0
        i = 0
        while total_sz < MAX_SD:
            total_sz += sizes[total_objects]
            total_objects += 1
            if total_objects % 100000 == 0:
                print("Initializing the LRU stack ... ", int(100 * float(total_sz)/MAX_SD), "% complete")

                if self.printBox != None:
                    self.printBox.setText("Initializing the LRU stack ... " + str(int(100 * float(total_sz)/MAX_SD)) + "% complete")
                

        ## debug file
        debug = open("OUTPUT/debug.txt", "w")

        ## build the LRU stack
        trace = range(total_objects)

        ## Represent the objects in LRU stack as leaves of a B+Tree
        trace_list, ss = gen_leaves(trace, sizes, self.printBox)
                            
        ## Construct the tree
        st_tree, lvl = generate_tree(trace_list, self.printBox)
        root = st_tree[lvl][0]
        root.is_root = True
        curr = st_tree[0][0]

        ## Initialize
        c_trace   = []
        tries     = 0
        i         = 0
        j         = 0
        k         = 0
        no_desc   = 0
        fail      = 0
        curr_max_seen = 0

        stack_samples = fd.sample(1000)

        sz_added   = 0
        sz_removed = 0
        evicted_   = 0

        reqs_seen   = [0] * 70 * MIL
        sizes_seen  = []
        sds_seen    = []
        sampled_fds = []

        if self.printBox != None:
            self.printBox.setText("Generating synthetic trace ...")
        
        while curr != None and i <= int(self.args.length):

            ## Generate 1000 samples -- makes the computation faster
            if k >= 1000:
                stack_samples = fd.sample(1000)
                k = 0

            sd = stack_samples[k]
            k += 1


            ## Rework this part -- can be made much more efficient

            req_objects = []
            no_objects  = 0
            present     = curr
            found_atleast_one = False
            while no_objects < 50 or found_atleast_one == False:
                if popularities[present.obj_id] - reqs_seen[present.obj_id] > 1:
                    found_atleast_one = True                     
                req_objects.append((popularities[present.obj_id] - reqs_seen[present.obj_id], present))
                no_objects += 1
                present = present.findNext()[0]

            if sd < 0:
                pctile = 0
            else:
                pctile = len(req_objects) - int(fd.findPr(sd) * len(req_objects)) - 1
                if pctile < 0:
                    pctile = 0
                
            req_objects = sorted(req_objects, key= lambda x:x[0])
            req_obj = req_objects[pctile][1]
            req_count = req_objects[pctile][0]
            # if sd > 0:
            #     while req_count <= 1:
            #         pctile += 1
            #         req_obj = req_objects[pctile][1]
            #         req_count = req_objects[pctile][0]
            
            end_object = False
            if sd < 0:
                ## Introduce a new object
                end_object = True
                sz_removed += req_obj.s
                evicted_ += 1
            else:
                sd = random.randint(sd, sd+200000) + curr.findUniqBytes(req_obj, debug)

            if sd >= root.s:
                fail += 1
                continue
            
            n  = node(req_obj.obj_id, req_obj.s)        
            n.set_b()            

            ## Add the object at the top of the list to the trace
            c_trace.append(n.obj_id)        

            if req_obj.obj_id > curr_max_seen:
                curr_max_seen = req_obj.obj_id
            
            sampled_fds.append(sd)

            if end_object == False:

                try:
                    ## Insert the object at the specified stack distance
                    descrepency, land, o_id = root.insertAt(sd, n, 0, curr.id, debug)                            
                except:
                    print("sd : ", sd, root.s)
                
                local_uniq_bytes = 0

                if n.parent != None :
                    ## Rebalance the tree if the number of children of the parent node is greater than threshold
                    root = n.parent.rebalance(debug)

            else:
                
                ## As we remove objects from the top of the list, add objects towards the end of the list
                ## so that the we have enough objects in the list i.e., size of the list is greater than MAX_SD
                while root.s < MAX_SD:

                    ## Require more objects
                    if (total_objects + 1) % (70*MIL) == 0:

                        n_sizes        = []
                        n_popularities = []
                        i = -1
                        for i in range(len(OWV)-1):
                            SZ = self.sz_dsts[trafficClasses[i]]
                            n_sizes.extend(SZ.sample_keys(int(70*MIL * OWV[i])))

                            P = self.popularity_dsts[trafficClasses[i]]
                            n_popularities.extend(P.sample_keys(int(70*MIL * OWV[i])))
            
                        SZ = self.sz_dsts[trafficClasses[i+1]]
                        n_sizes.extend(SZ.sample_keys(int(70*MIL) - len(n_sizes)))
                        P = self.popularity_dsts[trafficClasses[i+1]]
                        n_popularities.extend(P.sample_keys(int(70*MIL) - len(n_popularities)))
        
                        random.shuffle(n_sizes)
                        random.shuffle(n_popularities)        
                        sizes.extend(n_sizes)        
                        popularities.extend(n_popularities)
                        
                        reqs_seen_n = [0]*70*MIL
                        reqs_seen.extend(reqs_seen_n)

                        
                    total_objects += 1
                    sz = sizes[total_objects]
                    sz_added += sz
                    n = node(total_objects, sz)
                    n.set_b()
                    
                    ## Insert the new object at the end of the list 
                    descrepency, x, y = root.insertAt(root.s - 1, n, 0, curr.id, debug)
            
                    if n.parent != None:
                        root = n.parent.rebalance(debug)

            if curr.obj_id == req_obj.obj_id:
                next, success = curr.findNext()
                while (next != None and next.b == 0) or success == -1:
                    next, success = next.findNext()
                curr = next

            del_nodes = req_obj.cleanUpAfterInsertion(sd, n, debug)        

            if i % 100000 == 0:
                self.log_file.write("Trace computed : " +  str(i) + " " +  str(datetime.datetime.now()) +  " " + str(root.s) + " " + str(total_objects) + " " + str(curr_max_seen) + " fail : " + str(fail) + " sz added : " + str(sz_added) + " sz_removed : " + str(sz_removed) + "\n")
                print("Trace computed : " +  str(i) + " " +  str(datetime.datetime.now()) +  " " + str(root.s) + " " + str(total_objects) + " " + str(curr_max_seen) + " fail : " + str(fail) + " sz added : " + str(sz_added) + " sz_removed : " + str(sz_removed) + " evicted : " +  str(evicted_))
                self.log_file.flush()
                if self.printBox != None:
                    self.printBox.setText("Generating synthetic trace: " + str(i*100/self.args.length) + "% complete ...")
                self.curr_iter = i

            reqs_seen[req_obj.obj_id] += 1
            i += 1

        tm_now = int(time.time())
        os.mkdir("OUTPUT/" + str(tm_now))
        f = open("OUTPUT/" + str(tm_now) + "/gen_sequence.txt", "w")

        with open("OUTPUT/" + str(tm_now) + "/command.txt", 'w') as fp:
            fp.write('\n'.join(sys.argv[1:]))
            
        ## Assign timestamp based on the byte-rate of the FD
        self.assign_timestamps(c_trace, sizes, fd.byte_rate, f)
                
        ## We are done!
        if self.printBox != None:
            self.printBox.setText("Done! Ready again ...")


    ## Assign timestamp based on the byte-rate of the FD
    def assign_timestamps(self, c_trace, sizes, byte_rate, f):
        timestamp = 0
        KB_added = 0
        KB_rate = byte_rate/1000

        for c in c_trace:
            KB_added += sizes[c]
            f.write(str(timestamp) + "," + str(c) + "," + str(sizes[c]) + "\n")

            if KB_added >= KB_rate:
                timestamp += 1
                KB_added = 0
            

    ## Read object size distribution of the required traffic classes
    def read_obj_size_dst(self):
        self.sz_dsts = defaultdict()

        for c in self.trafficMixer.trafficClasses:
            sz_dst = SZ_dst("FOOTPRINT_DESCRIPTORS/" + str(c) + "/sz.txt", 0, TB)
            self.sz_dsts[c] = sz_dst


    ## Read object size distribution of the required traffic classes
    def read_popularity_dst(self):
        self.popularity_dsts = defaultdict()

        for c in self.trafficMixer.trafficClasses:
            popularity_dst = POPULARITY_dst("FOOTPRINT_DESCRIPTORS/" + str(c) + "/popularity.txt", 0, TB)
            self.popularity_dsts[c] = popularity_dst

