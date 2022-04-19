# settings 
#========================================================

import logging
import math
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
    def solve_VMC(self):
        # step 1
        edge = self.N + 1                              
        cloud = self.N + 2
        self.logger.info('EDGE: %d',edge)
        self.logger.info('Cloud: %d',cloud)
        
        # step 3
        src = []
        dst = []
        capacities = []
        for i in range(0, self.M):
            src.append(self.EDGE_src[i])
            dst.append(self.EDGE_dst[i])
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

        return mf+term1+term2

    # Hetrogeneous Model
    def checkEdges(self, e1, e2):
        if e1['src']==e2['src']:
            if (e1['flag']==0 or 1) and (e2['flag']==2 or 3):
                return 1
            if (e1['flag']==2 or 3) and (e2['flag']==0 or 1):
                return 1
        if e1['dst']==e2['dst']:
            if (e1['flag']==0 or 3) and (e2['flag']==1 or 2):
                return 1
            if (e1['flag']==1 or 2) and (e2['flag']==0 or 3):
                return 1
        return 0

    def solve_HETO(self):
        # step 1
        Ea = []
        for i in range(0, self.M):
            for j in range(0, 3):
                Ea.append({
                    'src': self.EDGE_src[i],
                    'dst': self.EDGE_dst[i],
                    'w': self.EDGE_weight[i][j],
                    'flag': j,
                })
        # step 2
        Ni = [0] * (self.N + 1)
        for i in range(0, self.M):
            Ni[self.EDGE_src[i]]+=1
            Ni[self.EDGE_dst[i]]+=1
        for i in range(0, self.M):
            # src term
            vi , vj = Ea[i]['src'] , Ea[i]['dst']
            if Ea[i]['flag'] == 0 or 1:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vi][0] / Ni[vi]
            elif Ea[i]['flag'] == 2 or 3:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vi][1] / Ni[vi]
            # dst term
            if Ea[i]['flag'] == 0 or 2:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vj][0] / Ni[vj]
            elif Ea[i]['flag'] == 1 or 3:
                Ea[i]['w'] += 1.0 * self.NODE_weight[vj][1] / Ni[vj]
        # step 3
        ctotal = 0
        while (len(Ea)>0):
            self.logger.info('rest edges: %d',len(Ea))
            vmin , pmin = 0 , 0 
            # find minimal
            for i in range(0,len(Ea)):
                cnt = 0
                for j in range(0,len(Ea)):
                    cnt += self.checkEdges(Ea[i], Ea[j])
                tmp = 1.0 * Ea[i]['w'] / cnt
                if tmp > vmin:
                    vmin = tmp
                    pmin = i
            # add ctotal 
            ctotal += Ea[pmin]['w']
            # delete edges
            Eb = []    
            for i in range(0,len(Ea)):
                if i==pmin or self.checkEdges(Ea[i], Ea[pmin])==1:
                    continue
                Eb.append(Ea[i])
            Ea = Eb
            
        return ctotal