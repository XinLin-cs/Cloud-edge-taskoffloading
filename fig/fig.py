import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

df = pd.read_csv('./data/result/result.csv')

XLabel = ['dataset1', 'dataset2', 'dataset3']
x = np.arange(len(XLabel))

homo = ['dataset1_homo', 'dataset2_homo', 'dataset3_homo']

Cost_HETO = df[df['Tag'].isin(homo)][df['Method']=='HETO']['Cost'].tolist()
Cost_VMC = df[df['Tag'].isin(homo)][df['Method']=='VMC']['Cost'].tolist()

width = 0.2

fig, ax = plt.subplots()
rects1 = ax.bar(x - width/2, Cost_HETO, width, label='HETO')
rects2 = ax.bar(x + width/2, Cost_VMC, width, label='VMC')
# 为y轴、标题和x轴等添加一些文本。
ax.set_ylabel('Cost', fontsize=16)
# ax.set_xlabel('X轴', fontsize=16)
# ax.set_title('这里是标题')
ax.set_xticks(x)
ax.set_xticklabels(XLabel)
ax.legend()

fig.tight_layout()
plt.show()
