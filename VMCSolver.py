# settings 
#========================================================

import logging
import math
from pickle import TRUE
from tabnanny import check
import time
from ortools.graph import pywrapgraph
from sqlalchemy import true
import random

class Solver(object):
    def __init__(self, showdebug=False): 
        logging.basicConfig(level = logging.DEBUG,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        if showdebug==True:
            self.logger.setLevel(logging.DEBUG)
        else:
            self.logger.setLevel(logging.INFO)

    
    def mounting_data(self, n, m, src, dst, edge_weight, node_weight):
        self.N = n
        self.M = m
        self.EDGE_src = src
        self.EDGE_dst = dst
        self.EDGE_weight = edge_weight
        self.NODE_weight = node_weight

    def checkCost(self, vx):
        ctotal = 0
        for i in range(0,self.N):
            ctotal+=self.NODE_weight[i][vx[i]]
        for i in range(0,self.M):
            s = vx[self.EDGE_src[i]-1]
            d = vx[self.EDGE_dst[i]-1]
            ctotal+=self.EDGE_weight[i][s*2+d]
        return ctotal

    def solve_D2D(self):
        vx = []
        for i in range(0,self.N):
            vx.append(random.randint(0,1))
        cost = self.checkCost(vx)
        self.logger.debug('[D2D] Cost: %f',cost) 
        return cost, vx

    # Homogeneous Model
    # VMC
    def solve_VMC(self):
        TIME1 = time.perf_counter()
        # step 1
        edge = self.N                             
        cloud = self.N + 1
        self.logger.debug('EDGE: %d',edge)
        self.logger.debug('Cloud: %d',cloud)
        
        # step 3
        src = []
        dst = []
        capacities = []
        for i in range(0, self.M):
            src.append(self.EDGE_src[i]-1)
            dst.append(self.EDGE_dst[i]-1)
            capacities.append(self.EDGE_weight[i][1]-self.EDGE_weight[i][0])
        
        # step 4
        for i in range(0, self.N):
            if self.NODE_weight[i][0]<self.NODE_weight[i][1]:
                src.append(edge)
                dst.append(i)
                capacities.append(self.NODE_weight[i][1]-self.NODE_weight[i][0])
            else:
                src.append(i)
                dst.append(cloud)
                capacities.append(self.NODE_weight[i][0]-self.NODE_weight[i][1])
        # print(src)
        # print(dst)
        # print(capacities)

        max_flow = pywrapgraph.SimpleMaxFlow()
        for i in range(0, len(capacities)):
            max_flow.AddArcWithCapacity(src[i], dst[i], capacities[i])
            # oppsited edge
            max_flow.AddArcWithCapacity(dst[i], src[i], capacities[i])
        # Find the maximum flow between edge and cloud.
        if max_flow.Solve(edge, cloud) != max_flow.OPTIMAL:
            print('There was an issue with the max flow input.')
            return
        mf = max_flow.OptimalFlow()
        self.logger.debug('Max flow(Min cut): %d',mf)

        # offloading decision
        Ve = max_flow.GetSourceSideMinCut()
        Vc = max_flow.GetSinkSideMinCut()
        Vx = [0] * self.N
        for it in Vc:
            if it < self.N:
                Vx[it]=1

        # # term1
        # term1 = 0
        # for i in range(0, self.M):
        #     term1 += self.EDGE_weight[i][0]
        # self.logger.debug('term1: %d',term1)
        # # term2
        # term2 = 0
        # for i in range(0, self.N):
        #     term2 += min(self.NODE_weight[i][0], self.NODE_weight[i][1])
        # self.logger.debug('term2: %d',term2)
        # ctotal = mf+term1+term2
        ctotal = self.checkCost(Vx)
        self.logger.debug('[VMC] Cost: %f',ctotal) 

        TIME2 = time.perf_counter()
        exeTIME = (TIME2-TIME1) * 1e3
        self.logger.debug('[VMC] Execution Time (ms): %f',exeTIME)
        return ctotal, exeTIME, Vx



    # Hetrogeneous Model
    # HETO

    class myEdge(object):
        def __init__(self, i, j, src, dst, weight):
            self.id = i*4+j
            self.src = src
            self.dst = dst
            self.w = weight
            self.sTag = j // 2 # src: edge=0,1 cloud=2,3
            self.dTag = j % 2 # dst: edge=0,2 cloud=1,3


    def checkEdges(self, e1, e2):
        # ?
        # if e1.src==e2.src and e1.dst==e2.dst:
        #     if e1.sTag!=e2.sTag or e1.dTag!=e2.dTag:
        #         return 1

        # why the follow is wrong??
        # oh i know. it really may cause div0 error, then i add the eps
        if e1.src==e2.src and e1.sTag!=e2.sTag:
                return 1
        if e1.src==e2.dst and e1.sTag!=e2.dTag:
                return 1
        if e1.dst==e2.src and e1.dTag!=e2.sTag:
                return 1
        if e1.dst==e2.dst and e1.dTag!=e2.dTag:
                return 1
        return 0

    def solve_HETO(self):
        TIME1 = time.perf_counter()
        # step 1
        Ea = []
        for i in range(0, self.M):
            for j in range(0, 4):
                Ea.append(self.myEdge(i,j,self.EDGE_src[i]-1,self.EDGE_dst[i]-1,self.EDGE_weight[i][j]))
                # Ea.append({
                #     'id': i*4+j,
                #     'src': self.EDGE_src[i]-1,
                #     'dst': self.EDGE_dst[i]-1,
                #     'w': self.EDGE_weight[i][j],
                #     'sTag': j // 2, # src: edge=0,1 cloud=2,3
                #     'dTag': j % 2, # dst: edge=0,2 cloud=1,3
                # })
        # step 2
        Ni = [0] * (self.N + 1)
        for i in range(0, self.M):
            Ni[self.EDGE_src[i]-1]+=1
            Ni[self.EDGE_dst[i]-1]+=1
        for i in range(0, len(Ea)):
            # src term
            vi , vj = Ea[i].src , Ea[i].dst
            if Ea[i].sTag == 0:
                Ea[i].w += 1.0 * self.NODE_weight[vi][0] / Ni[vi]
            else:
                Ea[i].w += 1.0 * self.NODE_weight[vi][1] / Ni[vi]
            # dst term
            if Ea[i].dTag == 0:
                Ea[i].w += 1.0 * self.NODE_weight[vj][0] / Ni[vj]
            else:
                Ea[i].w += 1.0 * self.NODE_weight[vj][1] / Ni[vj]
        # step 3
        ctotal = 0
        
        cnt = [0] * (len(Ea))
        for i in range(0,len(Ea)):
            for j in range(0,len(Ea)):
                cnt[i] += self.checkEdges(Ea[i], Ea[j])
        
        # edgeSet = []
        # for i in range(0,self.N):
        #     edgeSet.append([])
        # for i in range(0,len(Ea)):
        #     edgeSet[Ea[i].src].append(i)
        #     edgeSet[Ea[i].dst].append(i)
        # mutexedge = []
        # for i in range(0,len(Ea)):
        #     edges = list(
        #                 set(edgeSet[Ea[i].src])
        #                 |
        #                 set(edgeSet[Ea[i].dst])
        #             )
        #     edges2 = []
        #     for j in range(0,len(edges)):
        #         if self.checkEdges(Ea[i], Ea[edges[j]])==1:
        #             edges2.append(edges[j])
        #     mutexedge.append(edges2)

        # nowsz = len(Ea)

        # TIME3 = time.perf_counter()
        # initTIME = (TIME3-TIME1) * 1e3
        # self.logger.debug('Initial Time (ms): %f',initTIME) 

        while (len(Ea)>0):
            # self.logger.debug('rest edges: %d',nowsz)
            vmin , pmin = 0 , -1 
            # find minimal
            for i in range(0,len(Ea)):
                tmp = 1.0 * Ea[i].w / (cnt[Ea[i].id] + 1e-6)
                if pmin==-1 or tmp < vmin:
                    vmin = tmp
                    pmin = i
            # add ctotal 
            ctotal += Ea[pmin].w
            # delete edges
            
            Eb = []
            for i in range(0,len(Ea)):
                if i==pmin or self.checkEdges(Ea[pmin],Ea[i])==1:
                    for j in range(0,len(Ea)):
                        if self.checkEdges(Ea[i],Ea[j])==1:
                            cnt[Ea[j].id]-=1
                    continue
                Eb.append(Ea[i])
            Ea = Eb
                    
        self.logger.debug('[HETO] Cost: %f',ctotal) 


        
        TIME2 = time.perf_counter()
        exeTIME = (TIME2-TIME1) * 1e3
        self.logger.debug('[HETO] Execution Time (ms): %f',exeTIME) 
        return ctotal , exeTIME

    def solve_GREE(self):
        TIME1 = time.perf_counter()
        # step 1
        Ea = []
        for i in range(0, self.M):
            for j in range(0, 4):
                Ea.append(self.myEdge(i,j,self.EDGE_src[i]-1,self.EDGE_dst[i]-1,self.EDGE_weight[i][j]))
                # Ea.append({
                #     'src': self.EDGE_src[i]-1,
                #     'dst': self.EDGE_dst[i]-1,
                #     'w': self.EDGE_weight[i][j],
                #     'sTag': j // 2, # src: edge=0,1 cloud=2,3
                #     'dTag': j % 2, # dst: edge=0,2 cloud=1,3
                # })
        # step 2
        Ni = [0] * (self.N + 1)
        for i in range(0, self.M):
            Ni[self.EDGE_src[i]-1]+=1
            Ni[self.EDGE_dst[i]-1]+=1
        for i in range(0, len(Ea)):
            # src term
            vi , vj = Ea[i].src , Ea[i].dst
            if Ea[i].sTag == 0:
                Ea[i].w += 1.0 * self.NODE_weight[vi][0] / Ni[vi]
            else:
                Ea[i].w += 1.0 * self.NODE_weight[vi][1] / Ni[vi]
            # dst term
            if Ea[i].dTag == 0:
                Ea[i].w += 1.0 * self.NODE_weight[vj][0] / Ni[vj]
            else:
                Ea[i].w += 1.0 * self.NODE_weight[vj][1] / Ni[vj]
        # step 3
        ctotal = 0
        
        sum = [0] * (len(Ea))
        cnt = [0] * (len(Ea))
        for i in range(0,len(Ea)):
            for j in range(0,len(Ea)):
                if self.checkEdges(Ea[i], Ea[j])==1:
                    cnt[i]+=Ea[j].w
                    sum[i]+=1


        while (len(Ea)>0):
            # self.logger.debug('rest edges: %d',nowsz)
            vmin , pmin = 0 , -1 
            # find minimal
            for i in range(0,len(Ea)):
                avg = (cnt[Ea[i].id])/(sum[Ea[i].id]+1e-6)
                tmp = 1.0 * Ea[i].w / (avg + 1e-6)
                if pmin==-1 or tmp < vmin:
                    vmin = tmp
                    pmin = i
            # add ctotal 
            ctotal += Ea[pmin].w
            # delete edges
            
            Eb = []
            for i in range(0,len(Ea)):
                if i==pmin or self.checkEdges(Ea[pmin],Ea[i])==1:
                    for j in range(0,len(Ea)):
                        if self.checkEdges(Ea[i],Ea[j])==1:
                            cnt[Ea[j].id]-=Ea[i].w
                            sum[Ea[j].id]-=1
                    continue
                Eb.append(Ea[i])
            Ea = Eb

        self.logger.debug('[GREE] Cost: %f',ctotal) 

        TIME2 = time.perf_counter()
        exeTIME = (TIME2-TIME1) * 1e3
        self.logger.debug('[GREE] Execution Time (ms): %f',exeTIME) 
        return ctotal , exeTIME

    