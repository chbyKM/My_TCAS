import pandas as pd

df1 = pd.read_csv('university.csv')
df1 = df1[['ชื่อหลักสูตร', 'university',]]
df1 = df1.rename(columns={"university": "มหาวิทยาลัย"})
df2 = pd.read_csv('assets/university_location_clean.csv')
df2 = df2.rename(columns={"ชื่อสถานศึกษา": "มหาวิทยาลัย"})

print(f"# df1 -> len = {len(df1)}, unique uni = {len(df1['มหาวิทยาลัย'].unique())}")
print(df1.head(3))
print("------------------")
print(f"# df2 -> len = {len(df2)}, unique uni = {len(df2['มหาวิทยาลัย'].unique())}")
print(df2.head(3))
print("------------------")

# df3 = pd.merge(df1, df2, on='มหาวิทยาลัย')
# print(f"# df3 -> len = {len(df3)}")
# print(df3.head(3))
uni_dict = {uni: province for uni, province in zip(df2['มหาวิทยาลัย'].tolist(), df2['จังหวัด'].tolist())}
uni_dict_keys = list(uni_dict.keys())
for i in range(len(df1)):
    if df1.loc[[i], ['มหาวิทยาลัย']].iloc[0, 0] not in uni_dict_keys:
        df1.loc[[i], ['จังหวัด']] = ""
    else:
        df1.loc[[i], ['จังหวัด']] = uni_dict[df1.loc[[i], ['มหาวิทยาลัย']].iloc[0, 0]]

print(f"# new df1 -> len = {len(df1)}, unique uni = {len(df1['มหาวิทยาลัย'].unique())}")
print(df1.head(3))
