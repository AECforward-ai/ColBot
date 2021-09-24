import pandas as pd
import Column_Detailed_calculation as detailed_calc
from IPython.display import display

#this module is used for:
# - Column_optimisation(CASE_user, arg_sections):: Find column with lower utilisation from a load case and section list
#- Generate_Sections_List(df_sections, df_yield, df_cost, df_carbon): Generate a long section list with cost, carbon, weight, yield
#- def built_cost(Basis, S355M_plus,S460J2_plus,S460M_plus, Weight_550to700,Weight_700to1400   ): Return a new cost df

### ---------------------------------------FUNCTIONS FOR COLUMNS OPTIMISATION
##-------------------------------------------------------------------------------------
#creating list of objectives
def ListParam(Paramdf, ParamCol, ValueCol, ListValues):
    _listParam = []
    for value in ListValues:
        _listParam_df = Paramdf[(Paramdf[ValueCol] == value)].copy()
        _listParam.extend(_listParam_df[ParamCol].values)
    return _listParam


#Replace values of Input df with values in This df
def FillDfWithThis(varInputDf, varThisDf):
    _df = varInputDf.copy()
    _ThisDf = varThisDf
    for column in varThisDf.columns:
        if len(varInputDf)==len(varThisDf):
            _df[column]= _ThisDf[column]
        if len(varThisDf)==1:            
            _df[column]= _ThisDf.loc[0,column]
    return _df

#Launch calculations "CalcObject" for Case_df on all rows of Var_df,
def CalcsCaseVar(Case_df, Var_df, CalcObject, NamePredCol):
    _df = Var_df.copy()    
    _df0 = _df.copy()
    Case_df.reset_index(drop=True, inplace=True)
    Var_df.reset_index(drop=True, inplace=True)
    
    for row in range(len(Case_df)):
        row_CASE = pd.DataFrame(Case_df, index=[row])
        _dfrow = FillDfWithThis(_df0, row_CASE)
        if row==0:
            _df=_dfrow
        else:
            _df = _df.append(_dfrow)
    
    for row in  range(len(_df)):
        row_CASE = pd.DataFrame(_df, index=[row])
        _calcs_case = CalcObject.ColumnUtilisation(row_CASE)
        _calcs_case.calcs()
        _df.loc[row, (NamePredCol, "NA")] = _calcs_case.utilisation
    return _df


#Basic optimisation looking for the minimum by calculating all values
def OptimisationBrute(varCASE, varVAR, model, varListVAR, varListOBJ, NameColCalc):
    _OptiDf = varCASE.copy()
    for row in range(len(varCASE)):
        row_CASE = pd.DataFrame(varCASE, index=[row])
        _dfML = CalcsCaseVar(row_CASE , varVAR, model, NameColCalc)  #calculate utilisation
        _dfML = _dfML[_dfML[(NameColCalc,"NA")]<=1].copy()
        _dfML.columns = _dfML.columns.droplevel(1)
        for objectif in varListOBJ:
            if len(_dfML)!=0:
                    _minIndex = _dfML[objectif].idxmin()           #minimum utilisation
            _ColSuffix = objectif+"-"  #"Best_"+
            for variable in varListVAR:
                _colname=_ColSuffix+variable
                if len(_dfML)!=0:
                    _OptiDf.loc[row,_colname] = _dfML.loc[_minIndex,variable]
                else:
                    _OptiDf.loc[row,_colname] = "NaN"
            if len(_dfML)!=0:
                _OptiDf.loc[row,_ColSuffix+NameColCalc] = _dfML.loc[_minIndex,NameColCalc]
    _OptiDf.columns = _OptiDf.columns.droplevel(1)
    return _OptiDf



#To be called-------------------------------------------------------
#Look for best column depending on load case and list of sections
def Column_optimisation(CASE_user, arg_sections):
    verbose = True
    #read long sections lists with cost carbon 

    sections = arg_sections
    
    #loading list of parameters
    df_parameters = pd.read_excel('tedds_column_parameters.xlsx')
    if verbose: display(df_parameters.head(3))
    
    #list objectives
    listOBJ= ListParam(df_parameters, "parameter", "opti", ["OBJ"])
    if verbose: print("List of objectives: listOBJ", listOBJ)

    #List of Variables
    listVAR = ListParam(df_parameters, "parameter", "opti", ["VAR"])
    if verbose: print("List of variables: listVAR", listVAR)
    
    #test calculation
    if verbose: 
        print("Test Calculation")
        Calc_Case_user = CalcsCaseVar(CASE_user, sections, detailed_calc, "Umax")
        display(Calc_Case_user.tail(10))

    #optimisation
    if verbose: print("List of best variables for each objectives for one case")
    Optimisation_df = OptimisationBrute(CASE_user, sections,  detailed_calc ,listVAR,listOBJ, "Umax")
    
    return Optimisation_df



