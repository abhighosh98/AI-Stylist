from hydralit import HydraApp
import streamlit as st
import pyrebase
import streamlit as st
from datetime import datetime
from google.cloud import firestore
import pandas as pd
import time
from hydralit import HydraHeadApp
from app import LoginModule
from dummy_app import dummyModule
from detect_clothing_item import DetectItemModule
from __init__ import wardrobe
from recommendation_page import recommendation_module
import pyautogui


if __name__ == '__main__':

    #this is the host application, we add children to it and that's it!
    app = HydraApp(title='AI Stylist', favicon="🧠")
    
    if 'login_success_flag' not in st.session_state:
                st.session_state['login_success_flag'] = 0

    st.markdown(""" <style>
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style> """, unsafe_allow_html=True)

    st.markdown("<h1 style='text-align: center; color: red;'>AI Stylist</h1>", unsafe_allow_html=True)

    def clicking_sign_up_button():
        if sign_up_button:
            # Empty username
            if(len(username) == 0):
                username_empty_warning = st.warning("Username cannot be empty!")
                return

            length_of_returned_query_on_username = len(list(users_ref.where('username', '==', username).stream()))
            # Checking if username exists
            if(length_of_returned_query_on_username > 0):
                username_warning_exists = st.warning("Username already exists")     
                # time.sleep(2)
                # username_warning_exists.empty()   
                return
            
            # Empty username
            if(len(password) == 0):
                password_empty_warning = st.warning("Password cannot be empty!")
                return

            # Check for same password input
            if(password != password_confirm):
                password_mismatch_warning = st.warning("Password mismatch! Please check password")
                # time.sleep(2)
                # password_mismatch_warning.empty()  
                return


            sign_up_progress = st.progress(0)
            for percent_complete in range(100):
                time.sleep(0.01)
                sign_up_progress.progress(percent_complete + 1)
            # Add user to database
            users_ref.add({
            'username': username,
            'password': password,

            'overall_gcs_links': [],
            'up_gcs_links': [],
            'down_gcs_links': [],
            'foot_gcs_links': [],

            'overall_clothing_items': [],
            'up_clothing_items': [],
            'down_clothing_items': [],
            'foot_clothing_items': [],

            'overall_color': [],
            'up_color': [],
            'down_color': [],
            'foot_color': [],
            
            })
            st.success("Signed up successfully")
            print("clean user data added")

            

    def clicking_sign_in_button():
        # Empty username
        if(len(username) == 0):
            username_empty_warning = st.warning("Username cannot be empty!")
            return
        
        # Empty password
        if(len(password) == 0):
            password_empty_warning = st.warning("Password cannot be empty!")
            return

        full_query_of_user = list(users_ref.where('username', '==', username).stream())
        if(len(full_query_of_user) == 0):
            wrong_user_warning = st.warning("Username is not registered!")
            return

        for d in full_query_of_user:
            username_table_id = d.id
            username_related_data = d.to_dict()
        
        # Incorrect password
        if(password != username_related_data['password']):
            incorrect_password_warning = st.warning("Incorrect password")
            return
        
        st.success("Successfully logged in")
        st.session_state['login_success_flag'] = 1
            
    
    collection_name_users = 'Users'

    # Authenticate to Firestore with the JSON account key.
    db = firestore.Client.from_service_account_json("dsci551-2480c-firebase-adminsdk-618ag-661cea2016.json")

    # Create a reference to the Google post.
    users_ref = db.collection(collection_name_users)

    # Then get the data at that reference.
    users_table = users_ref.get()
    
    # login_sidebar_title = st.sidebar.title("Your Guide to Your Style")
    login_sidebar_title = st.sidebar.empty() 
    login_sidebar_title.title("Your Guide to Your Style")

    # Authentication
    # choice = st.sidebar.selectbox('Login/Signup', ['Login', 'Sign up'])
    choice_placeholder = st.sidebar.empty() 
    choice = choice_placeholder.selectbox('Login/Signup', ['Login', 'Sign up'])

    # Obtain User Input for email and password
    # username = st.sidebar.text_input('Please enter your email address', key = "current_password")
    username_placeholder = st.sidebar.empty() 
    username = username_placeholder.text_input('Please enter your user', key = "current_username")

    # password = st.sidebar.text_input('Please enter your password', type = 'password', key = 'current_password)
    password_placeholder = st.sidebar.empty() 
    password = password_placeholder.text_input('Please enter your password', type = 'password', key = "current_password")
    
    

    # Sign up Block
    if choice == 'Sign up':
        password_confirm = st.sidebar.text_input(
            'Please confirm your password',type = 'password'
            )
        sign_up_button = st.sidebar.button('Create my account')
        if(sign_up_button):
            clicking_sign_up_button()
    elif choice == 'Login':
        # sign_in_button = st.sidebar.button('Sign In')
        sign_in_button_placeholder = st.sidebar.empty() 
        sign_in_button = sign_in_button_placeholder.button('Sign In')
        if(sign_in_button):
            clicking_sign_in_button()

    # print("Within login", st.session_state)






    app.add_app("", app = dummyModule())
    #add all your application classes here
    if(st.session_state.login_success_flag == 1):
        app.add_app("Detect Color", app = LoginModule())
        login_sidebar_title.empty()
        choice_placeholder.empty()
        username_placeholder.empty()
        password_placeholder.empty()
        sign_in_button_placeholder.empty()
        sign_out_button = st.sidebar.button('Sign Out')
        if(sign_out_button):
            pyautogui.press('f5')


        app.add_app("Add Item", app = DetectItemModule())
        app.add_app("Digital Wardrobe", app = wardrobe())
        app.add_app("Recommend Outfits", app = recommendation_module())
        
    # print("In multipage", st.session_state)
    # app.add_app("Sample App",icon="🔊", app=MySampleApp())

    #run the whole lot
    app.run()