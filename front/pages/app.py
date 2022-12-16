import json
import os
import pickle
import boto3
import httpx
import numpy as np
from sklearn.preprocessing import LabelEncoder,StandardScaler
from catboost import CatBoostClassifier 
import botocore
from fastapi import Body, FastAPI
from fastapi.logger import logger
from pydantic import BaseModel
import joblib
import pandas as pd
import streamlit as st
import streamlit_authenticator as stauth


#--------------------------USER ATHENTICATION-------------------------------------
names = ["samanth koduru", "Shantan Dadi"]
usernames = ["samK","shanD"]
s3 = boto3.resource('s3')
Bucket = s3.Bucket('password-streamlit')
    
for s3_object in Bucket.objects.all():
    # Need to split s3_object.key into path and file name, else it will give error file not found.
        path, filename = os.path.split(s3_object.key)
        Bucket.download_file(s3_object.key, filename)
# load hashed Passwords
hashed_passwords = pickle.load(open('hashed_passwords.pkl','rb'))

#----------create credentials dictionary----------------------------------------
credentials = {
        "usernames":{
            usernames[0]:{
                "name":names[0],
                "password":hashed_passwords[0]
                },
            usernames[1]:{
                "name":names[1],
                "password":hashed_passwords[1]
                }            
            }
        }

print(hashed_passwords[0])

authenticator = stauth.Authenticate(credentials, "insurance_dashboard", "900", cookie_expiry_days=0)

name, authentication_status, username = authenticator.login("Login", "main")

if authentication_status == False:
    st.error("Username/passwords is incorrect")
if authentication_status == None:
    st.warning("Please enter your username and password")
if authentication_status:

#---------------------SETTINGS---------------------------------------------------------------
    gender = ["Male","Female"]
    region = [28,  3, 11, 41, 33,  6, 35, 50, 15, 45,  8, 36, 30,
       26, 16, 47, 48, 19, 39, 23, 37,  5, 17,  2,  7, 29,
       46, 27, 25, 13, 18, 20, 49, 22, 44,  0,  9, 31, 12,
       34, 21, 10, 14, 38, 24, 40, 43, 32,  4, 51, 42,  1,
       52]

    policy = ["Agents", "Over Mail", "Over Phone", "In Person"]
    