#CONSOLE EXAMPLE1
print("-----------------------module OPTIMISATION FOR ONE LOAD CASE--------------")
sections = pd.read_excel('sections_list.xlsx', header=[0,1])
print(sections.head(3))
    
CASE_user = pd.DataFrame({('N',"N"): [6600000], ('My1',"Nmm"): [0] , ('Mz1',"Nmm"): [0] ,
                          ('Ly',"mm"): [3000] } )
#CASE_user2 = pd.DataFrame({('N',"N"): [5100000, 22000000], ('My1',"Nmm"): [50000000,0] , ('Mz1',"Nmm"): [5000000,0],
#                          ('Ly',"mm"): [3000,6000], ('Lz',"mm"): [3750,4500],  ('Vy',"N"): [50000,0] } )
print(CASE_user)    
Optimisation_df = Column_optimisation(CASE_user, sections)
print(Optimisation_df)
    

#---------------------------------------------------------------------------------------
#-------------GENERATE FULL LIST OF COLUMN SECTIONS WITH PROPERTIES----------------------

def Generate_Sections_List(df_sections, df_yield, df_cost, df_carbon):
    verbose = False
    
    if verbose:
        print("Section List")
        display(df_sections.head(3), df_sections.tail(2))
        print("Steel yield")
        display(df_yield)
        print("Steel cost")
        display(df_cost)
        print("Steel embodied carbon")
        display(df_carbon)
    
    All_grades = df_yield["grade"].copy()
    sections_list = df_sections.copy() 
    sections_list["grade"]=All_grades[0]
    sections_list[("fy","MPa")]=0
    sections_list[("fyPa","Pa")]=0
    sections_list[("cost","pounds/m")]=0
    sections_list[("carbon","kg/m")]=0

    #Generate a long list of the sections and associated different steel grades
    _temp = sections_list.copy()
    for grade in All_grades[1:]:
        _df=_temp.copy()
        _df["grade"]=grade
        sections_list=pd.concat([sections_list,_df],axis=0)

    sections_list.reset_index(drop=True, inplace=True)
    if verbose: display(sections_list.head(5))


    #Filling the long list of sections with the correct, yield, cost and carbon

    for i in range(len(sections_list)):
        _grade=sections_list.at[i,("grade","")]
        _thickness=sections_list.at[i,("tf","mm")]
        _weightperm=sections_list.at[i,("weight","kg/m")]

        #setting the correct yield strength
        _ThisYield=df_yield[df_yield['grade']==_grade]
        for j in range(1,_ThisYield.shape[1]):
            if _thickness <= _ThisYield.columns[j]:
                sections_list.at[i,("fy","MPa")] = _ThisYield.iloc[0,j]
                sections_list.at[i,("fyPa","Pa")] = _ThisYield.iloc[0,j]*1000000
                break

        #setting the correct cost / m
        _ThisCost=df_cost[df_cost['grade']==_grade]
        for j in range(1,_ThisCost.shape[1]):
            if _weightperm <= _ThisCost.columns[j]:
                sections_list.at[i,("cost","pounds/m")] = _ThisCost.iloc[0,j] * _weightperm * 0.001    #cost per/t x weight/m of section
                break

        #setting the correct carbon / m
        _ThisCarbon=df_carbon[df_carbon['grade']==_grade]
        sections_list.at[i,("carbon","kg/m")] = _ThisCarbon.iloc[0,1] * _weightperm * 0.001    #kg carbon / m of section

        #Calculate basic Nmax = Nrd section capacity related to A x fy
        sections_list[("Nmax","N")]=sections_list[("A","mm2")]*sections_list[("fy","MPa")]
        sections_list[("Nmin","N")]=sections_list[("Nmax","N")]*0.3                                  #PARAM: Nmin=30% of Nmax. to be validated

        #Calculating Elastic Bending Resistance W x fy
        sections_list[("MyRd","Nmm")]=sections_list[("Wely","mm3")]*sections_list[("fy","MPa")]
        sections_list[("MzRd","Nmm")]=sections_list[("Welz","mm3")]*sections_list[("fy","MPa")]

        #Adding weight S355 only !!!SPECIFIC!!!
        sections_list.at[i,("weight_S355","kg/m")] = sections_list.at[i,("weight","kg/m")]
        if "S460" in sections_list.at[i,("grade","")]:
            sections_list.at[i,("weight_S355","kg/m")] = 9999

    #Removing lines where histar not availables
    RowsToRemove = []
    for i in range(len(sections_list)):
        _grade =           sections_list.at[i,("grade","")]
        _HistarAvailable = sections_list.at[i,("Histar","NA")]
        if "Histar" in _grade:      #test if substring in string
            if _HistarAvailable == "NO":
                RowsToRemove.extend([i])
    print("Removing sections for which histar is not available:", RowsToRemove)            
    sections_list.drop(RowsToRemove,0,inplace=True)
    sections_list.reset_index(drop=True, inplace=True)
    
    if verbose: display(sections_list.head(5))
        
    return sections_list;


