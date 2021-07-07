#cd C:\Users\emman\OneDrive - AECFORWARD LTD\2021 - Research\2021_06_15 ColBot\ColumnScraping
#streamlit run ColBot_Streamlit_v04.py
#? how to relaunch quickly?

# Importing modules (to be limited in the future)
import streamlit as st
import numpy as np
import seaborn as sns
import pandas as pd
#import tensorflow as tf
#from tensorflow import keras
import matplotlib.pyplot as plt
from PIL import Image
import os

#get working directory
cwd = os.getcwd()
image_dir = os.path.join(cwd,"images")

#Main theme (in addition to config.toml)
img = Image.open(os.path.join(image_dir,"Favicon"+".png"))
st.set_page_config(page_title="AECforward ColBot", page_icon=img, layout='centered', initial_sidebar_state='expanded')

# User Interface
cursorLy = st.sidebar.slider("Ly        Column Buckling length (mm)", 3000, 5000, value=4000, step=20)
cursorN =  st.sidebar.slider("N      Axial Force (kN)", 0, 10000, value=5000, step=100) 
cursorMy = st.sidebar.slider("My        Major Bending Moment (kNm)", 0, 100,step=25)
cursorMz = st.sidebar.slider("Mz        Minor Bending Moment (kNm)", 0, 100,step=50)
plot_checkbox = st.sidebar.checkbox("Plot the solution in L N diagram", value=True, help="Awesome plot try it")
objectives = [ "cost", "size" , "carbon A1-A3"]
#options = st.multiselect('What are your favorite colors', objectives)
#option = st.sidebar.write(options)
#streamlit.multiselect(label, options, default=None, format_func=<class 'str'>, key=None, help=None)
#st.info("Shape_cat equals " + str(shape_cat))
objective_plot = st.sidebar.selectbox( 'Plot for:', objectives )


# Presentation
cols = st.beta_columns(2)
img = Image.open(os.path.join(image_dir,"AECforward-Bot"+".png"))
cols[0].image(img, width=  100)
cols[1].title("ColBot")
cols[1].text("Beta - by AECforward.ai")
cols[1].text("This is just a prototype")
#st.subheader("Steel Columns Predictions for size, cost or embodied carbon")

# Building case - Including scaling
case = pd.DataFrame()
case["N"] = [1000*cursorN]
case["Ly"] = [cursorLy]
case["My1"] = [1E6*cursorMy]
case["Mz1"] = [1E6*cursorMz]




#To simulate API Json
@st.cache
def loadfile():  
    df_best= pd.read_csv('Xy_class_153000_310621.csv', header=[0,1])
    df_best = df_best.droplevel(1, axis=1)
    return df_best

import ColBot_json  
df_best = loadfile()

for objective in objectives:
    case["objective"] = [objective]
    json_in = case.to_dict(orient = 'records')
    #st.text(json_in)
    json_out = ColBot_json.FakeAPI(json_in, df_best)
    row = pd.json_normalize(json_out)
    if objective == objectives[0]:
        solutions = row.copy()
    else:
        solutions = solutions.append(row)
solutions.reset_index(drop=True, inplace=True)  
#st.text(solutions)

#DISPLAY OPTIONS
st.subheader("Generative design")
st.text("The best predicted columns size with the lowest cost/size/embodied carbon A1-A3 are:")
st.text("")
cols = st.beta_columns(len(objectives))
ColumnsToDisplay = [  "Section", "grade"]
for i in range(len(objectives)):
    
    objective = solutions.loc[i, "objective"]
    #text = "Option " + str(i) + " :"
    cols[i].subheader(objective)
    #display a bar
    try:
        img = Image.open(os.path.join(image_dir,"bar_"+objective+".png"))
        cols[i].image(img, width=  200, use_column_width = False )  #use_column_width = True
    except:
        pass

    for column in ColumnsToDisplay:
        cols[i].text(solutions.loc[i,column])
    imgname = solutions.loc[i,"Section"]
    try:
        img = Image.open(os.path.join(image_dir,imgname+".png"))
        cols[i].image(img, width=  200, use_column_width = False )  #use_column_width = True
    except:
        pass



#OPTIONS BAR PLOTS
st.text("")
st.subheader("Options comparison")
st.text("The charts are comparing the cost, size and embodied carbon A1-A3 for the different options:")
#st.text("For different objective, the best predicted sections are:")
cols = st.beta_columns(len(objectives))
plt.rcParams.update({'font.size': 23})
ylabels = ["cost £/m", " size mm", "carbon  kgCo2/m"]
for i in range(len(objectives)):
    objective = objectives[i]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set(xlabel='Option', ylabel=ylabels[i])
    ax.bar(np.arange(len(solutions)),solutions[objective], label=solutions['Section'],
          color=["dodgerblue","orange","yellowgreen"]  , alpha=0.9)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.6)
    plt.show()
    cols[i].pyplot(fig)
    



#@st.cache   why is this not working????
#@st.cache(hash_funcs={dict: lambda _: None})
#st.cache(hash_funcs={lambda _: None})
def Bigplot():
    st.text("")
    st.subheader("Plot of N L diagram")
    st.text("The black lines are showing the current case: forces (N) and length (L)")

    N = case.at[0,'N']
    Ly = case.at[0,'Ly']
    My = case.at[0,'My1'] / 1E6
    Mz = case.at[0,'Mz1'] / 1E6
    listCASE = ['N', 'My1', 'Mz1', 'Ly']
    objective = objective_plot
    print(N, Ly)

    df_toplot = df_best.copy()
    #df_toplot.columns = df_toplot.columns.droplevel(1)

    print("Cases :", listCASE)
    xplot = listCASE[0]
    yplot = listCASE[3]
    
    df_toplot = df_toplot[df_toplot['My1'] == case.at[0,'My1']]
    df_toplot = df_toplot[df_toplot['Mz1'] == case.at[0,'Mz1']]
    
    _ColSuffix = "Best_"+objective+"-"
    PlotColorColumn = _ColSuffix + "Section"
    PlotMarkerColumn = _ColSuffix + "grade"

    titlePlot = "Section with lowest " + objective + "  for My=" + str("%.0f"% My) + "kNm and Mz=" + str( "%.0f"% Mz) + "kNm"
    #for better presentation of the legends:
    plt.rcParams.update({'font.size': 10})
    Sea_df = df_toplot.sort_values(PlotColorColumn, ascending = False)  
    fig, ax = plt.subplots(1,1, figsize=(10,10))
    ax.set(xlabel='N : Axial Force (N)', ylabel='L : Buckling length (mm)' ,title=titlePlot)
    sns_plot = sns.scatterplot( data=Sea_df, x=xplot, y=yplot, s=30, hue=PlotColorColumn, style=PlotMarkerColumn, palette="colorblind")
    #plt.title(PlotColorColumn)
    ax.set_xlim([0,10000000])
    ax.set_ylim([3000,5000])
    ax.axvline(N, color = "black")
    ax.axhline(Ly, color = "black")
    ax.legend(loc='upper right')
    plt.show()
    st.pyplot(fig)
    return fig

if plot_checkbox:
    
    Bigplot()

#blank lines
for i in range(0,20):
    st.write("")

if st.button("What are the assumptions?", help="If you want to know more"):
    st.text("Calcs, costs, grade, histar....")




