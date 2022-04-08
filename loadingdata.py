import time
import numpy as np
import pandas as pd
import scipy.io as scio
from tqdm import tqdm
from Solver import Solver
from envconfig import task_tag

#loadingdata
dataFile = task_tag
data = scio.loadmat(dataFile)
dataMat = data.get('EXAMPLE')[0]
#solving
time_local = []
time_best = []
time_dp = []
spd_search = .0
spd_dp = .0

for i in tqdm(range(0,len(dataMat))):
    task_unit = dataMat[i]
    solver = Solver()
    solver.mounting_data(task_unit)
    time_local.append(solver.check_state())
    t1 = time.perf_counter()
    time_best.append(solver.solve_search())
    t2 = time.perf_counter()
    time_dp.append(solver.solve_dp())
    t3 = time.perf_counter()
    spd_search += t2-t1
    spd_dp += t3-t2

print("search: %f seconds"%spd_search)
print("dp: %f seconds"%spd_dp)

# print(time_local)
# print(time_best)
# print(time_dp)

#saving
result = {
    'time_local':time_local,
    'time_best':time_best,
    'time_dp':time_dp,
}
result_df = pd.DataFrame(result)
result_df.to_csv('./data/result.csv',sep=',',index=False,header=True)