from convertingGraph import getGraph
from VMCSolver import Solver
import pandas as pd
from tqdm import tqdm
from numpy import mean
import logging


resMat = []
for repeating in range(0,1):
    graphs = getGraph()
    # running all datasets
    for g in graphs:
        print("==============",g['tag'],"==============")
        VMCs = []
        HETOs = []
        GREEs = []
        D2Ds = []
        solver = Solver(showdebug=False)
        solver.mounting_data(n=g['n'], m=g['m'], src=g['src'],dst=g['dst'], edge_weight=g['wij'], node_weight=g['wi'])
        
        cost , exeTime , Vx = solver.solve_VMC()
        VMCs.append(cost)
        cost , exeTime = solver.solve_HETO()
        HETOs.append(cost)
        cost , exeTime = solver.solve_GREE()
        GREEs.append(cost)
        cost , exeTime = solver.solve_D2D()
        D2Ds.append(cost)
        resMat.append([g['tag'],'VMC',mean(VMCs),exeTime])
        resMat.append([g['tag'],'HETO',mean(HETOs),exeTime])
        resMat.append([g['tag'],'GREE',mean(GREEs),exeTime])
        resMat.append([g['tag'],'D2D',mean(D2Ds),exeTime])
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