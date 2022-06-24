from google.cloud import vision
from google.cloud import storage
# Line throws error as it was replaced in v2
# from google.cloud.vision import types 
from google.cloud.vision_v1 import types
import os
import io
import numpy as np
import pandas as pd
import webcolors
import cv2
# import matplotlib.pyplot as plt
from hydralit import HydraHeadApp
import streamlit as st
import string
import random
from google.cloud import firestore


# Constants
os.environ["GOOGLE_APPLICATION_CREDENTIALS"]="dsci551-2480c-4e478b8d0198.json"
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


def closest_colour(requested_colour):
    min_colours = {}
    for key, name in edited_color_dict.items():
        r_c, g_c, b_c = webcolors.hex_to_rgb(key)
        rd = (r_c - requested_colour[0]) ** 2
        gd = (g_c - requested_colour[1]) ** 2
        bd = (b_c - requested_colour[2]) ** 2
        min_colours[(rd + gd + bd)] = name
    return min_colours[min(min_colours.keys())]

def get_colour_name(requested_colour):
    try:
        closest_name = actual_name = webcolors.rgb_to_name(requested_colour)
    except ValueError:
        closest_name = closest_colour(requested_colour)
        actual_name = None
    return closest_name

outfit_creation = {"up" : ['Dress', 'Shirt', 'Tank top', 'T-shirt'],
                  "down" : ['Skirt', 'Jeans', 'Shorts'],
                  "foot" : ['Heels', 'Shoe' ],
                  "overall" : ['Coat']}

clothing_label_list = ['Shoe',
 'Coat',
 'Dress',
 'Skirt',
 'Tank top',
 'NA',
 'T-shirt',
 'Heels',
 'Shirt',
 'Shorts',
 'Jeans',
 "Nothing Detected"]

edited_color_dict = {'#ffa500': 'orange',
 '#000000': 'black',
 '#0000ff': 'blue',
 '#008000': 'green',
 '#808080': 'gray',
 '#800000': 'maroon',
 '#000080': 'navy',
 '#808000': 'olive',
 '#ff0000': 'red',
 '#008080': 'teal',
 '#ffffff': 'white',
 '#ffff00': 'yellow'}

color_label_list = list(edited_color_dict.values())

correction_hashmap = {"One-piece garment" : "Dress",
                    "Day dress" : "Dress",
                    "High heels" : "Heels",
                    "Sandal" : "Heels",
                    "Basic pump" : "Heels",
                    "Dress shirt" : "Shirt",
                    "Footwear" : "Shoe",
                    "Outdoor shoe" : "Shoe", 
                    "Walking shoe" : "Shoe", 
                    "Sneakers" : "Shoe",
                    "Miniskirt" : "Skirt",
                    "Active tank" : "Tank top",
                    "Undershirt" : "Tank top",
                    "Pants" : "Jeans", 
                    "Blazer" : "Coat",
                    "Leather jacket" : "Coat",
                    "Top" : "T-shirt" # Added later

}
# List of labels label detection api call
required_labels = ["One-piece garment", "Day dress", "Dress", 
                "High heels", "Sandal", "Basic pump", 
                "Jeans",
                "Shirt", "Dress shirt",
                "Shoe", "Footwear", "Outdoor shoe", "Walking shoe", "Sneakers",
                "Shorts",
                "Miniskirt", "Skirt",
                "Active tank", "Undershirt",
                "T-shirt",
                "Coat",
                ]

# List of labels from object localization api call
labels_for_cropping = ["Top",
                    "Dress", "Day dress",
                    "High heels",
                    "Shorts",
                    "Miniskirt",
                    "Coat",
                    "Shoe",
                    "Pants",
                    "Blazer",
                    "Leather jacket"]
img_name = "pic_for_clothing_detection.png"

client = vision.ImageAnnotatorClient()

