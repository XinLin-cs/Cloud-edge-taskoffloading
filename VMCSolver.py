# settings 
#========================================================

import logging
import math
from tabnanny import check
import time
from ortools.graph import pywrapgraph

class Solver(object):
    def __init__(self, ):
        logging.basicConfig(level = logging.INFO,format = '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        self.logger = logging.getLogger(__name__)
        pass
    
    def mounting_data(self, n, m, src, dst, edge_weight, node_weight):
        self.N = n
        self.M = m
        self.EDGE_src = src
        self.EDGE_dst = dst
        self.EDGE_weight = edge_weight
        self.NODE_weight = node_weight

    # Homogeneous Model
    # VMC
    def solve_VMC(self):
        TIME1 = time.perf_counter()
        # step 1
        edge = self.N                             
        cloud = self.N + 1
        self.logger.info('EDGE: %d',edge)
        self.logger.info('Cloud: %d',cloud)
        
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
        self.logger.info('Max flow(Min cut): %d',mf)

        # term1
        term1 = 0
        for i in range(0, self.M):
            term1 += self.EDGE_weight[i][0]
        self.logger.info('term1: %d',term1)
        # term2
        term2 = 0
        for i in range(0, self.N):
            term2 += min(self.NODE_weight[i][0], self.NODE_weight[i][1])
        self.logger.info('term2: %d',term2)
        ctotal = mf+term1+term2
        self.logger.info('Cost: %f',ctotal) 

        TIME2 = time.perf_counter()
        exeTIME = (TIME2-TIME1) * 1e3
        self.logger.info('Execution Time (ms): %f',exeTIME)
        return ctotal, exeTIME

    # Hetrogeneous Model
    # HETO
    def checkEdges(self, e1, e2):
        # ?
        # if e1['src']==e2['src'] and e1['dst']==e2['dst']:
        #     if e1['sTag']!=e2['sTag'] or e1['dTag']!=e2['dTag']:
        #         return 1

        # why the follow is wrong??
        # oh i know. it really may cause div0 error, then i add the eps
        if e1['src']==e2['src'] and e1['sTag']!=e2['sTag']:
                return 1
        if e1['src']==e2['dst'] and e1['sTag']!=e2['dTag']:
                return 1
        if e1['dst']==e2['src'] and e1['dTag']!=e2['sTag']:
                return 1
        if e1['dst']==e2['dst'] and e1['dTag']!=e2['dTag']:
                return 1
        return 0

    def solve_HETO(self):
        TIME1 = time.perf_counter()
        # step 1
        Ea = []
        for i in range(0, self.M):
            for j in range(0, 4):
                Ea.append({
                    'src': self.EDGE_src[i]-1,
                    'dst': self.EDGE_dst[i]-1,
                    'w': self.EDGE_weight[i][j],
                    'sTag': j // 2, # src: edge=0,1 cloud=2,3
                    'dTag': j % 2, # dst: edge=0,2 cloud=1,3
                })
        # step 2
        Ni = [0] * (self.N + 1)
        for i in range(0, self.M):
            Ni[self.EDGE_src[i]-1]+=1
            Ni[self.EDGE_dst[i]-1]+=1
        for i in range(0, len(Ea)):
            # src term
            vi , vj = Ea[i]['src'] , Ea[i]['dst']
            if Ea[i]['sTag'] == 0:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vi][0] / Ni[vi]
            else:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vi][1] / Ni[vi]
            # dst term
            if Ea[i]['dTag'] == 0:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vj][0] / Ni[vj]
            else:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vj][1] / Ni[vj]
        # step 3
        ctotal = 0
        rmvFlag = [0] * (len(Ea))
        cnt = [0] * (len(Ea))
        for i in range(0,len(Ea)):
            for j in range(0,len(Ea)):
                cnt[i] += self.checkEdges(Ea[i], Ea[j])
        nowsz = len(Ea)
        while (nowsz>0):
            # self.logger.info('rest edges: %d',nowsz)
            vmin , pmin = 0 , -1 
            # find minimal
            for i in range(0,len(Ea)):
                if rmvFlag[i] == 1:
                    continue
                tmp = 1.0 * Ea[i]['w'] / (cnt[i]+1e-6)
                if pmin==-1 or tmp < vmin:
                    vmin = tmp
                    pmin = i
            # add ctotal 
            ctotal += Ea[pmin]['w']
            # delete edges
            for i in range(0,len(Ea)):
                if rmvFlag[i] == 1:
                    continue
                if i==pmin or self.checkEdges(Ea[pmin], Ea[i])==1:
                    for j in range(0,len(Ea)):
                        if rmvFlag[j] == 1:
                            continue
                        if self.checkEdges(Ea[i], Ea[j])==1:
                            cnt[j] -= 1
                    rmvFlag[i] = 1
                    nowsz -= 1
        self.logger.info('Cost: %f',ctotal) 

        TIME2 = time.perf_counter()
        exeTIME = (TIME2-TIME1) * 1e3
        self.logger.info('Execution Time (ms): %f',exeTIME) 
        return ctotal , exeTIME