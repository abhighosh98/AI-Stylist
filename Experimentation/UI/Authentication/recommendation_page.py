from google.cloud import storage
import os
import numpy as np
import pandas as pd
import webcolors
import cv2
# import matplotlib.pyplot as plt
from hydralit import HydraHeadApp
import streamlit as st
from google.cloud import firestore
import json
from sklearn.preprocessing import LabelEncoder
import xgboost as xgb
import pickle
import itertools


# Constants
project_id = "dsci551-2480c"
region = "us-east1"
path_to_credentials = "dsci551-2480c-4e478b8d0198.json"
bucket_name = "dsci551_storage"
bucket_path = "test_images/"
collection_name_users = 'Users'
length = 15
db = firestore.Client.from_service_account_json("dsci551-2480c-firebase-adminsdk-618ag-661cea2016.json")
users_ref = db.collection(collection_name_users)
partial_keys_for_username_related_data = ['_gcs_links', '_clothing_items', '_color']
gcs_links_columns = ['overall_gcs_links', 'up_gcs_links', 'down_gcs_links', 'foot_gcs_links']
required_columns_for_model_prediction = ['overall_clothing_items', 'overall_color',
'up_clothing_items', 'up_color',
'down_clothing_items', 'down_color',
'foot_clothing_items', 'foot_color',]

saved_objects = 'saved_objects'
xgb_color_names = xgb.XGBRegressor()
xgb_color_names.load_model(os.path.join(saved_objects, "xgb_color_names.json"))
with open (os.path.join(saved_objects, 'label_encoder_list'), 'rb') as fp:
    label_encoder_list = pickle.load(fp)
le = LabelEncoder()
le = le.fit(label_encoder_list)

with open (os.path.join(saved_objects, 'final_clothing_label_list'), 'rb') as fp:
    final_clothing_label_list = pickle.load(fp)
le_clothing = LabelEncoder()
le_clothing = le_clothing.fit(final_clothing_label_list)
gcs_links_columns = ['overall_gcs_links', 'up_gcs_links', 'down_gcs_links', 'foot_gcs_links']
required_columns_for_model_prediction = ['overall_clothing_items', 'overall_color',
'up_clothing_items', 'up_color',
'down_clothing_items', 'down_color',
'foot_clothing_items', 'foot_color',]




