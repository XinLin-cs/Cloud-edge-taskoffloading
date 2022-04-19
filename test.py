from convertingGraph import getGraph
from VMCSolver import Solver

graphs = getGraph()
for g in graphs:
    print("==============",g['tag'],"==============")
    solver = Solver()
    solver.mounting_data(n=g['n'], m=g['m'], src=g['src'],dst=g['dst'], edge_weight=g['wij'], node_weight=g['wi'])
    cost = solver.solve_HomogeneousModel()
    print(cost)

# EXAMPLE-HomogeneousModel
print("==============","EXAMPLE-Fig5","==============")
solver = Solver()
solver.mounting_data(
    n=4, 
    m=4, 
    src=[0,0,1,1],
    dst=[1,3,2,3], 
    edge_weight=[[12,4,4,12],[13,7,7,13],[15,9,9,15],[7,6,6,7]], 
    node_weight=[[4,2],[8,1],[11,3],[5,16]]
)
cost = solver.solve_HomogeneousModel()
print(cost)