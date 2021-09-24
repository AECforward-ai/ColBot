#!/usr/bin/env python
# coding: utf-8

# ## Detailed Column Calculations - v01 
# 
# 
# 
# 17/06/21
# 
# !!! Mistake Tedds choice of buckling curves to be fixed
# 
# UC / UB
# 
# Only Class 1?
# 
# No S420
# # #Simple moment distribution: Linear
# # #Simplied assumptions for Lateral torsional buckling Lcr_lt=Lz hence KLT=1.0
# # Moments on columns; Less conservative to assume Mbot=Mtop. Use as default. More realistic for column in simple building (moment +/- on each column)
# # need IT IT warping and torsional constants
# "Using Method 2 of Annex B"  kzy   #Formula differente from EUROCODE?
 # Calculation in Tedds for class 3 web is using ψw = 2*N/A*fy-1 . Replaced by stress calcs
 #Buckling curves table6.2: for h/n>1.2  (tf <= 100) not satistfied with UC1299. Assume tf<150???
 

# In[22]:
class ColumnUtilisation:
    def __init__(self,case):
        self.case=case
        self.text="NA"
        self.summary="NA"
        self.utilisation = 9999

    def calcs(self):                           #Method in the class
        case = self.case
        #print("case:", case)
        self.text="Column ok"

        import math
        pi = math.pi
        sqrt = math.sqrt
        CalcNotOK = False    #will return True if any sub calc not OK
        verbose = False #Will print all the lines
        CalcNotValid = False   #Will return True if calculation assumptions are not valid (e.g. shear too high)

        # In[23]:
        AllText=""
        Summary=""
        # This is a p function which p if verbose=True and append all the lines of text together
        def p(*args, InSummary = False):
            nonlocal AllText
            nonlocal verbose
            nonlocal Summary
            Line = ""
            for string in args:
                Line += str(string) + " "    
            if verbose:
                print(Line)
            AllText+= "\n" + Line
            if InSummary:
                Summary += "\n" + Line
        
            return Line

        def p_title(arg):
            nonlocal AllText
            nonlocal verbose
            Line="------------------------------------------------------" + "\n" +arg + "\n"
            AllText+= "\n" + Line
            if verbose:
                print(Line)

        p("Column detailed calculations - Beta v01 - To be reviewed by Structural Engineer - Not for design", InSummary=True)


        # ## INPUTS
        # ### Manual input
        # In[24]:

        ManualInput = False
        if ManualInput == True :
            Section = "UC356x368x202"
            h = 374.6 #mm Section Depth
            b = 374.7 #mm Section Breath
            tf = 27 #mm Flange thickness
            tw = 16.5 #mm Web thickness
            r = 15.2 #mm Root radius
            A = 25722 #mm2 Area of section
            Wely = 3537717 #mm3 Elastic section modulus about y-axis
            Welz = 1264394 #mm3 Elastic section modulus about z-axis
            Wply= 3971739 #mm3 Plastic section modulus about y-axis
            Wplz= 1919530 #mm3 Plastic section modulus about z-axis
            Iy = 662614418 #mm4 Inertia - Second moment of area about y-axis
            Iz = 236884133 #mm4 Inertia z = Second mometn of area about z-azis
            Iw= 7.16E12 #mm6       Warping constant
            IT= 558.0E4 #mm4       torsional constant

            fy = 440 #N/mm2 #Yield strength


            ### Column geometry and loads
            Ly = 4000 #mm Buckling length for flexural buckling - Major axis
            Lz = 3750 #mm Buckling length for flexural buckling - Minor axis   
            Lcr_LT = Lz  #mm Simplied assumptions for Lateral torsional buckling Lcr_lt=Lz hence KLT=1.0

            N = 10000000 #N Axial load +Compression
            My1 = 25000000 #Nmm  #Major axis moment at end 1 - Bottom
            My2 = -My1 #Nmm Major axis moment at end 2 - Top

            Mz1 = 15000000  # Nmm Minor axis moment at end 1 - Bottom
            Mz2 = -Mz1 #Nm Minor axis moment at end 2 - Top
            Vy = 75000 #N Major axis shear force
            Vz = 35000 #N Minor axis shear force


        # ### Reading data from a file
        # In[25]:
        #note:Could be simplified using a dictionary. However calcs would not be as clear; i["h"] rather than h.

        fromfile = False   #only if inputs has to be read from xls
        UsingdfInputs = True

        if UsingdfInputs:
            if fromfile:
                import pandas as pd
                from IPython.display import display
                pd.set_option("display.max_columns", None)
                _df = pd.read_excel("df_CASE_user.xlsx", header=[0,1])       
            else:
                _df = self.case
            if verbose:
                print(_df)

            _df.reset_index(drop=True, inplace=True)
            try:
                #Column properties
                Section = _df.at[0,("Section","NA")]        
                h = _df.at[0,("h","mm")]
                b = _df.at[0,("b","mm")]
                tf = _df.at[0,("tf","mm")]
                tw = _df.at[0,("tw","mm")]
                r = _df.at[0,("r","mm")]
                A = _df.at[0,("A","mm2")]
                Wely = _df.at[0,("Wely","mm3")]
                Welz = _df.at[0,("Welz","mm3")]
                Wply = _df.at[0,("Wply","mm3")]
                Wplz = _df.at[0,("Wplz","mm3")]
                Iy = _df.at[0,("Iy","mm4")]
                Iz = _df.at[0,("Iz","mm4")]
                Iw = _df.at[0,("Iw","mm6")]
                IT = _df.at[0,("IT","mm4")]       
                #yield
                fy = _df.at[0,("fy","MPa")]
                p("Dataframe inputs : OK")
            except:
                p("FAIL - Could not get the properties")
                CalcNotValid = True
                pass            

            try:
                N = _df.at[0,("N","N")]
                My1 = _df.at[0,("My1","Nmm")]
                Ly = _df.at[0,("Ly","mm")]
                My2 = -My1
            except:
                p("FAIL - N My1 Ly are required")
                CalcNotValid = True
                pass
 
            try: 
                Lz = _df.at[0,("Lz","mm")]
                Lcr_LT = Lz
                test = 1 /Lz
            except:
                Lz = Ly
                Lcr_LT = Lz
                p("Lz=Ly assumed as no Lz given")
                
            try:
                Mz1 = _df.at[0,("Mz1","Nmm")]
                Mz2 = -Mz1
            except:
                p("Mz=0 assumed as no Mz given")
                Mz1 = 0
                Mz2 = 0
                pass

            try:
                Vy = _df.at[0,("Vy","N")]
                Vz = _df.at[0,("Vz","N")]
            except:
                p("V=0 assumed as no V given")
                Vy = 0
                Vz = 0
                pass

        
    


        # In[26]:


        p_title("Section")
        p("Section = ", Section, InSummary=True)
        p("fy =", fy  ,"MPa   Yield strength", InSummary=True)
        p("h =", h,"mm    Section Depth")
        p("b =", b,"mm    Section Breath")
        p("tf =", tf,"mm    Flange thickness")
        p("tw =", tw ,"mm    Web thickness")
        p("r =", r  ,"mm    Root radius")
        p("A =", A  ,"mm2    Area of section")
        p("Wely =", Wely  ,"mm3    Elastic section modulus about y-axis")
        p("Welz =", Welz  ,"mm3    Elastic section modulus about z-axis")
        p("Wply =", Wply  ,"mm3    Plastic section modulus about y-axis")
        p("Wplz =", Wplz  ,"mm3    Plastic section modulus about z-axis")
        p("Iy =", Iy  ,"mm4    Inertia - Second moment of area about y-axis")
        p("Iz =", Iz  ,"mm4    Inertia - Second moment of area about z-axis")
        p("Iw =", Iw  ,"mm6    warping constant")
        p("IT =", IT  ,"mm4    torsional constant")

        p_title("Geometry and Forces")
        p("Ly =", "%.0f"% Ly  ,"mm    Buckling length for flexural buckling - Major axis",  InSummary=True)
        p("Lz =", "%.0f"% Lz  ,"mm    Buckling length for flexural buckling - Minor axis ",  InSummary=True)
        p("Lcr_LT =", "%.0f"% Lcr_LT  ,"mm    Simplied assumptions for Lateral torsional buckling Lcr_lt=Lz")
        p("N =", "%.0f"% N  ,"N    Axial load +Compression", InSummary=True)
        p("My1 =", "%.0f"% My1  ,"Nmm    Major axis moment at end 1 - Bottom", InSummary=True)
        p("My2 =", "%.0f"% My2  ,"Nmm    Major axis moment at end 2 - Top")
        p("Mz1 =", "%.0f"% Mz1  ,"Nmm    Minor axis moment at end 1 - Bottom", InSummary=True)
        p("Mz2 =", "%.0f"% Mz2  ,"Nmm    Minor axis moment at end 2 - Top")
        p("Vy =", "%.0f"% Vy  ,"N    Major axis shear force", InSummary=True)
        p("Vz =", "%.0f"% Vz  ,"N    Minor axis shear force")


        # #### constants

        # In[27]:


        #Partial factors - Section 6.1
        γM0 = 1 #Resistance of cross-sections;
        γM1 = 1  #Resistance of members to instability;
        γM2 = 1.1  #Resistance of cross-sections in tension to fracture;

        E = 210000 # N/mm2   #Modulus of elasticity
        ν = 0.3   #Poisson’s ratio
        G = E / (2*(1 + ν))   
        p("G = ","%.0f" %G," MPa     Shear modulus")


        # ### HAND MODIFICATIONS !!

        # In[28]:
