import matplotlib.pyplot as plt
import pandas as pd

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
    values = {'time_local':[],'time_best':[],'time_dp':[]}
    for i in range(0, line_point):
        names.append(int(Min+i*width+width/2))
        values['time_local'].append(0)
        values['time_best'].append(0)
        values['time_dp'].append(0)
    for column in dataset:
        for it in dataset[column]:
            values[column][int((it-Min)/width)]+=1

    plt.figure(figsize=(9, 3))
    plt.subplot(131)
    plt.plot(names, values['time_local'])
    plt.plot(names, values['time_best'])
    plt.plot(names, values['time_dp'])
    p2 = plt.subplot(132)
    p2.boxplot([dataset['time_local'],dataset['time_best'],dataset['time_dp']])
    # p2.set_xlabel("xlabel")               
    p2.set_xticklabels(['time_local','time_best','time_dp'],  rotation=15,fontsize=10)   # 设置x轴坐标值的标签 旋转角度 字体大小
    plt.subplot(133)
    plt.bar(['search','dp'],[1.5288479000000024,0.018382799999997923],width=0.5)

    plt.suptitle('Makespan')
    plt.show()

data_df = pd.read_csv('./data/result.csv' ,sep=',')

drawing_graph(data_df)