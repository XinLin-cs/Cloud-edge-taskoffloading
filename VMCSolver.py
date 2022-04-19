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

    def solve_HomogeneousModel(self):
        src = self.EDGE_src
        dst = self.EDGE_dst
        # step 1
        edge = self.N                               
        cloud = self.N + 1
        self.logger.info('EDGE: %d',edge)
        self.logger.info('Cloud: %d',cloud)
        
        
        capacities = []
        # step 3
        for i in range(0, self.M):
            capacities.append(self.EDGE_weight[i][0]-self.EDGE_weight[i][1])
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
        print(src)
        print(dst)
        print(capacities)

        max_flow = pywrapgraph.SimpleMaxFlow()
        for i in range(0, len(capacities)):
            max_flow.AddArcWithCapacity(src[i], dst[i], capacities[i])
        # Find the maximum flow between edge and cloud.
        if max_flow.Solve(0, self.N-1) != max_flow.OPTIMAL:
            print('There was an issue with the max flow input.')
            return
        mf = max_flow.OptimalFlow()
        self.logger.info('Max flow(Min cut): %d',mf)

        # term1
        term1 = 0
        for i in range(0, self.M):
            term1 += self.EDGE_weight[i][1]
        self.logger.info('term1: %d',term1)
        # term2
        term2 = 0
        for i in range(0, self.N):
            term2 += min(self.NODE_weight[i][0], self.NODE_weight[i][1])
        self.logger.info('term2: %d',term2)

        return mf+term1+term2
            
    