class DetectItemModule(HydraHeadApp):

        def run(self):
            try:
                firestore_object = list(users_ref.where('username', '==', st.session_state.current_username).stream())
                for d in firestore_object:
                            username_table_id = d.id
                            username_related_data = d.to_dict()
            except:
                print(st.session_state)

            # Open CV part
            st.write("Try to keep only one clothing item in the video frame")
            img_file_buffer = st.camera_input("Take a picture")

            if img_file_buffer is not None:
                # To read image file buffer with OpenCV:
                bytes_data = img_file_buffer.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)                
                cv2.imwrite(img_name, cv2_img)

                # Detect type of clothing item
                height = cv2_img.shape[0]
                width = cv2_img.shape[1]
                with io.open(img_name, 'rb') as image_file:
                    content = image_file.read()
                image = types.Image(content=content)

                # Generate labels and (labels + crop hints)
                all_labels = client.label_detection(image=image)
                labels_and_crops = client.object_localization(image=image).localized_object_annotations
                temp_labels_from_crop_list = [labels_and_crops[i].name for i in range(len(labels_and_crops))] 
                temp_label_list = [all_labels.label_annotations[i].description for i in range(len(all_labels.label_annotations))]
                
                # Combine only the labels from both the sets
                combined_labels = temp_labels_from_crop_list + temp_label_list
                for dup in list(correction_hashmap.keys()):
                    if(dup in combined_labels):
                        combined_labels[combined_labels.index(dup)] = correction_hashmap[dup]
                pred_clothing_type = list(np.intersect1d(combined_labels, required_labels))
                if(len(pred_clothing_type) == 0):
                    pred_clothing_type = ["Nothing Detected"]
                else:
                    for detection in labels_and_crops:
                        if(detection.name in labels_for_cropping):
                            x1 = int(detection.bounding_poly.normalized_vertices[0].x * width)
                            y1 = int(detection.bounding_poly.normalized_vertices[0].y * height)
                            x3 = int(detection.bounding_poly.normalized_vertices[2].x * width)
                            y3 = int(detection.bounding_poly.normalized_vertices[2].y * height)
                        
                            cv2.imwrite(img_name, cv2_img[y1 : y3, x1 : x3])
                            break
                print(combined_labels)
                print(pred_clothing_type, "\n\n")

               

                # Detect color
                cv2_img = cv2.cvtColor(cv2_img, cv2.COLOR_BGR2RGB)
                pixels = np.float32(cv2_img.reshape(-1, 3))
                n_colors = 5
                criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
                flags = cv2.KMEANS_RANDOM_CENTERS

                _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
                _, counts = np.unique(labels, return_counts=True)

                # Finds most dominant color
                dominant = palette[np.argmax(counts)].astype(int)
                main_color = get_colour_name(dominant)



                # Change tags if incorrect
                st.text('The detected clothing item was : ' + pred_clothing_type[0])
                final_clothing_type = st.selectbox('Choose the correct item if wrong', clothing_label_list, index = clothing_label_list.index(pred_clothing_type[0]))


                st.text('The detected color was : ' + main_color)
                final_color = st.selectbox('Choose the correct color if wrong', color_label_list, index = color_label_list.index(main_color))

                col1, col2, col3 , col4, col5 = st.columns(5)
                with col3 :
                    upload_to_wardrobe = st.button('Upload')


                if(upload_to_wardrobe):
                    # st.write(st.session_state)
                    if(st.session_state.current_password == ""):
                        st.write("Please login")
                    else:
                        for outfit_creation_key in list(outfit_creation.keys()):
                            if(final_clothing_type in outfit_creation[outfit_creation_key]):
                                clothing_location_on_body = outfit_creation_key
                                break
                        
                        # Uploading to bucket
                        random_string_name = ''.join(random.choices(string.ascii_letters+string.digits,k = length)) + '.png'
                        storage_client = storage.Client.from_service_account_json(path_to_credentials)
                        bucket = storage_client.get_bucket(bucket_name)
                        gcs_full_path = os.path.join(bucket_path, random_string_name)
                        blob = bucket.blob(gcs_full_path)
                        blob.upload_from_filename(img_name)

                        # # # Adding data to firestore
                        username_related_data[clothing_location_on_body + '_gcs_links'].append(gcs_full_path)
                        username_related_data[clothing_location_on_body + '_clothing_items'].append(final_clothing_type)
                        username_related_data[clothing_location_on_body + '_color'].append(final_color)
                        # print(username_related_data)

                        count_of_list_size_from_user_related_data = [len(x) for x in list(username_related_data.values()) if type(x) == list]
                        highest_count_in_list =  max(count_of_list_size_from_user_related_data)

                        for user_related_data_keys in list(username_related_data.keys()):
                            if(type(username_related_data[user_related_data_keys]) == list):
                                while(len(username_related_data[user_related_data_keys]) < highest_count_in_list):
                                    username_related_data[user_related_data_keys].append(np.nan)
                        users_ref.document(username_table_id).update(username_related_data)
                        
                        # st.write(pd.DataFrame(username_related_data))
                        st.success("Image Uploaded")





                                            