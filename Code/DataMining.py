"""
Created on April 2021

@author: Ali Mokhtari
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import datetime
import csv

path = '../data/'

descarteIndex = pd.read_csv(path+'descarteIndex_m50.csv',header=0)

index_del = []
states = []
for index, row in descarteIndex.iterrows():
    if row['admin_level'] != 1:       
        index_del.append(index)
    else:
        states.append(row['admin1'])

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

##############################################################################

states_cases = cases.reset_index()
states_mob = mob
states_merged = pd.merge(states_mob, states_cases,
                         on=['state','date'], how="inner")
states_merged = states_merged.fillna(0)

states_merged['last_index'] = states_merged['date'].shift(periods = +1)
states_merged['difference'] = states_merged['date'] - states_merged['last_index'] 
states_merged = states_merged.drop(['last_index'], axis=1)
states_merged['difference'] = states_merged['difference'].dt.days
states_merged = states_merged.reset_index(drop=True)
mv_avg = 14
states_merged['new_cases'] = states_merged.cases - states_merged['cases'].shift(periods = 1)
states_merged.to_csv('newcases.csv')
states_merged['cases_avg'] = states_merged['new_cases'].rolling(mv_avg).mean()
states_merged['m50_avg'] = states_merged['m50'].rolling(mv_avg).mean()

index_begin_state = states_merged[states_merged['state'] 
                                  != states_merged['state'
                                                   ].shift(periods=1) ].index
for index in index_begin_state:
    for i in range(mv_avg):
        states_merged = states_merged.drop([i+index])

states_merged = states_merged.reset_index(drop = True)



for state in states:
   
    fig, axes = plt.subplots()
    state_date = states_merged[states_merged['state']== state]['date']
    state_cases = states_merged[states_merged['state']== state]['cases_avg']
    state_mob = states_merged[states_merged['state']== state]['m50_avg']
    
    

    color = 'tab:red'
    axes.set_xlabel('date')
    axes.set_ylabel('number of cases', color=color)
    axes.plot(state_date , state_cases, color=color,
             linestyle='dashed')
    axes.tick_params(axis='y', labelcolor=color)
    ax2 = axes.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('mobility', color=color)  
    ax2.plot(state_date , state_mob, color=color,
             linestyle='solid')
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title(state)
        
    fig.tight_layout() 
    plt.savefig('../figures/complete/'+state+'.pdf')   
    
# for ax in fig.get_axes():
#     ax.label_outer()

plt.show()
    
states_merged_slice = states_merged[states_merged['date'] < '2020-07-31']
states_merged_slice = states_merged_slice[states_merged_slice['date'] > '2020-05-01']

# states_m50_cases_slice = pd.DataFrame(data=
#                                       states_merged_slice.loc[:,
#                                                               ['state',
#                                                                 'm50_avg',
#                                                                 'cases_avg']])



sl1 = states_merged_slice[
    (states_merged_slice['date'] > '2020-05-01' ) &
    (states_merged_slice['date'] < '2020-06-01')]
sl1 = sl1.drop(['m50', 'cases', 'deaths','new_cases', 'difference'], axis = 1)

sl1 = sl1.reset_index(drop=True)

temp_df = states_merged_slice[
    (states_merged_slice['date'] > '2020-07-01' ) &
    (states_merged_slice['date'] < '2020-07-31')].reset_index(drop=True)
temp_df = temp_df.drop(['m50', 'cases','deaths','new_cases','difference',
                        'm50_avg'], axis = 1)
temp_df = temp_df.reset_index(drop=True)

states_m50_cases_slice = pd.DataFrame(data={'state':sl1['state'],
                                            'm50_avg': sl1['m50_avg'], 
                                            'cases_avg':temp_df['cases_avg'] })





for state in states:

    fig, axes = plt.subplots()
    state_date = states_merged_slice[states_merged_slice['state']== state]['date']
    state_cases = states_merged_slice[states_merged_slice['state']== state]['cases_avg']
    state_mob = states_merged_slice[states_merged_slice['state']== state]['m50_avg']
    
    

    color = 'tab:red'
    axes.set_xlabel('date')
    axes.set_ylabel('number of cases', color=color)
    axes.plot(state_date , state_cases, color=color,
             linestyle='dashed')
    axes.tick_params(axis='y', labelcolor=color)
    ax2 = axes.twinx()  
    color = 'tab:blue'
    ax2.set_ylabel('mobility', color=color)  
    ax2.plot(state_date , state_mob, color=color,
             linestyle='solid')
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title(state + " (sliced)")
        
    fig.tight_layout() 
    fig.autofmt_xdate()
    plt.savefig('../figures/sliced/'+state+'.pdf')   
    
# for ax in fig.get_axes():
#     ax.label_outer()

plt.show()

count =0
with open('corr.csv','w', newline='') as csvfile:
    writer = csv.writer(csvfile, delimiter=',')    
    
    for state in states: 
        if state !='Washington, D.C.':
            print("\n\nState: " + state)
            correlation  = states_m50_cases_slice[
                states_m50_cases_slice['state']==state].corr(
                    method = 'pearson').loc['m50_avg', 'cases_avg']
                
            writer.writerow([state, correlation])        
            print(correlation)
            if abs(correlation) > 0.75 :
                count +=1

print('count = '+ str(count))

