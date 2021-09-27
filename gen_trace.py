import sys
from treelib import *
from collections import defaultdict

def gen_leaves(trace, sizes, items=None, initial_times=None):
    # create a tree and return

    total_sz = 0    
    st_tree = defaultdict(list)

    ## First create a level 0 trace
    trace_list = []
    seen_ele = defaultdict()

    for i in range(len(trace)):
        oid = trace[i]
        n = node(oid, sizes[oid])
        n.set_b()
        
        if items != None:
            items[oid] = n
            total_sz += sizes[oid]
            if initial_times != None:                
                n.last_access = initial_times[oid]
        
        trace_list.append(n)

        if i%10000 == 0:
            print("Parsed number of requests : ", i)

    return trace_list, total_sz



def gen_leaves_lirs(trace, sizes, items=None, initial_times=None):
    # create a tree and return

    total_sz = 0    
    st_tree = defaultdict(list)

    ## First create a level 0 trace
    trace_list = []
    seen_ele = defaultdict()

    for i in range(len(trace)):
        oid = trace[i]
        n = lirsnode(oid, sizes[oid])
        n.setLIR()
        n.set_b()
        
        if items != None:
            items[oid] = n
            total_sz += sizes[oid]
            if initial_times != None:                
                n.last_access = initial_times[oid]
        
        trace_list.append(n)

        if i%10000 == 0:
            print("Parsed number of requests : ", i)

    return trace_list, total_sz




def generate_tree(trace_list):

    lvl = 0
    st_tree = defaultdict(list)
    st_tree[lvl] = trace_list

    while len(st_tree[lvl]) > 1:

        print("Parsing through lvl : ", lvl)

        for i in range(int(len(st_tree[lvl])/2)):

            n1 = st_tree[lvl][2*i]
            n2 = st_tree[lvl][2*i+1]        
            p_n = node("nl", (n1.s*n1.b + n2.s*n2.b))

            n1.set_parent(p_n)
            n2.set_parent(p_n)

            p_n.add_child(n1)
            p_n.add_child(n2)
            p_n.set_b()        

            st_tree[lvl+1].append(p_n)

            if i%10000 == 0:
                print("Parsed number of nodes : ", i)


        print("length : ", len(st_tree[lvl]), " i : ", i)
                
        if len(st_tree[lvl]) > 2*i+2:
            n3 = st_tree[lvl][2*i+2]
            n3.set_b()
            p_n = st_tree[lvl+1][-1]
            n3.set_parent(p_n)
            p_n.add_child(n3)
            p_n.s += n3.s * n3.b
            
            
        lvl += 1

    return st_tree, lvl


def print_tree(n):
    if n.obj_id != "nl":        
        print(str(n.obj_id) + ":" + str(n.s) + ":" + str(n.b) + ":" + str(n.id))
    for c in n.children:
        print_tree(c)


def sample(vals, cdf):
    z = np.random.random()
    val = vals[-1]
    for i in range(len(vals)):
        if cdf[i] > z:
            return vals[i]
    return val


def run_test():

    trace = [1,2,3,5,1,6,7,5,1,0,2,5,7,2,1,0,5]
    sizes = []

    for i in range(8):
        sizes.append(10)

    trace_list = gen_leaves(trace, sizes)
    st_tree, lvl = generate_tree(trace_list)
    root = st_tree[lvl][0]
    curr = st_tree[0][0]

    c_trace = []

    while curr != None:
        sd = sample(sd, sd_cdf)
        n  = node(curr.obj_id, curr.s)        
        c_trace.append(curr.obj_id)
        root.insertAt(sd, n, 0)        
        curr.cleanUpAfterInsertion(sd, n)
        curr = curr.findNext()        
        while curr.b == 0:
            curr = curr.findNext()

    return c_trace




def test():
    trace = [1,2,3,5,1,6,7,5,1,0,2,5,7,2,1,0,5]
    sizes = []
    for i in range(8):
        sizes.append(10)

    trace_list = gen_leaves(trace, sizes)
    st_tree, lvl = generate_tree(trace_list)

    root = st_tree[lvl][0]
    curr = st_tree[0][0]

    ## Test 1
    i = 0
    for t in trace_list:        
        if t.next == None:
            print(t.obj_id, "None", i, "None")
        else :
            print(t.obj_id, t.next.obj_id, i, t.next.id)    
        i += 1
    

    #Test 2 - print tree
    print_tree(root)

    ## Test find_next 
    while curr != None:
         print(curr.id, curr.obj_id)
         curr = curr.findNext()

    ## Test 3 - Check if the function insertAt works
    ## Insert first object
    sd = 60
    n = node(1, 10)
    root.insertAt(sd, n, 0)
    print("--------------------------")
    print_tree(root)
    ## Insert second object
    s = 35
    n = node(2, 10)
    root.insertAt(sd, n, 0)
    print("--------------------------")
    print_tree(root)
    

    ## Test 4 - Setting the right connections
    curr.cleanUpAfterInsertion(sd, n)
    print("--------------------------")
    print_tree(root)
    

        
#if __name__=="__main__":
#    run_test()
    