#--------------------Proceed with streamlit functions----------------------------------------


    def get_pkl():
        s3 = boto3.resource('s3')
        myBucket = s3.Bucket('pkl-files-s3')
        
        for s3_object in myBucket.objects.all():
        # Need to split s3_object.key into path and file name, else it will give error file not found.
            path, filename = os.path.split(s3_object.key)
            myBucket.download_file(s3_object.key, filename)


    get_pkl()
    xgb = pickle.load(open('XGBClassifier.pkl','rb'))
    print(xgb)


    st.title('Car Insurance')


    def predict(Age, Driving_License, Region_Code, Previously_Insured,
        Annual_Premium, Policy_Sales_Channel, vintage, Gender_F,
        Gender_M, Vehicle_Age_1_2, Vehicle_Age_1,
        Vehicle_Age_2, Vehicle_Damage_No, Vehicle_Damage_yes):
        input=np.array([[Age, Driving_License, Region_Code, Previously_Insured,
        Annual_Premium, Policy_Sales_Channel, vintage, Gender_F,
        Gender_M, Vehicle_Age_1_2, Vehicle_Age_1,
        Vehicle_Age_2, Vehicle_Damage_No, Vehicle_Damage_yes]]).astype(np.float64)
        prediction = xgb.predict(input)
        #pred = '{0:.{1}f}'.format(prediction[0][0], 2)

        print("This my prediction.........yaaaaaaay",prediction)
        return int(prediction)

    def main():
        #st.title("Potential Insurance Client Prediction")
        html_temp = """
        <div style="background:#025246 ;padding:10px">
        <h2 style="color:white;text-align:center;">Potential Insurance Client Prediction</h2>
        </div>
        """
        st.markdown(html_temp, unsafe_allow_html = True)

        Age = st.text_input("Age")
        ques = st.radio("Do you have a license?",('Yes','No'))
        if ques == 'Yes':
            Driving_License = 1
        else:
            Driving_License = 0
        #Driving_License = st.text_input("Driving_License")
        Region_Code=st.selectbox("Select Region Code:", region, key = "Region Code")
        #Region_Code = st.text_input("Region_Code")
        r = st.radio("Have you been insured before?",('Yes','No'))
        if r == 'Yes':
            Previously_Insured = 1
        else:
            Previously_Insured = 0
        #Previously_Insured = st.text_input("Previously_Insured")
        Annual_Premium = st.slider('Please enter your current annual premium', 1000, 50000, 500)
        #Annual_Premium = st.text_input("Annual_Premium")
        channel=st.selectbox("Select How you were contacted:", policy , key = "policy")
        if channel == 'Agents':
            Policy_Sales_Channel = 1
        if channel == 'Over Mail':
            Policy_Sales_Channel = 6
        if channel == 'In Person':
            Policy_Sales_Channel = 2
        #Policy_Sales_Channel = st.text_input("Policy_Sales_Channel")
        vintage = st.slider('Number of days has the customer been associated with us ?', 0, 500, 10)
        #vintage = st.text_input("vintage")
        gen=st.selectbox("Select Gender:", gender, key = "Gender")
        if gen == 'Male':
            Gender_F = 0
            Gender_M = 1
        else:
            Gender_F = 1
            Gender_M = 0
        #Gender_F = st.text_input("Gender_F")
        #Gender_M = st.text_input("Gender_M")
        v_age = st.slider('How many years since the car has been puchased?', 0, 10, 1)
        if v_age < 1:
            Vehicle_Age_1_2 = 0
            Vehicle_Age_1 = 1
            Vehicle_Age_2 = 0
        if v_age >= 1 and v_age <= 2:
            Vehicle_Age_1_2 = 1
            Vehicle_Age_1 = 0
            Vehicle_Age_2 = 0
        if v_age > 2:
            Vehicle_Age_1_2 = 0
            Vehicle_Age_1 = 0
            Vehicle_Age_2 = 1

        #Vehicle_Age_1_2 = st.text_input("Vehicle_Age_1_2")
        #Vehicle_Age_1 = st.text_input("Vehicle_Age_1")
        #Vehicle_Age_2 = st.text_input("Vehicle_Age_2")
        dam = st.radio("Is the car damaged?",('Yes','No'))
        if dam == 'Yes':
            Vehicle_Damage_No = 0
            Vehicle_Damage_yes = 1
        else:
            Vehicle_Damage_No = 0
            Vehicle_Damage_yes = 1
        #Vehicle_Damage_No = st.text_input("Vehicle_Damage_No")
        #Vehicle_Damage_yes = st.text_input("Vehicle_Damage_yes")

        safe_html ="""  
        <div style="background-color:#80ff80; padding:10px >
        <h2 style="color:white;text-align:center;"> The Abalone is young</h2>
        </div>
        """
        warn_html ="""  
        <div style="background-color:#F4D03F; padding:10px >
        <h2 style="color:white;text-align:center;"> The Abalone is middle aged</h2>
        </div>
        """
        danger_html="""  
        <div style="background-color:#F08080; padding:10px >
        <h2 style="color:black ;text-align:center;"> The Abalone is old</h2>
        </div>
        """

        if st.button("Predict"):
            output = predict(Age, Driving_License, Region_Code, Previously_Insured,
        Annual_Premium, Policy_Sales_Channel, vintage, Gender_F,
        Gender_M, Vehicle_Age_1_2, Vehicle_Age_1,
        Vehicle_Age_2, Vehicle_Damage_No, Vehicle_Damage_yes)
            if output == 1:
                #st.success('output== {}'.format(output))
                st.success('Looks like a potential Customer')
            elif output == 0:
                st.success('Doesnt seen like a potential Customer')

            if output == 1:
                st.markdown(safe_html,unsafe_allow_html=True)
            elif output == 2:
                st.markdown(warn_html,unsafe_allow_html=True)
            elif output == 3:
                st.markdown(danger_html,unsafe_allow_html=True)

    if __name__=='__main__':
        main()