class recommendation_module(HydraHeadApp):
        def run(self):
            try:
                firestore_object = list(users_ref.where('username', '==', st.session_state.current_username).stream())
                for d in firestore_object:
                            username_table_id = d.id
                            username_related_data = d.to_dict()
            except:
                print(st.session_state)
        
            # Creating df for prediction
            user_wardrobe_df = pd.DataFrame(username_related_data)   
            
            appended_dfs_from_user_related_data = []
            # st.write(username_related_data)

            for links_col, i in zip(gcs_links_columns, range(0, len(required_columns_for_model_prediction), 2)):
                appended_dfs_from_user_related_data.append(pd.concat([user_wardrobe_df[links_col], user_wardrobe_df[required_columns_for_model_prediction[i]], user_wardrobe_df[required_columns_for_model_prediction[i + 1]]], axis = 1).apply(
                lambda x: ','.join(x.dropna().astype(str)),
                axis=1
            ))
            mix_n_match_df = pd.concat([appended_dfs_from_user_related_data[0], appended_dfs_from_user_related_data[1],
                    appended_dfs_from_user_related_data[2], appended_dfs_from_user_related_data[3]], axis = 1)
            mix_n_match_df.columns = ['overall', 'up', 'down', 'foot']
            # mix_n_match_df.replace('', np.nan, inplace = True)
            permuted_df = pd.DataFrame([e for e in itertools.product(mix_n_match_df.overall, mix_n_match_df.up,
                                          mix_n_match_df.down, mix_n_match_df.foot,)], 
             columns = mix_n_match_df.columns)
            permuted_df = permuted_df.drop(index = permuted_df[permuted_df.duplicated()].index)
            permuted_df.replace("", np.nan, inplace = True)
            permuted_df.dropna(inplace = True)
            # permuted_df = permuted_df.applymap(lambda x: 'no link,NA,no color' if x == '' else x)
            prediction_and_link_df = pd.DataFrame([])
            try:
                for col in permuted_df.columns:
                    temp_df = permuted_df[col].str.split(',', expand=True)
                    temp_df.columns = [col + '_gcs_links',
                                    col + '_item',
                                    col + '_color']
                    prediction_and_link_df = pd.concat([prediction_and_link_df, temp_df], axis = 1)
                prediction_df = prediction_and_link_df[['overall_color', 'up_color', 'down_color', 'foot_color', 
                                        'overall_item', 'up_item', 'down_item', 'foot_item']].copy()
                prediction_df['overall_color'] = le.transform(prediction_df['overall_color'])
                prediction_df['up_color'] = le.transform(prediction_df['up_color'])
                prediction_df['down_color'] = le.transform(prediction_df['down_color'])
                prediction_df['foot_color'] = le.transform(prediction_df['foot_color'])

                prediction_df['overall_item'] = le_clothing.transform(prediction_df['overall_item'])
                prediction_df['up_item'] = le_clothing.transform(prediction_df['up_item'])
                prediction_df['down_item'] = le_clothing.transform(prediction_df['down_item'])
                prediction_df['foot_item'] = le_clothing.transform(prediction_df['foot_item'])   
                top_3_indices = pd.DataFrame(xgb_color_names.predict(prediction_df)).sort_values(0).index[-3 : ]  
                gcs_links_df = prediction_and_link_df[gcs_links_columns]
                df_to_get_item_for_page = prediction_and_link_df[['overall_item', 'up_item', 'down_item', 'foot_item']].copy()

                
                
                # st.write(top_3_indices)
                print(prediction_and_link_df[['overall_color', 'up_color', 'down_color', 'foot_color', 
                                        'overall_item', 'up_item', 'down_item', 'foot_item']].iloc[top_3_indices])
                # st.write(gcs_links_df.iloc[top_3_indices])
                


                # Displaying the outputs
                st.title("Your top 3 outfits")
                column1, column2, column3 = st.columns(3)
                cols = [column1, column2, column3]
                
                # with column1:
                #     st.header("Overall Item")
                # with column2:
                #     st.header("Upper Body")
                # with column3:
                #     st.header("Lower Body")
                # with column4:
                #     st.header("Foot")
                # # with column5:
                # #     st.header("FScoreoot")

                # for i in top_3_indices:
                #     # Overall
                #     with column1:
                #         with st.container():
                #         # with st.expander("", expanded = True):
                #             st.subheader(df_to_get_item_for_page['overall_item'].iloc[i])
                #             temp_link = gcs_links_df['overall_gcs_links'].iloc[i]
                #             if(temp_link == 'no link'):                                                 
                #                 st.image("https://www.colorhexa.com/0e1117.png")
                #             else:
                #                 img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                #                 st.image(img_string)
                #             st.write("----------------------------")

                #     # Up
                #     with column2:
                #         with st.container():
                #         # with st.expander("", expanded = True):
                #             st.subheader(df_to_get_item_for_page['up_item'].iloc[i])
                #             temp_link = gcs_links_df['up_gcs_links'].iloc[i]
                #             if(temp_link == 'no link'):                                                 
                #                 st.image("https://www.colorhexa.com/0e1117.png")
                #             else:
                #                 img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                #                 st.image(img_string)

                #     # Down
                #     with column3:
                #         with st.container():
                #         # with st.expander("", expanded = True):
                #             st.subheader(df_to_get_item_for_page['down_item'].iloc[i])
                #             temp_link = gcs_links_df['down_gcs_links'].iloc[i]
                #             if(temp_link == 'no link'):                                                 
                #                 st.image("https://www.colorhexa.com/0e1117.png")
                #             else:
                #                 img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                #                 st.image(img_string)

                #     # Foot
                #     with column4:
                #         with st.container():
                #         # with st.expander("", expanded = True):
                #             st.subheader(df_to_get_item_for_page['foot_item'].iloc[i])
                #             temp_link = gcs_links_df['foot_gcs_links'].iloc[i]
                #             if(temp_link == 'no link'):                                                 
                #                 st.image("https://www.colorhexa.com/0e1117.png")
                #             else:
                #                 img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                #                 st.image(img_string)

                with column1:
                    st.header("Outfit 1")
                with column2:
                    st.header("Outfit 2")
                with column3:
                    st.header("Outfit 3")

                for i, col in zip(top_3_indices, cols):
                    with col:
                        with st.container():
                            temp_link = gcs_links_df['overall_gcs_links'].iloc[i]
                            if(temp_link == 'no link'):                                                 
                                st.image("https://www.colorhexa.com/0e1117.png")
                            else:
                                img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                                st.image(img_string)

                for i, col in zip(top_3_indices, cols):
                    with col:
                        with st.container():
                            temp_link = gcs_links_df['up_gcs_links'].iloc[i]
                            if(temp_link == 'no link'):                                                 
                                st.image("https://www.colorhexa.com/0e1117.png")
                            else:
                                img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                                st.image(img_string)

                for i, col in zip(top_3_indices, cols):
                    with col:
                        with st.container():
                            temp_link = gcs_links_df['down_gcs_links'].iloc[i]
                            if(temp_link == 'no link'):                                                 
                                st.image("https://www.colorhexa.com/0e1117.png")
                            else:
                                img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                                st.image(img_string)

                for i, col in zip(top_3_indices, cols):
                    with col:
                        with st.container():
                            temp_link = gcs_links_df['foot_gcs_links'].iloc[i]
                            if(temp_link == 'no link'):                                                 
                                st.image("https://www.colorhexa.com/0e1117.png")
                            else:
                                img_string = 'https://storage.cloud.google.com/dsci551_storage/' + temp_link
                                st.image(img_string)


    
                




            except Exception as e:
                st.warning("Please add more items to your wardrobe")
                print(e)