print("-----------------------module SECTION LIST WITH ALL PROPERTIES--------------")
df_sections = pd.read_excel('steel_sections.xlsx', header=[0,1])
df_yield = pd.read_excel('steel_yield.xlsx')
df_cost = pd.read_excel('steel_cost.xlsx')
df_carbon = pd.read_excel('steel_carbon.xlsx')
sections = Generate_Sections_List(df_sections, df_yield, df_cost, df_carbon)
print(sections)



#------------------------------------------------------------------------------
#---------------------BUILD NEW STEEL COST MATRIX------------------------------

def built_cost(Basis, S355M_plus,S460J2_plus,S460M_plus, Weight_550to700,Weight_700to1400   ):
    data = [{'grade': "S355J0 - BOF", 551: Basis},
            {'grade': "S355Histar - EAF", 551: Basis+S355M_plus},
            {'grade': "S460J2 - BOF", 551: Basis+S460J2_plus},
            {'grade': "S460Histar - EAF", 551: Basis+S460M_plus}]
    cost = pd.DataFrame(data)
    cost[700]=cost[551]+Weight_550to700
    cost[1400]=cost[551]+Weight_700to1400
    return cost

print("-----------------------module NEW COST MATRIX--------------")
#Console example
Basis = 725
S355M_plus = 75
S460J2_plus = 100
S460M_plus = 125
Weight_550to700 = 75
Weight_700to1400 = 225

cost = built_cost(Basis, S355M_plus,S460J2_plus,S460M_plus, Weight_550to700,Weight_700to1400   )
print(cost)

#--------------------------------------------------------------------------------
#---------------------LOOK UP  FOR A CASE IN PREGENERATED LIST OF SOLUTION-------

def match(case,df):
        _df = df.copy()
        #Filling up with zeros if values are not entered
        columns_case_df = []
        for name in df.columns.tolist():
            if '-' not in str(name):
                columns_case_df.append(name)
        for name in columns_case_df:
            #print(name,case.columns.tolist())
            if name not in case.columns.tolist():
                case[name]=0

        for column in case.columns:
            _df = _df[_df[column] == case.at[0,column]]
        return _df

#TRY IT
print("-----------------------module MATCH CASE IN DF-------------")
file = 'Xy826k_short.pickle'
df_best = pd.read_pickle(file )
CASE_user = pd.DataFrame({('N',"N"): [6600000], ('My1',"Nmm"): [0] , ('Mz1',"Nmm"): [0] ,
                             ('Ly',"mm"): [3000] } ) 
case = CASE_user.droplevel(1, axis=1)
print("---------------------LOOKUP---------")
solution_onerow = match(case, df_best)
display(solution_onerow)

#--------------------------------------------------------------------------------
#---------------------TRANSFORM A ROW OF AN OPTIMISED SOLUTION INTO A TABLE-------


def RowToTableSolution(case, row_best , objectives):
    row0 = case.copy()
    for objective in objectives:
        row=row0
        row["objective"]=objective
        _ColSuffix = objective+"-"
        for column in row_best.columns:
            if _ColSuffix in column:
                Simple_Name =  column.replace(_ColSuffix, '')
                row[Simple_Name] = row_best[column].values
        if objective == objectives[0]:
            solutions = row.copy()
        else:
            solutions = solutions.append(row)
    solutions.reset_index(drop=True, inplace=True)
    return solutions
            

print("----------------------------RowToTableSolution")            
objectives_list = [  "weight_S355" , "cost", "size" , "carbon"]
solutions = RowToTableSolution(case, solution_onerow , objectives_list)
display(solutions)