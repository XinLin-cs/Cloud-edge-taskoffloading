import pandas as pd

df = pd.DataFrame(
    {
        '1':1,
        '2':2,
    },
    # columns=['c','d']
)
print(df)
df.to_csv('./result/test.csv')

df = pd.read_csv('./result/test.csv')
print(df)