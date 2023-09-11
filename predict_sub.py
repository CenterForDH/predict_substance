import pickle
import streamlit as st
import time
import requests

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
def model_file():
    mfile_url = 'https://raw.githubusercontent.com/CenterForDH/predict_substance/main/predict_substance_model.pkl'
    response = requests.get(mfile_url)
    model = pickle.loads(response.content)
    return model




def prediction(X_test):
    model = model_file()
    result = model.predict_proba([X_test])

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
    
    SEX     = st.radio('Sex',('Male','Female'), horizontal=True)
    SEXDict = {'Male':1,'Female':2}
    SEX = SEXDict[SEX]

    GRADE   = st.radio('Age(year)',(13,14,15,16,17,18), horizontal=True)

    height  = st.number_input('Height (cm)', min_value=80, max_value=190, value=130)
    weight  = st.number_input('Weight (kg)', min_value=30, max_value=100, value=50)
    bmiv = weight/((height/100)**2)
    bmi_2 = set_bmi(bmiv)
    bmiDict = {1:'Underweight',2:'Normal',3:'Overweight',4:'Obesity'}
    st.write('BMI: ', bmiDict[bmi_2], round(bmiv,2))
    
    region  = st.radio('Region of regidence', ('Urban','Rural'), horizontal=True)
    regionDict = {'Urban':1,'Rural':2}
    region  = regionDict[region]
    
   
    study    = st.radio('School performance', ('Low', 'Low-middle','Middle','Upper-middle','Upper'), horizontal=True)
    studyDict = {'Low':1, 'Low-middle':2,'Middle':3,'Upper-middle':4,'Upper':5}
    study = studyDict[study]

    smoking   = st.radio('Smoking status', ('No','Yes'), horizontal=True)
    smokingDict = {'No':0,'Yes':1}
    smoking   = smokingDict[smoking]
    
    alcoholic_consumption = st.radio('Acohol consumption per month', ('No','1-2','3-5','6-9','< 10'), horizontal=True)
    alcoholic_consumptionDict = {'No':0,'1-2':1,'3-5':2,'6-9':3,'< 10':4}
    alcoholic_consumption = alcoholic_consumptionDict[alcoholic_consumption]
    
    stress  = st.radio('Stress status', ('Low','Moderate', 'High','Very much'), horizontal=True)
    stressDict = {'Low':1,'Moderate':2,'High':3,'Very much':4}
    stress = stressDict[stress]
    
    depression = st.radio('Sadness and despair', ('No','Yes'), horizontal=True)
    depressionDict = {'No':0,'Yes':1}
    depression = depressionDict[depression]

    suicidalthinking = st.radio('Suicidal thinking', ('No','Yes'), horizontal=True)
    suicidalthinkingDict = {'No':0,'Yes':1}
    suicidalthinking = suicidalthinkingDict[suicidalthinking]

    suicideattempts = st.radio('Suicide attempts', ('No','Yes'), horizontal=True)
    suicideattemptsDict = {'No':0,'Yes':1}
    suicideattempts = suicideattemptsDict[suicideattempts]
    
    X_test = [GRADE, SEX, alcoholic_consumption, bmi_2, depression, 
          region, smoking, stress, study, suicidalthinking, suicideattempts]

    result = prediction(X_test)

    return result


def main():
    result = input_values()    
    
    with st.sidebar:
        st.markdown(f'# Probability for substance usage')
        st.markdown(f'# {result*100:.2f} %')

    now = time.localtime()
    print(time.strftime('%Y-%m-%d %H:%M:%S', now))

        

if __name__ == '__main__':
    main()
