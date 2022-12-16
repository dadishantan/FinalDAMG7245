import pickle
import boto3
from pathlib import Path

import streamlit_authenticator as stauth

names = ["samanth koduru", "Shantan Dadi"]
usernames = ["samK","shanD"]
passwords = ["abc123","def456"]

hashed_passwords = stauth.Hasher(passwords).generate()
clf_model_pkl = pickle.dump(hashed_passwords,open('hashed_passwords.pkl','wb'))
s3 = boto3.resource('s3')
s3.meta.client.upload_file('hashed_passwords.pkl','password-streamlit','hashed_passwords.pkl')


