import streamlit as st
import boto3
import pickle
import os
import streamlit_authenticator as stauth



st.set_page_config(
    page_title= "Classify Potential Customer App"
)

st.title("Main Page")
st.sidebar.success("Select a page above.")