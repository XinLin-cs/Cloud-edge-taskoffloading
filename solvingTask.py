# settings
task_tag = "data/Task1.mat"
#========================================================
import time
import numpy as np
import pandas as pd
import scipy.io as scio
from tqdm import tqdm
from Solver import Solver
import math

#loadingdata
dataFile = task_tag
data = scio.loadmat(dataFile)
print(data)
dataMat = data.get('EXAMPLE')[0]
#solving
time_local = []
time_search = []
spd_search = []
time_dp = []
spd_dp = []

for i in tqdm(range(0,len(dataMat))):
    task_unit = dataMat[i]
    solver = Solver()
    solver.mounting_data(task_unit)
    time_local.append(solver.check_state())
    t1 = time.perf_counter()
    time_search.append(solver.solve_search())
    t2 = time.perf_counter()
    time_dp.append(solver.solve_dp())
    t3 = time.perf_counter()

    spd_search.append(math.log((t2-t1)*1e6,10))
    spd_dp.append(math.log((t3-t2)*1e6,10))

# print(time_local)
# print(time_best)
# print(time_dp)

#saving
result = {
    'time_local':time_local,
    'time_search':time_search,
    'spd_search':spd_search,
    'time_dp':time_dp,
    'spd_dp':spd_dp,
}
result_df = pd.DataFrame(result)
result_df.to_csv('./data/result.csv',sep=',',index=False,header=True)