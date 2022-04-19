from cProfile import label
import matplotlib.pyplot as plt
import pandas as pd
import math

from IPython import display
display.set_matplotlib_formats('svg')

def drawing_graph(dataset, line_point=10):
    # 离散化
    Max = Min = []
    for column in dataset:
        Max.append(dataset[column].max())
        Min.append(dataset[column].min())
    Max, Min = max(Max), min(Min)
    width = (Max+1-Min)/line_point

    names = []
    values = {'time_local':[],'time_search':[],'time_dp':[]}
    for i in range(0, line_point):
        names.append(int(Min+i*width+width/2))
        values['time_local'].append(0)
        values['time_search'].append(0)
        values['time_dp'].append(0)
    for column in values:
        for it in dataset[column]:
            values[column][int((it-Min)/width)]+=1

    plt.figure(figsize=(9, 3))
    plt.subplot(131)
    plt.plot(names, values['time_local'], label='local')
    plt.plot(names, values['time_search'], linewidth=3.0, label='search')
    plt.plot(names, values['time_dp'], label='dp')
    plt.legend(loc='upper right')  # loc代表图例所在的位置

    p2 = plt.subplot(132)
    p2.boxplot([dataset['time_local'],dataset['time_search'],dataset['time_dp']])
    # p2.set_xlabel("xlabel")
    p2.set_ylabel("s")               
    p2.set_xticklabels(['time_local','time_search','time_dp'],  rotation=15,fontsize=10)   # 设置x轴坐标值的标签 旋转角度 字体大小
    
    p3 = plt.subplot(133)
    p3.boxplot([dataset['spd_search'],dataset['spd_dp']])
    # p3.set_xlabel("xlabel") 
    p3.set_ylabel("log10(μs)")               
    p3.set_xticklabels(['spd_search','spd_dp'],  rotation=15,fontsize=10)   # 设置x轴坐标值的标签 旋转角度 字体大小
    
    plt.suptitle('Cloud-edge taskoffloading')
    plt.show()

data_df = pd.read_csv('./data/result.csv' ,sep=',')

drawing_graph(data_df)