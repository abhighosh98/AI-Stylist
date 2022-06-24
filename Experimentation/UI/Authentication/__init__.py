import streamlit as st
import streamlit.components.v1 as components
from hydralit import HydraHeadApp
from google.cloud import storage
import os
import io
import numpy as np
from hydralit import HydraHeadApp
import streamlit as st
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


class wardrobe(HydraHeadApp):
        def run(self):
            # if __name__ == "__main__":
            def main():
                try:
                    firestore_object = list(users_ref.where('username', '==', st.session_state.current_username).stream())
                    for d in firestore_object:
                                username_table_id = d.id
                                username_related_data = d.to_dict()
                except:
                    print(st.session_state)
                
                # Creating links
                # all_items_links = []
                # for user_related_data_keys in list(username_related_data.keys()):
                #     if(user_related_data_keys.endswith("links")):
                #         all_items_links.append(user_related_data_keys)
                items_image_links = username_related_data['overall_gcs_links'] + username_related_data['up_gcs_links'] + username_related_data['down_gcs_links'] + username_related_data['foot_gcs_links']
                items_image_links = ['https://storage.cloud.google.com/dsci551_storage/' + x for x in items_image_links if type(x) != float]

                # Running Carousel
                st.title('My WardRobe')
                imageCarouselComponent = components.declare_component("image-carousel-component", path="frontend/public")
                # link = "https://storage.cloud.google.com/dsci551_storage/test_images/"
                # imageUrls = []
                # for i in [0,1,2,3,4,5,8,9,10,11]:
                #     imageUrls.append(link+str(i)+".jpg")
                # print(imageUrls)
                selectedImageUrl = imageCarouselComponent(imageUrls = items_image_links, 
                height=300,
                width=100)

                # if selectedImageUrl is not None:
                #     st.image(selectedImageUrl)
                print(items_image_links)
                # print(imageUrls)
            main()