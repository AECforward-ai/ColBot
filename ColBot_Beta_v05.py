#cd C:\Users\emman\OneDrive - AECFORWARD LTD\2021 - Research\2021_09_20 Colbot\ColBot
#streamlit run ColBot_Beta_v05.py
#? how to relaunch quickly?

# Importing modules (to be limited in the future)
import streamlit as st
import numpy as np
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
from PIL import Image
import os
import Column_modules    #module
#import ColBot_json  
#import pickle5 as pickle
import pickle

#get working directory
cwd = os.getcwd()
image_dir = os.path.join(cwd,"images")

#Constants and file names
objectives_list = [  "weight_S355" , "cost", "size" , "carbon"]
steel_sections_file =os.path.join(cwd, 'steel_sections.xlsx')   #list of sections
parameters_file = os.path.join(cwd, 'tedds_column_parameters.xlsx')
steel_cost_file = os.path.join(cwd,'steel_cost.xlsx')
steel_yield_file = os.path.join(cwd,'steel_yield.xlsx')
steel_carbon_file= os.path.join(cwd,'steel_carbon.xlsx')
sections_list_file =  os.path.join(cwd, 'sections_list.xlsx')   #list of sections with cost carbon etc
solutions_pickle_file = os.path.join(cwd, 'Xy826k_short.pickle')

#-------------------------------------------------------------------------------------------------------
#--------------------------USER INTERFACES--------------------------------------------------------------
#-------------------------------------------------------------------------------------------------------

#Main theme (in addition to config.toml)
img = Image.open(os.path.join(image_dir,"Favicon"+".png"))
st.set_page_config(page_title="AECforward ColBot", page_icon=img, layout='centered', initial_sidebar_state='expanded')

# CASE user interface
cursorLy = st.sidebar.slider("Ly        Column Buckling length (mm)", 3000, 5000, value=4000, step=20)
cursorN =  st.sidebar.slider("N      Axial Force (kN)", 0, 10000, value=5000, step=100) 
cursorMy = st.sidebar.slider("My        Major Bending Moment (kNm)", 0, 100,step=25)
cursorMz = st.sidebar.slider("Mz        Minor Bending Moment (kNm)", 0, 100,step=25)
CASE_user = pd.DataFrame({('N',"N"): [1000*cursorN],
                         ('My1',"Nmm"): [1E6*cursorMy],
                        ('Mz1',"Nmm"): [1E6*cursorMz] ,
                          ('Ly',"mm"): [cursorLy] } )  
case = CASE_user.droplevel(1, axis=1)

objectives_checkbox = st.sidebar.checkbox("I want to specify my objectives", value=False, help="Allows to customise the options")
if objectives_checkbox: 
    
    objectives = st.sidebar.multiselect(
        'Objectives to be compared',
        objectives_list,
        objectives_list)
    st.sidebar.caption("weight_S355 is a typical baseline option in S355")
else:
    objectives = ["cost", "size" , "carbon"]
cost_checkbox = st.sidebar.checkbox("I know my steel costs", value=False, help="if you are in the trade")
if cost_checkbox:
    Basis = st.sidebar.slider("S355Jo - Baseline", 500, 2000, value=725, step=25)
    S355M_plus = st.sidebar.slider("S355M extra", 0, 200, value=75, step=5)
    S460J2_plus = st.sidebar.slider("S460J2 extra", 0, 200, value=100, step=5)
    S460M_plus = st.sidebar.slider("S460M extra", 0, 200, value=125, step=5)
    Weight_550to700 = st.sidebar.slider("Section >550kg/m extra", 0, 400, value=75, step=25)
    Weight_700to1400 = st.sidebar.slider("Section >700kg/m extra", 0, 400, value=225, step=25)
    plot_checkbox = False
else :
    plot_checkbox = st.sidebar.checkbox("Plot the force vs height diagram", value=False, help="Awesome plot try it")
    objective_plot = "carbon"
if plot_checkbox:
    objective_plot = st.sidebar.selectbox( 'Plot for:', objectives_list, index=3 )

# Presentation
cols = st.beta_columns(2)
img = Image.open(os.path.join(image_dir,"AECforward-Bot"+".png"))
cols[0].image(img, width=  100)
cols[1].title("ColBot")
cols[1].text("Beta - by AECforward.ai")

#st.subheader("Steel Columns Predictions for size, cost or embodied carbon")

#----------------------------SOLUTION CALCULATIONS------------------------------------------------------

#FILES READING functions with streamlit cache to avoid reloading
@st.cache
def ReadXls(FileName):
    _df = pd.read_excel(FileName)
    return _df
@st.cache
def ReadXlsWithHeader(FileName):
    _df = pd.read_excel(FileName, header=[0,1])
    return _df
def ReadXlsDropHeader1(FileName):
    _df = pd.read_excel(FileName, header=[0,1]).droplevel(1, axis=1)
    return _df
