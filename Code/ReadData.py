"""
Created on April 2021

@author: Ali Mokhtari
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime

path = '../data/'

descarteIndex = pd.read_csv(path+'descarteIndex_m50.csv',header=0)

index_del = []
for index, row in descarteIndex.iterrows():
    if row['admin_level'] != 1:       
        index_del.append(index)


descarteIndex = descarteIndex.drop(index_del, axis = 0)
caseInformation = pd.read_csv(path+'caseInformation_States.csv', header = 0)

mob = pd.DataFrame(data=None, columns = ['state', 'date', 'm50'])
#descarteIndex.to_csv('out1.csv')


for index, row in descarteIndex.iterrows():     
    date_size = row.shape[0]
    for i in range(5,date_size):
        date = list(descarteIndex)[i]
        temp_df = pd.DataFrame({'state':[row['admin1']], 'date':[date] ,
                                'm50': [row[i]]})
        mob = mob.append(temp_df, ignore_index=True)

mob['date'] = pd.to_datetime(mob['date'],format ='%Y-%m-%d')
caseInformation['date'] = pd.to_datetime(caseInformation['date'],
                                         format = '%Y-%m-%d')


cases = caseInformation.drop(['fips'], axis = 1
                             ).groupby(by=['state', 'date']).sum()
La_cases =cases.loc['Louisiana']

La_mob = mob[mob['state']=='Louisiana'].drop(['state'], axis=1)
# La_mob['last_index'] = La_mob['date'].shift(periods = +1)
# La_mob['difference'] = La_mob['date'] - La_mob['last_index']
# La_mob['difference'] = La_mob['difference'].dt.days


La_merged = pd.merge(La_mob, La_cases, on=['date'], how="inner")
La_merged = La_merged.fillna(0)



La_merged['last_index'] = La_merged['date'].shift(periods = +1)
La_merged['difference'] = La_merged['date'] - La_merged['last_index']
La_merged = La_merged.drop(['last_index'], axis=1)
La_merged['difference'] = La_merged['difference'].dt.days

La_merged = La_merged.reset_index(drop=True)
La_merged['new_cases'] = La_merged.cases - La_merged['cases'].shift(periods = 1)
La_merged.loc[0,'new_cases'] = 1
La_merged['cases_avg'] = La_merged['new_cases'].rolling(7).mean()
La_merged['m50_avg'] = La_merged['m50'].rolling(7).mean()
La_merged.loc[0,'cases_avg'] = 1


fig, ax1 = plt.subplots()

color = 'tab:red'
ax1.set_xlabel('date')
ax1.set_ylabel('number of cases', color=color)
ax1.plot(La_merged['date'] , La_merged['cases_avg'], color=color,
         linestyle='dashed')
ax1.tick_params(axis='y', labelcolor=color)
ax2 = ax1.twinx()  
color = 'tab:blue'
ax2.set_ylabel('mobility', color=color)  
ax2.plot(La_merged['date'] , La_merged['m50_avg'], color=color,
         linestyle='solid')
ax2.tick_params(axis='y', labelcolor=color)
plt.title("#of cases/mobility vs. time for Louisiana")

fig.tight_layout()  # otherwise the right y-label is slightly clipped
plt.show()
