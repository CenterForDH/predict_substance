import streamlit as st
import time
import os
import pandas as pd
import numpy as np

from pathlib import Path
import pickle 
from imblearn.over_sampling import SMOTE
from xgboost import XGBClassifier
from sklearn.model_selection import train_test_split
from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline as ImbPipeline
import scipy.stats
from scipy import stats
from skopt import BayesSearchCV
from sklearn.base import BaseEstimator, TransformerMixin
import xgboost as xgb
from sklearn.preprocessing import MinMaxScaler,StandardScaler
from sklearn.model_selection import KFold, cross_val_score, StratifiedKFold, train_test_split, GridSearchCV
from sklearn.metrics import make_scorer, recall_score, accuracy_score, f1_score,precision_score, roc_auc_score, confusion_matrix, balanced_accuracy_score, average_precision_score,precision_recall_curve, auc

#st.set_page_config(layout="wide")

st.markdown(
    """
    <style>
    .css-1jc7ptx, .e1ewe7hr3, .viewerBadge_container__1QSob,
    .styles_viewerBadge__1yB5_, .viewerBadge_link__1S137,
    .viewerBadge_text__1JaDK {
        display: none;
    }
    </style>
    """,
    unsafe_allow_html=True
)

footerText = """
<style>
#MainMenu {
visibility:hidden ;
}

footer {
visibility : hidden ;
}

.footer {
position: fixed;
left: 0;
bottom: 0;
width: 100%;
background-color: transparent;
color: white;
text-align: center;
}
</style>

<div class='footer'>
<p> Copyright @ 2023 Center for Digital Health <a href="mailto:iceanon1@khu.ac.kr"> iceanon1@khu.ac.kr </a></p>
</div>
"""

st.markdown(str(footerText), unsafe_allow_html=True)

@st.cache_data
@st.cache_resource
#sub_finalized_model_adb predict_substance_model
def model_file():
    #mfile1 = str(Path(__file__).parent) / 'XGboost_grid_auc.pkl'
    #mfile2 = str(Path(__file__).parent) / 'XGboost_grid_precision.pkl'

    with open('XGboost_grid_auc.pkl', 'rb') as file1:
            auc_model = pickle.load(file1)
    with open('XGboost_grid_precision.pkl', 'rb') as file2:
            precision_model = pickle.load(file2)
    
    return auc_model,precision_model

# predict_substance_model
# sub_finalized_model_lgb


def prediction(X_test):
    auc_model, precision_model = model_file()
    #result=auc_model.predict_proba(X_test)
    y_proba_auc = auc_model.predict_proba(X_test)
    y_proba_precision = precision_model.predict_proba(X_test)
    result =  y_proba_auc*0.4 + y_proba_precision*0.6

    return result[0][1]


def set_bmi(BMI):
    x = 4
    if   BMI <  18.5           : x = 1
    elif BMI >= 18.5 and BMI < 23: x = 2
    elif BMI >= 23   and BMI < 25: x = 3
    elif BMI >= 25             : x = 4
    else : x = 0

    return x


def input_values():
    file_path="train_x.csv"
    if os.path.exists(file_path):
        train = pd.read_csv(file_path)
        print("로컬 파일 로드 성공!")
    else:
        print(f"파일이 없습니다: {file_path}")

    
    SEX     = st.radio('Sex',('Male','Female'), horizontal=True)
    SEXDict = {'Male':1,'Female':2}
    sex = SEXDict[SEX]

    grade   = st.radio('Grade',('7th', '8th', '9th', '10th', '11th', '12th'), horizontal=True)
    gradeDict = {'7th': 1, '8th': 2, '9th': 3, '10th': 4, '11th': 5, '12th': 6}
    grade= gradeDict[grade]
    
    height  = st.number_input('Height (cm)', min_value=80, max_value=190, value=130)
    weight  = st.number_input('Weight (kg)', min_value=30, max_value=100, value=50)
    bmiv = weight/((height/100)**2)
    bmi_2 = set_bmi(bmiv)
    bmiDict = {1:'Underweight',2:'Normal',3:'Overweight',4:'Obesity'}
    st.write('BMI: ', bmiDict[bmi_2], round(bmiv,2))
    
    region  = st.radio('Region of regidence', ('Urban','Rural'), horizontal=True)
    regionDict = {'Urban':1,'Rural':2}
    region  = regionDict[region]
    
    household_income  = st.radio('Household income', ('Low','Middle','Upper-middle','High'), horizontal=True)
    household_incomeDict = {'Low':1,'Middle':2,'Upper-middle':3,'High':4}
    economic  = household_incomeDict[household_income]
   
    study    = st.radio('School performance', ('Low', 'Low-middle','Middle','Upper-middle','Upper'), horizontal=True)
    studyDict = {'Low':1, 'Low-middle':2,'Middle':3,'Upper-middle':4,'Upper':5}
    study = studyDict[study]

    smoking   = st.radio('Smoking status', ('No','Yes'), horizontal=True)
    smokingDict = {'No':0,'Yes':1}
    smoking   = smokingDict[smoking]
    
    alcoholic_consumption = st.radio('Acohol consumption Status', ('No','Yes'), horizontal=True)
    alcoholic_consumptionDict = {'No':0,'Yes':1}
    alcohol = alcoholic_consumptionDict[alcoholic_consumption]
    
    stress  = st.radio('Stress status', ('Low','Moderate', 'High','Very much'), horizontal=True)
    stressDict = {'Low':1,'Moderate':2,'High':3,'Very much':4}
    stress = stressDict[stress]
    
    depression = st.radio('Depression', ('No','Yes'), horizontal=True)
    depressionDict = {'No':0,'Yes':1}
    depression = depressionDict[depression]

    suicidalthinking = st.radio('Suicidal thinking', ('No','Yes'), horizontal=True)
    suicidalthinkingDict = {'No':0,'Yes':1}
    suicidalthinking = suicidalthinkingDict[suicidalthinking]

    suicideattempts = st.radio('Suicide attempts', ('No','Yes'), horizontal=True)
    suicideattemptsDict = {'No':0,'Yes':1}
    suicideattempts = suicideattemptsDict[suicideattempts]
    
    X_test = [sex, grade, region, bmi_2, study, economic, smoking, alcohol, stress, depression, suicidalthinking, suicideattempts]
    
    if isinstance(X_test, list):
        X_test = np.array(X_test)
    if X_test.ndim == 1:
        X_test = X_test.reshape(1, -1)
        
    scaler = MinMaxScaler()
    scaler.fit(train)   
    X_test_scaled = scaler.transform(X_test)
    
    result = prediction(X_test)

    return result


def main():
    result = input_values()    
    
    with st.sidebar:
        st.markdown(f'# Probability for substance usage')
        
        if result*100 < 50:
            addiction_level = 'Barely'
        elif result*100 < 75:  # 50% 이상 75% 미만
            addiction_level = 'Moderately'
        elif result*100 < 90:  # 75% 이상 90% 미만
            addiction_level = 'Considerably'
        elif result*100 <= 100 :  # 90% 이상
            addiction_level = 'Extremely'
            
        st.markdown(f'# {result*100:.2f} %')

    now = time.localtime()
    print(time.strftime('%Y-%m-%d %H:%M:%S', now))


        

if __name__ == '__main__':
    main()
