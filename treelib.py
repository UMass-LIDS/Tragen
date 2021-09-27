from numpy.random import choice
import numpy as np
import sys
import random

root = None

class node:
    counter = 0

    def __init__(self, obj_id, size):
        self.obj_id = obj_id
        self.s = size
        self.b = 0
        self.stop_del = False
        self.children = []
        self.next = None
        self.parent = None
        self.id = node.counter
        self.child_idx = 0
        self.is_root = False
        self.last_access = -1
        node.counter += 1

    def addValTillRoot(self, val):
        p = self.parent
        while p != None:
            p.s += val
            p = p.parent

    def __del__(self):
        pass

    def lca(self, n):
        a = self
        while a != None:
            b = n
            while b != None:
                if a.id == b.id:                    
                    return a.id
                b = b.parent
            a = a.parent

        print('LCA : Parent connections not correct ', self.id, n.id)
        sys.exit()

    def add_child(self, n):
        n.child_idx = len(self.children)
        self.children.append(n)
        n.parent = self

    def set_parent(self, n):
        self.parent = n

    def set_next(self, n):
        self.next = n


    def findUniqBytes(self, n, debug):

        curr_node = self
        next_node = n
        local_uniq_bytes = 0

        ### If curr node and next node belong to the same parent
        if curr_node.parent.id == next_node.parent.id:
            for i in range(curr_node.child_idx + 1, next_node.child_idx):
                local_uniq_bytes += curr_node.parent.children[i].s * curr_node.parent.children[i].b

            return local_uniq_bytes
        
        lca_id = curr_node.lca(next_node)        
        
        curr_parent = curr_node.parent
        child_node = curr_node
        child_idx = child_node.child_idx
            
        while curr_parent.id != lca_id:
                
            if child_idx == len(curr_parent.children):
                curr_parent = curr_parent.parent
                child_node  = child_node.parent
                child_idx   = child_node.child_idx
                continue

            for i in range(child_idx + 1, len(curr_parent.children)):
                lb = curr_parent.children[i].s * curr_parent.children[i].b
                local_uniq_bytes += lb

            curr_parent = curr_parent.parent
            child_node  = child_node.parent
            child_idx   = child_node.child_idx

        save_node1 = child_node

        curr_parent = next_node.parent
        child_node = next_node
        child_idx = child_node.child_idx

        
        while curr_parent.id != lca_id:
            
            if child_idx == 0:
                curr_parent = curr_parent.parent
                child_node  = child_node.parent
                child_idx   = child_node.child_idx
                continue
            
            for i in range(0, child_idx):
                lb = curr_parent.children[i].s * curr_parent.children[i].b
                local_uniq_bytes += lb

            curr_parent = curr_parent.parent
            child_node  = child_node.parent
            child_idx   = child_node.child_idx

        save_node2 = child_node

        for i in range(save_node1.child_idx + 1, save_node2.child_idx):
            lb = save_node1.parent.children[i].s * save_node1.parent.children[i].b
            local_uniq_bytes += lb

        return local_uniq_bytes

    def cleanUpAfterInsertion(self, sd, inserted_node, debug):
        curr_node = self
        next_node = curr_node.next

        if next_node == None:
            self.delete_node(debug)
            return

        uniq_bytes = curr_node.s
        cnt = 0
        to_del_nodes = []

        while uniq_bytes < sd:

            if next_node == None:
                break

            to_del_nodes.append(curr_node)
            uniq_bytes += curr_node.findUniqBytes(next_node)
            next_node = next_node.next
            curr_node = curr_node.next

        for d in to_del_nodes:
            inserted_node.next = d.next
            d.delete_node()

        return to_del_nodes


    def delete_node(self, debug):
        weight = self.s * self.b
        p = self.parent
        
        if p == None:
            return
              
        self.parent.children = [c for c in self.parent.children if c.id != self.id]
        
        i = 0
        for c in self.parent.children:
            c.child_idx = i
            i += 1

        while p != None:
            p.s = p.s - weight
            p = p.parent                

        p = self.parent
        
        if p.s == 0:
            p.delete_node(debug)
        

    def rebalance(self, debug):
        
        if self.is_root == True or self == None:
            ## if you create new root return new root
            if len(self.children) > 8:
               # debug.write("root rebalanced \n")
                new_root = node("nl", 0)
                new_root.s = self.s
                new_root.set_b()
                new_root.children.append(self)
                new_root.is_root = True
                self.is_root = False
                self.parent = new_root
                self.split_node()
                return new_root
                
            ## if you dont create new root 
            return self

        if len(self.children) > 8:
            self.split_node()

        r = self.parent.rebalance(debug)
        return r


    def delete_last_node(self, debug):
        c = self

        while len(c.children) > 0:
            c = c.children[-1]

        obj_id = c.obj_id
        c.delete_node(debug)

        return c.s, obj_id
                    

    def split_node(self):
        n_pos = self.child_idx

        new_node = node("nl", 0)

        rm_children = self.children[4:]
        i = 0
        rm_val = 0
        for r_c in rm_children:
            r_c.child_idx = i
            i += 1
            rm_val += (r_c.s * r_c.b)
            r_c.parent = new_node

        new_node.children = rm_children
        new_node.s = rm_val
        new_node.set_b()
        new_node.parent = self.parent
        self.parent.children.insert(n_pos + 1, new_node)

        i = 0
        for c in self.parent.children:
            c.child_idx = i
            i += 1

        self.children = self.children[:4]
        self.s = self.s - rm_val
        
    def insertAt(self, sd, n, pos, curr_id, debug):

        if len(self.children) == 0:

            thr = float(sd)/self.s
            z = np.random.random()
            descrepency = -1 * sd

            fall_pos = round(thr, 3)

            if self.id == curr_id:
                pos += 1
                descrepency = 0                

            elif thr > z:
                pos += 1
                descrepency = self.s - sd
                
            self.parent.children.insert(pos, n)
            n.parent = self.parent

            i = 0
            for c in self.parent.children:
                c.child_idx = i
                i += 1

            n.update_till_root()
            return descrepency, fall_pos, self.obj_id

        i = 0
        sd_rem = sd
        descrepency = 0
        
        for c in self.children:
            if sd_rem < c.s:
                descrepency, fall_pos, obj_id = c.insertAt(sd_rem, n, i, curr_id, debug)
                break

            i += 1
            sd_rem = sd_rem - (c.s * c.b)

        return descrepency, fall_pos, obj_id

    def deleteAt(self, sd, debug):

        if len(self.children) == 0:
            self.delete_node(debug)
            return self
            
        sd_rem = sd
        
        for c in self.children:
            if sd_rem < c.s:
                n = c.deleteAt(sd_rem, debug)
                break
            sd_rem = sd_rem - (c.s * c.b)
            
        return n


    def dontDeleteAt(self, sd, debug):

        if len(self.children) == 0:
            return self
            
        sd_rem = sd
        
        for c in self.children:
            if sd_rem < c.s:
                n = c.dontDeleteAt(sd_rem, debug)
                break
            sd_rem = sd_rem - (c.s * c.b)
            
        return n

    
    def deleteAtApprox(self, sd, popularities, req_count, number_ele, debug):
        curr = self.dontDeleteAt(sd, debug)
        max_node = curr
        req_nodes = []
        pps = []
        max_diff = popularities[curr.obj_id] - req_count[curr.obj_id]
        foundCandidate = False
        
        while True:
            diff = popularities[curr.obj_id] - req_count[curr.obj_id]
            if  diff > 0:
                req_nodes.append(curr)
                if diff >= max_diff:
                    max_diff = diff                
                    max_node = curr
                    
            if len(req_nodes) >= number_ele:
                break

            curr, s = curr.findNext()
                
        #sum_pps = sum(pps)
        #pps = [float(p)/sum_pps for p in pps]
        #n = choice(req_nodes, 1, p=pps)
        max_node.delete_node(debug)
        return max_node
        

    def delete_random_node(self, debug):
        if len(self.children) == 0:
            self.delete_node(debug)
            return self.s, self.obj_id
        else:
            r = random.randint(0, len(self.children)-1)        
            sz, obj_id = self.children[r].delete_random_node(debug)
            return sz, obj_id

    def delete_last_node(self, debug):
        if len(self.children) == 0:
            self.delete_node(debug)
            return self.s, self.obj_id
        else:
            sz, obj_id = self.children[-1].delete_last_node(debug)
            return sz, obj_id
        
    def add_child_first_pos(self, n, debug):
        self.children.insert(0, n)
        i = 0
        for c in self.children:
            c.child_idx = i
            i += 1
        
        n.parent = self
        n.update_till_root()

        return self.rebalance(debug)

    def add_child_last_pos(self, n, debug):
        p = self
        while len(p.children) > 0:
            p = p.children[-1]
        p = p.parent
        p.children.append(n)
        
        i = 0
        for c in p.children:
            c.child_idx = i
            i += 1

        n.parent = p
        n.update_till_root()
            
        return n.rebalance(debug)
    
    def set_b(self):
        self.b = 1

    def unset_b(self):
        self.b = 0

    def inorder(self):
        print(self.o_id)
        if len(self.children) == 0:
            return
        for c in self.children:
            c.inorder()


    def findNext(self):
        curr_node = self
        p_node = curr_node.parent

        while curr_node.child_idx >= len(p_node.children) - 1:

            curr_node = curr_node.parent
            p_node = p_node.parent

            if p_node == None:
                return [None, 1]


        n_node = p_node.children[curr_node.child_idx + 1]
            
        while len(n_node.children) > 0:
            n_node = n_node.children[0]
            
        if n_node.obj_id == "nl":
            return [n_node, -1]

        return [n_node, 1]


    def findPrevious(self):
        curr_node = self
        p_node = curr_node.parent

        while curr_node.child_idx == 0:

            curr_node = curr_node.parent
            p_node = p_node.parent

            if p_node == None:
                return [None, 1]

        n_node = p_node.children[curr_node.child_idx - 1]
            
        while len(n_node.children) > 0:
            n_node = n_node.children[-1]
            
        if n_node.obj_id == "nl":
            return [n_node, -1]

        return [n_node, 1]


    ## A function to swap self with n
    def swap(self, n):

        self.dimnish_till_root()
        n.dimnish_till_root()
        
        n_cidx = n.child_idx
        s_cidx = self.child_idx

        s_parent = self.parent
        n_parent = n.parent

        n_parent.children[n_cidx] = self
        s_parent.children[s_cidx] = n

        self.parent = n_parent
        n.parent = s_parent
        n.child_idx = s_cidx
        self.child_idx = n_cidx

        n.update_till_root()
        self.update_till_root()
        
    def update_till_root(self):        
        val = self.s * self.b
                
        p = self.parent
        while p != None:
            p.s += val
            p = p.parent

    def dimnish_till_root(self):        
        val = self.s * self.b
                
        p = self.parent
        while p != None:
            p.s -= val
            p = p.parent


class lirsnode(node):
    def __init__(self, obj_id, size):
        node.__init__(self, obj_id, size)
        self.lir = False
        
    def setLIR(self):
        self.lir = True

    def unsetLIR(self):
        self.lir = False
               
    