#       fy = 460 #N/mm2 #Yield strength


        # ## CALCULATIONS

        # ### Section classification

        # #### Web section classification (Table 5.2)

        # In[29]:
        p_title("Section classification")
        p("Web section classification (Table 5.2)")

        #Coefficient depending on fy;
        ϵ = math.sqrt(235 / fy) 
        p("ϵ=","%.2f"%ϵ)

        cw = h - 2 * (tf + r) 
        p("cw = ","%.1f"%cw," mm  Depth between fillets ")

        ratiow = cw / tw  #Ratio of c/t;
        p("c/t = ","%.1f"%ratiow, "  ratio")

        lw = min(N / (fy * tw), cw)
        p("lw = ","%.1f"% lw," mm  Length of web taken by axial load ")


        α = (cw/2 + lw/2) / cw
        p("α = ","%.1f"% α, " Ration for class 1 & 2 proportion in compression")

        #Class 3 webs
        #ψw = 2*N / (A*fy) - 1   # Calculation in Tedds for class 3 web is using ψw = 2*N/A*fy-1 . Replaced but stress calcs
        MaxMy = max(abs(My1), abs(My2))
        StressTop = +N/A + MaxMy/Wely
        StressBot = +N/A - MaxMy/Wely
        if StressTop != 0 :
            ψw = StressBot / StressTop
        else:
            ψw = 0              #not very clear how to deal with this
        p("Stress top = ", "%.1f"% StressTop, " MPa")
        p("Stress bottom = ", "%.1f"% StressBot, " MPa")
        p("ψw = ","%.1f"% ψw, " Stress Ratio for class 3 sections")

        Limit1w=0
        Limit2w=0
        Limit3w=0
        if α>0.5 :  
            Limit1w = (396 * ϵ) / (13 * α - 1)
            Limit2w = (456 * ϵ) / (13 * α - 1)
        if α<=0.5 :
            Limit1w = (36 * ϵ) / α
            Limit2w = (41.5 * ϵ) / α
    
        if ψw > -1:
            Limit3w = (42*ϵ) / (0.67 + 0.33*ψw)
        if ψw <= -1:
            Limit3w = (62*ϵ) * (1 - ψw) * sqrt(-ψw)    
    
        p("c/t=","%.1f"%ratiow)
        p("Limit for class 1 web; c/t<","%.1f"% Limit1w)
        p("Limit for class 2 web; c/t<","%.1f"% Limit2w)
        p("Limit for class 3 web; c/t<","%.1f"% Limit3w)


        classweb = 4
        if ratiow <= Limit1w:
            classweb = 1
        elif ratiow <= Limit2w:
            classweb = 2
        elif ratiow <= Limit3w:
            classweb = 3
        elif ratiow > Limit3w:
            classweb = 4
            CalcNotValid = True
            p("Web is class 4: Calculations not valid", InSummary= True)
    
        p("Webclass =", classweb )




        # #### Flange section classification (Table 5.2)

        # In[30]:


        cf = (b - tw)/2 - r
        p("Outstand length =",cf,"mm" )

        ratiof = cf / tf
        p("Ratio of c/t = ", "%.2f"% ratiof)

        p("Conservatively assume uniform compression in flange")
        Limit1f = 9 * ϵ 
        p("Limit for class 1 flange c/t<","%.1f"% Limit1f)
        Limit2f = 10 * ϵ 
        p("Limit for class 2 flange c/t<","%.1f"% Limit2f)
        Limit3f = 14 * ϵ
        p("Limit for class 3 flange c/t<","%.1f"% Limit3f)

        flangeclass1 = ratiof < Limit1f
        p("Is the flange class1:", flangeclass1 )

        classflange = 4
        if ratiof < Limit1f:
            classflange = 1
        elif ratiof < Limit2f:
            classflange = 2
        elif ratiof < Limit3f:
            classflange = 3  
    
        p("Flange class =", classflange )

        p("")
        classSection = max(classweb, classflange)
        p("The section class =", classSection)    


        # ## Resistance of cross section (cl. 6.2)

        # #### Shear - Major axis (cl. 6.2.6)

        # In[31]:


        p_title("Resistance of cross section")
        p("Vy=",Vy,"N    Design shear force" )

        Avy = max((h - 2*tf) * tw, A - 2 * b * tf + (tw + 2 * r) * tf)
        p("Avy = ","%.1f"%Avy, "mm2    Shear area ")

        VplyRd = Avy * (fy / math.sqrt(3)) / γM0
        p("VplyRd = " + "%.1f"% VplyRd + "N    Plastic shear resistance")

        Vratio = Vy / VplyRd
        p("Vy / VplyRd =", "%.3f"% Vratio)

        Vok = Vratio <1
        p("Shear resistance exceeds the design shear force:", Vok)

        Vokreduced = (Vy <= 0.5*VplyRd)
        p("No reduction in fy required for bending/axial force:", Vokreduced)

        if (not Vok) or (not Vokreduced):
            CalcNotValid = True
            p("CALC NOT VALID")


        # #### Shear - Minor axis (cl. 6.2.6)

        # In[32]:


        p("Vz = ",Vz,"N    Design shear force: ")

        Avz = 2 * b * tf - (tw + 2 * r) * tf
        p("Avz =  ","%.1f"%Avz, "mm2    Shear area (minor)")

        VplzRd = Avz * (fy / math.sqrt(3)) / γM0
        p("VplzRd = " + "%.1f"% VplzRd + "N    Plastic shear resistance ")

        Vratioz = Vz / VplzRd
        p("Vz / VplzRd =", "%.3f"% Vratioz)

        Vokz = Vratioz <1
        p("Shear resistance exceeds the design shear force:", Vokz)

        Vokreducedz = (Vz <= 0.5*VplzRd)
        p("No reduction in fy required for bending/axial force:", Vokreducedz)

        if (not Vokz) or (not Vokreducedz):
            CalcNotValid = True
            p("CALC NOT VALID")


        # #### Compression (cl. 6.2.4)

        # In[12]:


        p("N =", N, "N    Design force")

        NcRd = NplRd = A * fy / γM0 
        p("For class 1, 2, 3")
        p("NcRd = NplRd =",  "%.1f"% NcRd, " N   Design resistance")
        n = N_NcRd = N / NcRd
        p("n = N / NcRd =",  "%.3f"% N_NcRd, InSummary=True)
      
        N_NcRd_ok = N_NcRd <1
        if N_NcRd_ok:
              p("OK - The compression design resistance exceeds the design force")
        else:
            CalcNotOK = True
            p("NOT OK") 
      


        # #### Bending - Major axis (cl. 6.2.5)

        # In[13]:


        MyEd = max(abs(My1), abs(My2))
        p("MyEd=", "%.1f"% MyEd," N   Design bending moment")

        p("The section is class = ", classSection)
        Wy=0
        if classSection<=2:
            Wy = Wply
            p("Wy = Wply = ", "%.1f"% Wply, "mm3   Section modulus")
        elif classSection==3: 
            p("Wy = Wely = ", "%.1f"% Wely, "mm3   Section modulus")    
            Wy = Wely
        else:
            CalcNotValid = True
            p("CALC NOT VALID")    

        McyRd = Wy * fy / γM0
        p("McyRd = ","%.1f"% McyRd , "Nmm    Design resistance", InSummary=True)
      
        MyEd_McyRd = MyEd / McyRd
        p("MyEd / McyRd = ", "%.3f"% MyEd_McyRd)      
      
        MyEd_McyRd_ok = MyEd_McyRd <1
        if MyEd_McyRd_ok:
              p("OK - The bending design resistance (y) exceeds the design moment")
        else:
            CalcNotOK = True
            p("NOT OK")      


        # #### Bending - Minor axis(cl. 6.2.5)

        # In[14]:


        MzEd = max(abs(Mz1), abs(Mz2))
        p("MzEd=", "%.1f"% MzEd," N   Design bending moment")
        p("Wplz=", "%.1f"% Wplz, "mm3   Section modulus")

        p("The section is class = ", classSection)
        Wz=0
        if classSection<=2:
            Wz = Wplz
            p("Wz = Wplz = ", "%.1f"% Wplz, "mm3   Section modulus")
        elif classSection==3: 
            p("Wz = Welz = ", "%.1f"% Welz, "mm3   Section modulus")    
            Wz = Welz
        else:
            CalcNotValid = True
            p("CALC NOT VALID")    
    
        MczRd = Wz * fy / γM0
        p("MczRd = ","%.1f"% MczRd , "Nmm    Design resistance", InSummary=True)
      
        MzEd_MczRd = MzEd / MczRd
        p("MzEd / MczRd = ", "%.3f"% MzEd_MczRd)      
      
        MzEd_MczRd_ok = MzEd_MczRd <1
        if MzEd_MczRd_ok:
              p("OK - The bending design resistance (z) exceeds the design moment")
        else:
            CalcNotOK = True
            p("NOT OK")   


        # ### Combined bending and axial force (cl. 6.2.9)
        # 

        # In[15]:


        p_title("Combined bending and axial force")


        n = abs(N) / NplRd
        p("n=", "%.3f"% n , "    Ratio design axial to design plastic resistance")

        a = min(0.5, (A - 2 * b * tf) / A)
        p("a=", "%.3f"% a , "    Ratio web area to gross area")


        # #### Bending and Axial force - Class 1 and 2 (cl. 6.2.9.1)
        # Class 1 and 2 cross sections.
        # 
        # Where an axial force is present an allowance should be made for its effects on the plastic moment resistance

        # In[16]:




        if classSection==1 or classSection==2:
    
            p("The Section class is 1 or 2: EC clause 6.2.9.1")
    
            p("MyEd=", "%.1f"% MyEd, "Nm     Design bending moment")
    
            MplyRd = Wply * fy / γM0
            p("MplyRd = ","%.0f"% MplyRd , "Nmm    Plastic design resistance") 

            MNyRd = MplyRd * min(1, (1 - n) / (1 - 0.5 * a))
            p("MNyRd = ", "%.0f"% MNyRd, "Nmm Modified design resistance")    

            if MNyRd != 0:
                MyEd_MNyRd = MyEd / MNyRd
            else: 
                MyEd_MNyRd = 999
            p("MyEd/MNyRd", "%.2f"% MyEd_MNyRd)

            MyEd_MNyRd_ok = (MyEd_MNyRd <1 ) and (MyEd_MNyRd >=0)
            if MyEd_MNyRd_ok:
                  p("OK - Bending resistance (major) in presence of axial load exceeds design moment")
            else:
                CalcNotOK = True
                p("NOT OK")  


            p("MzEd=", "%.1f"% MzEd, "Nm     Design bending moment")

            MplzRd = Wplz * fy / γM0
            p("MplzRd = ","%.0f"% MplzRd , "Nmm    Plastic design resistance") 

            if n>a:
                MNzRd = MplzRd * (1 - ((n - a) / (1 - a))**2)
                p("n>a")
            else:
                MNzRd = MplzRd
                p("n<a")
            p("MNzRd = ", "%.0f"% MNzRd, "Nmm Modified design resistance")    

            if MNyRd !=0:
                MzEd_MNzRd = MzEd / MNzRd
            else:
                MzEd_MNzRd = 999
            p("MzEd/MNzRd", "%.3f"% MzEd_MNzRd)

            MzEd_MNzRd_ok = (MzEd_MNzRd <1 and MzEd_MNzRd >=0)
            if MzEd_MNzRd_ok:
                  p("OK - Bending resistance (minor) in presence of axial load exceeds design moment")
            else:
                CalcNotOK = True
                p("NOT OK")
    
            p("BiAxial Bending")
            p("For I and H sections:")
            α = 2.00
            p("α = ", "%.2f"% α )
            β = max(1, 5 * n) 
            p("β = ", "%.2f"% β)

            if (MyEd_MNyRd >=0) and (MzEd_MNzRd >=0) and (MNyRd !=0) and (MNyRd != 0):
                URCS_1 = math.pow(abs(My1) / MNyRd,α) + math.pow(abs(Mz1) / MNzRd, β)
                URCS_2 = math.pow(abs(My2) / MNyRd,α) + math.pow(abs(Mz2) / MNzRd, β)              
            else:
                URCS_1 = 999
                URCS_2 = 999

            p("URCS_1 = ","%.3f"% URCS_1, "Section utilisation at end 1 - Axial and bending", InSummary = True)
            p("URCS_2 = ","%.3f"% URCS_2, "Section utilisation at end 2 - Axial and bending", InSummary = True)

            URCS_ok = (URCS_1 < 1.0) and (URCS_2 < 1.0)
            if URCS_ok:
                  p("OK - The cross-section resistance is adequate for combined biaxial bending and axial")
            else:
                CalcNotOK = True
                p("NOT OK")  

        else:
            p("The Section class is not 1 or 2")


        # #### Bending and Axial force - Class 1 and 2 (cl. 6.2.9.2)

        # In[17]:


        if classSection==3:
            p("Combined bending and axial load")
            p("The Section class is 3: EC clause 6.2.9.2 and  6.2.1(7)")
        
            p("MyEd=", "%.1f"% MyEd, "Nm     Design bending moment")
    
            p("URCS_1 = N/NcRd + abs(My1)/McyRd + abs(Mz1)/MczRd")
            URCS_1 = N/NcRd + abs(My1)/McyRd + abs(Mz1)/MczRd
            p("URCS_1 = ","%.3f"% URCS_1, "Section utilisation at end 1 - Axial and bending")

            URCS_2 = N/NcRd + abs(My2)/McyRd + abs(Mz2)/MczRd 
            p("URCS_2 = ","%.3f"% URCS_2, "Section utilisation at end 2 - Axial and bending")


        # ## Buckling resistance (cl. 6.3)

        # #### Buckling curves
        # 
        # 

        # In[18]:


        p_title("Buckling resistance (cl. 6.3)")
        #Selecting the correct buckling curve according to Table 6.2
        curve_yy = "NA"
        curve_zz = "NA"
        if (h/b) > 1.2:
            if tf <= 40:
                curves_yy = ["a", "a0"]
                curves_zz = ["b", "a0"]
            if (40 < tf) and (tf <= 150):    #Buckling curves h/n>1.2  (tf <= 100) not satistfied with UC1299. Assume tf<150???
                curves_yy = ["b","a"]
                curves_zz = ["c","a"]
        if (h/b) <= 1.2:
            if tf <= 100:
                curves_yy = ["b","a"]
                curves_zz = ["c","a"]
            if (tf > 100):
                curves_yy = ["d","c"]
                curves_zz = ["d","c"]

        #!! Grade S420 not covered!
        if fy<=355:                   #355 to fix mistake
            curve_yy=curves_yy[0]
            curve_zz=curves_zz[0]   
        if fy>356:                    #360
            curve_yy=curves_yy[1]
            curve_zz=curves_zz[1] 
    

        p("fy = ",fy, "N/mm2    Yield strength for buckling resistance")
        h_b= h/b
        p("h/b = ", "%.1f"% h_b)
        p("tf = ", tf, "mm")
        p("The buckling curve in yy direction:", curve_yy)
        p("The buckling curve in zz direction:", curve_zz)


        # <img src="BucklingCurve.png" alt="Table 6.2" style="width: 500px;"/>

        # In[19]:


        def Table6_1(argcurve):
            factor = -1
            if argcurve == "a0":
                factor = 0.13
            elif argcurve == "a":
                factor = 0.21
            elif argcurve == "b":
                factor = 0.34        
            elif argcurve == "c":
                factor = 0.49            
            elif argcurve == "d":
                factor = 0.76 
            return factor


        # #### Flexural buckling - Major axis

        # In[20]:




        Ncry = pi**2 * E * Iy / (Ly**2)
        p("Ncry = ", "%.0f"% Ncry," N    Elastic critical buckling force" )

        λy = math.sqrt(A * fy / Ncry)
        p("λy =", "%.3f"% λy, "    Non-dimensional slenderness")

        αy = Table6_1(curve_yy)
        p("αy = ",αy, "    Imperfection factor (Table 6.1)")

        Φy = 0.5 * (1 + αy*(λy - 0.2) + λy**2)
        p("Φy = ", "%.3f"% Φy)

        Χy = min(1.0, 1 / (Φy + math.sqrt(Φy**2 -λy**2)))
        p("Χy = ","%.3f"% Χy, "Reduction factor")

        NbyRd = Χy * A * fy  / γM1
        p("NbyRd = ", "%.0f"% NbyRd, "N    Design buckling resistance (Major)" , InSummary=True)         

        N_NbyRd = N / NbyRd         
        p("N / NbyRd =", "%.3f"% N_NbyRd, "Buckling resistance - Major Axis")
         
        N_NbyRd_ok = N_NbyRd <1
        if N_NbyRd_ok:
              p("OK - The flexural buckling resistance exceeds the design axial load (Major axis)")
        else:
            CalcNotOK = True
            p("NOT OK")  


        # #### Flexural buckling - Minor axis

        # In[21]:


        Ncrz = pi**2 * E * Iz / (Lz**2)
        p("Ncrz = ", "%.0f"% Ncrz," N    Elastic critical buckling force" )

        λz = math.sqrt(A * fy / Ncrz)
        p("λz =", "%.3f"% λz, "    Non-dimensional slenderness")

        αz = Table6_1(curve_zz)
        p("αz = ",αz, "    Imperfection factor (Table 6.1)")

        Φz = 0.5 * (1 + αz*(λz - 0.2) + λz**2)
        p("Φz = ", "%.3f"% Φz)

        Χz = min(1.0, 1 / (Φz + math.sqrt(Φz**2 -λz**2)))
        p("Χz = ","%.3f"% Χz, "Reduction factor")

        NbzRd = Χz * A * fy  / γM1
        p("NbzRd = ", "%.0f"% NbzRd, "N    Design buckling resistance (Minor)" , InSummary=True)         

        N_NbzRd = N / NbzRd         
        p("N / NbzRd =", "%.3f"% N_NbzRd,  "Buckling resistance - Minor Axis")
         
        N_NbzRd_ok = N_NbzRd <1
        if N_NbzRd_ok:
              p("OK - The flexural buckling resistance exceeds the design axial load (Minor axis)")
        else:
            CalcNotOK = True
            p("NOT OK")  


        # ## Torsional and torsional-flexural buckling (cl. 6.3.1.4)
        # 

        # For members with open cross-sections account should be taken of the possibility that the resistance of the member to either torsional or torsional-flexural buckling could be less that its resistance to flexural buckling
        # 
        # SCI:
        # Torsional buckling, which may be critical for cruciform sections subject to axial compression
        # Torsional-flexural buckling, which may be critical for asymmetric sections subject to axial compression.
        # 

        # ## Buckling resistance moment (cl.6.3.2.1)
        # 
        # Critical moment - Clark, J. W. and hill, H. N. - Lateral buckling of beams  (TBC)
        # 
        # Valid for DOUBLE symmetrical sections
        # 
        # Mcr = c1 x (π2 x E x I / Leff2) x (( (Iw/Iz) + (Leff2 x G x IT/π2 x E x Iz) + (C2 zg)2)0.5 - C2zg)
        # 
        # 
        # 

        # In[ ]:


        p("All calcs valid for rolled sections or equivalent welded sections")
        p("KLT = 1.0  Lcr_LT = Lz    Lateral torsional buckling length factor")

        # Lcr_LT = KLT * Lz   (Tedds Notations)
        Lcr_LT = Lz              #Simplied assumptions for Lateral torsional buckling Lcr_lt=Lz hence KLT=1.0
        p("Lcr_LT = ", "%.0f"% Lcr_LT, "Effective buckling length")

        if MyEd != 0:
            Ψ = My2 / MyEd
        else:
            Ψ = 0
        p("Ψ = ","%.2f"% Ψ,"    End moment factor")

        #!!! Simple moment distribution: Linear
        kc = 1 / (1.33 - 0.33 * Ψ) 
        p("kc = ","%.3f"% kc,"    Moment distribution correction factor (Table 6.6)")

        C1 = 1 / (kc**2)
        p("C1 = ","%.2f"% C1)

        g = math.sqrt(1 - (Iz / Iy))
        p("g = ","%.3f"% g,"    Curvature factor")

        Mcr = C1 * pi**2 * E * Iz * sqrt((Iw / Iz) + Lcr_LT**2 * G * IT / (pi**2 * E * Iz)) /(Lcr_LT**2 * g)
        p("Mcr = ","%.0f"% Mcr,"    Elastic critical buckling moment")


        # In[ ]:


        λLT = sqrt(Wy * fy / Mcr)
        p("λLT = ","%.3f"% λLT,"    Slenderness ratio for lateral torsional buckling")

        λLT0 = 0.40
        p("λLT = ","%.3f"% λLT0,"    Limiting slenderness ratio as per 6.3.2.3 for rolled sections")

        βr = 0.75
        p("βr = ","%.3f"% βr,"    Correction factor for rolled sections")

        if h/b<=2:
            curve_LT = "b"
        if h/b > 2:
            curve_LT = "c"
        p("Buckling curve LT = ", curve_LT,"  (Table 6.5)")


        αLT = Table6_1(curve_LT)
        p("αLT = ",αLT, "    Imperfection factor (Table 6.1)")

        ΦLT = 0.5 * (1 + αy*(λLT - λLT0) + βr*λy**2)
        p("ΦLT = ", "%.3f"% ΦLT)

        ΧLT = min(1.0 , 1 / λLT**2 ,  1 / (ΦLT + sqrt(ΦLT**2 -βr*λy**2)))
        p("ΧLT = ","%.3f"% ΧLT, "Reduction factor")

        f = min(1 - 0.5 * (1 - kc)* (1 - 2 * (λLT - 0.8)**2), 1)
        p("f = ","%.3f"% f, "Modification factor")

        ΧLTmod = min(ΧLT / f, 1, 1/λLT**2)
        p("ΧLTmod = ","%.3f"% ΧLTmod, "Modified LTB reduction factor  - eq 6.58")

        MbRd = ΧLTmod * Wy * fy / γM1
        p("MbRd = ","%.0f"% MbRd, "Nmm    Design buckling resistance moment", InSummary=True)

        MyEd = max(abs(My1), abs(My2))
        p("MyEd = ","%.0f"% MyEd, "Nmm    Design bending moment")

        MyEd_MbRd  = MyEd / MbRd
        p("MyEd / MbRd = ","%.3f"% MyEd_MbRd)

        MyEd_MbRd_ok = MyEd_MbRd<1
        if MyEd_MbRd_ok:
              p("OK - The design buckling resistance moment exceeds the maximum design moment")
        else:
            CalcNotOK = True
            p("NOT OK")  


        # ## Combined bending and axial compression (cl. 6.3.3)

        # In[ ]:



        NRk = A * fy 
        if classSection==1 or classSection==2:
            p("Class 1 or 2 cross-sections. W=Wpl")
            MyRk = Wply * fy
            MzRk = Wplz * fy
        if classSection==3:
            p("Class 3 cross-sections. W=Wel")
            MyRk = Wely * fy
            MzRk = Welz * fy
        p("NRk = ","%.0f"% NRk, "N    Characteristic resistance to normal force")
        p("MyRk = ","%.0f"% MyRk, "Nmm    Characteristic moment resistance - Major axis", InSummary=True)
        p("MzRk = ","%.0f"% MzRk, "Nmm    Characteristic moment resistance - Minor axis", InSummary=True)


        def Ψ(M1,M2):
            if abs(M1)<=abs(M2):
                if M2>=0:
                    _Ψ = M1 / max(M2, 100)
                else:
                    _Ψ = M1 / M2
            else:
                if M1>=0:
                    _Ψ = M2 / max(M1, 100)
                else:
                    _Ψ = M2 / M1
            return _Ψ

        Ψy = Ψ(My1, My2)
        Ψz = Ψ(Mz1, Mz2)
        ΨLT = Ψy
        p("Ψy = ","%.3f"% Ψy, "    Moment distribution factor - Major axis")
        p("Ψz = ","%.3f"% Ψz, "    Moment distribution factor - Major axis")
        p("ΨLT = ","%.3f"% Ψy, "    Moment distribution factor - LTB")

        Cmy = max(0.4, 0.6 + 0.4 * Ψy)
        Cmz = max(0.4, 0.6 + 0.4 * Ψz)
        CmLT = max(0.4, 0.6 + 0.4 * ΨLT)
        p("Cmy = ","%.3f"% Cmy, "    Moment factor - Major axis")
        p("Cmz = ","%.3f"% Cmz, "    Moment factor - Minor  axis")
        p("CmLT = ","%.3f"% CmLT, "    Moment factor - LTB")

        p("Using Method 2 of Annex B")
        if classSection==1 or classSection==2:
            p("Class 1 or 2 cross-sections factors")
            kyy = Cmy*( 1 + min(0.8, λy-0.2) * N/(Χy*NRk/γM1) )
            kzy = 1 - min(0.1, 0.1*λz)*N / ((CmLT - 0.25)*(Χz * NRk/ γM1))      #Formula differente from EUROCODE?
            kzz = Cmz * (1 + min(1.4, 2*λz - 0.6) * N / (Χz * NRk / γM1))
            kyz =  0.6 * kzz  
    
        if classSection==3 or classSection==4:
            p("Class 3 cross-sections factors")
            kyy = Cmy*( 1 + min(0.6, 0.6*λy) * N/(Χy*NRk/γM1) )
            kzy = 1 - min(0.05, 0.05*λz)*N / ((CmLT - 0.25)*(Χz * NRk/ γM1))
            kzz = Cmz * (1 + min(0.6, 0.6*λz) * N / (Χz * NRk / γM1))
            kyz =  kzz 
    
        p("Interactions factors:")
        p("kyy = ","%.3f"% kyy)
        p("kzy = ","%.3f"% kzy)
        p("kzz = ","%.3f"% kzz)
        p("kyz = ","%.3f"% kyz)

        URB_1 = N / (Χy*NRk / γM1) + (kyy*MyEd) / (ΧLT*MyRk / γM1) + (kyz*MzEd) / (MzRk / γM1)
        URB_2 = N / (Χz*NRk / γM1) + (kzy*MyEd) / (ΧLT*MyRk / γM1) + (kzz*MzEd) / (MzRk / γM1)
        p("URB_1 = ","%.3f"% URB_1 , " Section utilisation end 1: Buckling and bending" ,InSummary=True)
        p("URB_2 = ","%.3f"% URB_2 , " Section utilisation end 2: Buckling and bending" ,InSummary=True)

        URB_1_ok = URB_1<1
        URB_2_ok = URB_2<1
        if URB_1_ok and URB_2_ok:
              p("OK - The design buckling resistance with combined bending is not exceeded")
        else:
            CalcNotOK = True
            p("NOT OK")  
                                                                        #FAIL - The buckling resistance is exceeded


        # ## Summary

        # In[ ]:
        p("URCS_1 = ","%.3f"% URCS_1, "Section utilisation at end 1 - Axial and bending")
        p("URCS_2 = ","%.3f"% URCS_2, "Section utilisation at end 2 - Axial and bending")
        p("N / NbyRd =", "%.3f"% N_NbyRd, "Buckling resistance - Major Axis")
        p("N / NbzRd =", "%.3f"% N_NbzRd,  "Buckling resistance - Minor Axis")
        p("URB_1 = ","%.3f"% URB_1 , " Section utilisation end 1: Buckling and bending ")
        p("URB_2 = ","%.3f"% URB_2 , " Section utilisation end 2: Buckling and bending")

        UR = max(URCS_1, URCS_2, URB_1, URB_2 )


    
        if CalcNotValid:
            p("")
            p("!!!  Caculation Not Valid - Check Assumptions !!!!!!!", InSummary=True)
            UR=9999999


        p("")
        p("UR = ","%.3f"% UR, "Overall utilisation factor", InSummary=True)
        if CalcNotOK:
            p("NOT OK" , InSummary=True)


        # In[ ]:


        #print(Summary)
        #print(AllText)
        self.text = AllText
        self.summary = Summary
        self.utilisation = UR
        #return UR


# ### Test class structure

# In[ ]:

testhere = False
if testhere:
    d = ColumnUtilisation(2500)
    d.calcs()
    print(d.utilisation)
    print(d.summary)
    print(d.text)




