from convertingGraph import getGraph
from VMCSolver import Solver
import pandas as pd

graphs = getGraph()

resMat = []

# running all datasets
for g in graphs:
    print("==============",g['tag'],"VMC","==============")
    solver = Solver()
    solver.mounting_data(n=g['n'], m=g['m'], src=g['src'],dst=g['dst'], edge_weight=g['wij'], node_weight=g['wi'])
    cost , exeTime = solver.solve_VMC()
    resMat.append([g['tag'],'VMC',cost,exeTime])

    print("==============",g['tag'],"HETO","==============")
    solver = Solver()
    solver.mounting_data(n=g['n'], m=g['m'], src=g['src'],dst=g['dst'], edge_weight=g['wij'], node_weight=g['wi'])
    cost , exeTime = solver.solve_HETO()
    resMat.append([g['tag'],'HETO',cost,exeTime])

# save result as csv
df = pd.DataFrame(
    resMat,
    columns=['Tag','Method','Cost','exeTime']
)
df.to_csv('./data/result/result.csv',index=False)

# EXAMPLE-HomogeneousModel
print("==============","EXAMPLE-Fig5","==============")
solver = Solver()
solver.mounting_data(
    n=4, 
    m=4, 
    src=[1,1,2,2],
    dst=[2,4,3,4], 
    edge_weight=[[4,12,12,4],[7,13,13,7],[9,15,15,9],[6,7,7,6]], 
    node_weight=[[4,2],[8,1],[11,3],[5,16]]
)
res_VMC = solver.solve_VMC()
print("VMC", res_VMC)
res_HETO = solver.solve_HETO()
print("HETO", res_HETO)