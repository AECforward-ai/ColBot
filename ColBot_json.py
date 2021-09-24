#!/usr/bin/env python
# coding: utf-8

# In[2]:


import flask
from flask import Flask, request, jsonify
import pandas as pd
import json
from IPython.display import display

#to be done: Approximation of N,L,M if exact value not in the list
#to be done: Return all criterias rather than one?


def FakeAPI(json_in, df_best):

    df = pd.json_normalize(json_in)

    print("Json in")
    display(df) 

    #Read the objective in Json. If no objetive found, size is used per default.
    try:
        objective = df.at[0,"objective"]  
        case = df.drop(columns=['objective'])
    except:
        objective = "size"
        case = df.copy()
    #print("objective =", objective)

    #print("case: ")
    #display(case)


    #display(df_best.head(3)) 


    def match(case,df):
        _df = df.copy()

        #Filling up with zeros if values are not entered
        columns_case_df = []
        for name in df.columns.tolist():
            if 'Best' not in str(name):
                columns_case_df.append(name)
        for name in columns_case_df:
            #print(name,case.columns.tolist())
            if name not in case.columns.tolist():
                case[name]=0

        for column in case.columns:
            _df = _df[_df[column] == case.at[0,column]]
        return _df.index


    rowNo = match(case, df_best)
    display(rowNo)
    row_best = df_best.iloc[rowNo]
    display(row_best)

    _ColSuffix = "Best_"+objective+"-"
    print(_ColSuffix)

    solution = case.copy()
    solution["objective"]=objective
    for column in row_best.columns:
        if _ColSuffix in column:
            Simple_Name =  column.replace(_ColSuffix, '')
            solution[Simple_Name] = row_best[column].values

    #display(solution)

    output = solution.to_dict(orient = 'records')
    #json_out = jsonify(output)
    return output

TryLocal = False
if TryLocal:
    df_best= pd.read_csv('Xy_class_30000_290621.csv', header=[0,1])
    df_best = df_best.droplevel(1, axis=1)

    json_test = [{"N":300000,"Ly":4000,"My1":0,"Mz1":0}]
    df2 = pd.json_normalize(json_test)
    display(df2)
    print("Output = ", FakeAPI(json_test, df_best))




