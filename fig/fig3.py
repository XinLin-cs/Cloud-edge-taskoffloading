import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('./data/result/result.csv')

XLabel = ['dataset1', 'dataset2', 'dataset3']
x = np.arange(len(XLabel))

homo = ['dataset1_homo', 'dataset2_homo', 'dataset3_homo']


Cost_VMC = df[df['Tag'].isin(homo)][df['Method']=='VMC']['Cost'].tolist()
Cost_D2D = df[df['Tag'].isin(homo)][df['Method']=='D2D']['Cost'].tolist()
Cost_GREE = df[df['Tag'].isin(homo)][df['Method']=='GREE']['Cost'].tolist()

width = 0.10
gap = 0.01

fig, ax = plt.subplots()
rects1 = ax.bar(x - width - gap, Cost_D2D, width, label='D2D', hatch='/')
rects2 = ax.bar(x , Cost_GREE, width, label='GREE', hatch='//')
rects3 = ax.bar(x + width + gap, Cost_VMC, width, label='VMC', hatch='-')
# 为y轴、标题和x轴等添加一些文本。
ax.set_ylabel('Cost', fontsize=16)
# ax.set_xlabel('X轴', fontsize=16)
# ax.set_title('这里是标题')
ax.set_xticks(x)
ax.set_xticklabels(XLabel)
ax.legend()

fig.tight_layout()
plt.show()