@st.cache
def ReadPicke(FileName):
    #_df = pd.read_pickle(FileName)
    with open(FileName, 'rb') as handle:
        _df = pickle.load(handle)
    return _df


#Running direct calcs Locally
parameters = ReadXls(parameters_file )

#4.5s / query vs 2.75s
#Full calculation is launched if special costs are entered 
if cost_checkbox:     
    df_sections = ReadXlsWithHeader(steel_sections_file )
    df_yield = ReadXls(steel_yield_file)
    #
    df_carbon = ReadXls(steel_carbon_file)
    df_cost = Column_modules.built_cost(Basis, S355M_plus,S460J2_plus,S460M_plus, Weight_550to700,Weight_700to1400)
    sections_withheader = Column_modules.Generate_Sections_List(df_sections, df_yield, df_cost, df_carbon)
    sections = sections_withheader.droplevel(1, axis=1)

    solutions_row = Column_modules.Column_optimisation(CASE_user, sections_withheader)
    solutions = Column_modules.RowToTableSolution(case, solutions_row , objectives)
    
#otherwise the "json" is used (TEMPORARY: do not call full 
else:
    sections = ReadXlsDropHeader1(sections_list_file)
    df_cost = ReadXls(steel_cost_file)              #only use for reference outputs
    df_best = ReadPicke(solutions_pickle_file)
    solutions_row = Column_modules.match(case, df_best)  
    solutions = Column_modules.RowToTableSolution(case, solutions_row , objectives)


#------------------------GENERATIVE DESIGN : DISPLAY---------------------------------------------------
#GENERATIVE DESIGN - display
st.subheader("Generative design")
st.markdown("The best predicted columns size with the lowest cost/size/embodied carbon A1-A3 are:")
st.text("")
cols = st.beta_columns(len(objectives))
ColumnsToDisplay = [  "Section", "grade"]
for i in range(len(objectives)):
    
    objective = solutions.loc[i, "objective"]
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





#---------------------------- OPTIONS BAR COMPARISON PLOTS---------------------------------------------------
st.markdown("")
st.subheader("Options comparison")
st.markdown("The charts are comparing the cost, size and embodied carbon A1-A3 for the different options:")
#st.markdown("For different objective, the best predicted sections are:")

plt.rcParams.update({'font.size': 30})
properties = [  "weight" , "cost", "size" , "carbon"]
ylabels = ["weight  kg/m", "cost  £/m", " size  mm", "carbon   kgCO2/m"]


#Add properties to the solutions
for row in range(len(solutions)):
    solution = solutions.iloc[row]
    section = sections[(sections['Section']==solution['Section'])&(sections['grade']==solution['grade'])]
    section.reset_index(drop=True, inplace=True)
    for property in properties:
        solutions.at[row, [property]]=section.at[0,property]
    #color label
    color = parameters[parameters["parameter"]==solution["objective"]]
    color.reset_index(drop=True, inplace=True)
    solutions.at[row, "color"] = color.at[0,"color"]


cols = st.beta_columns(len(properties))
for i in range(len(properties)):
    property = properties[i]
    fig = plt.figure()
    ax = fig.add_subplot(111)
    ax.set(xlabel='Option', ylabel=ylabels[i], title=property)
    ax.bar(np.arange(len(solutions)),solutions[property], label=solutions['Section'],
          color=solutions['color']  , alpha=0.9)
    ax.grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.6)
    plt.show()
    cols[i].pyplot(fig)

    



#@st.cache   why is this not working????
#@st.cache(hash_funcs={dict: lambda _: None})
#st.cache(hash_funcs={lambda _: None})
#@st.cache
def Bigplot():
    st.markdown("")
    st.subheader("Plot of N L diagram")
    st.markdown("The black lines are showing the current case: forces (N) and length (L)")

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
    
    _ColSuffix = objective+"-"
    #OLD _ColSuffix = "Best_"+objective+"-"
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
for i in range(0,3):
    st.write("")


if st.button("Questions? Comments? or want full detailed calculations?", help="If you want more"):
    st.markdown("Please email us at "+
                '<a href="mailto: bots@AECforward.ai">bots@AECforward.ai</a>'+
                " with the following reference:", unsafe_allow_html=True)
    reference = pd.DataFrame(solutions, columns=['objective', 'Section', 'grade']) 
    st.caption("ColBot/"+str(case.to_dict(orient = 'records'))+"/"
            +str(reference.to_dict(orient = 'records'))+"/"
            +str(df_cost.to_dict(orient = 'records')))


for i in range(0,10):
    st.write("")

st.caption("ColBot Beta v5. AECforward.ai own all intellectual property rights to ColBot. " +
          "This design has been generated automatically using a machine learning process and hence is approximate. "+
          "The Information provided is for Informational purposes only and should not be treated as a substitute for or replacement of professional structural engineering advice."
          )


