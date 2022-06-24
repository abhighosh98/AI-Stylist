import streamlit as st
from datetime import datetime
from google.cloud import firestore
from hydralit import HydraApp
import pandas as pd
import time
from hydralit import HydraHeadApp
import webcolors
import cv2 
import numpy as np

def closest_colour(requested_colour):
    min_colours = {}
    for key, name in webcolors.CSS3_HEX_TO_NAMES.items():
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




class LoginModule(HydraHeadApp):

        def run(self):
            # Open CV part
            img_file_buffer_color = st.camera_input("Take a picture")

            if img_file_buffer_color is not None:
                # To read image file buffer with OpenCV:
                bytes_data = img_file_buffer_color.getvalue()
                cv2_img = cv2.imdecode(np.frombuffer(bytes_data, np.uint8), cv2.IMREAD_COLOR)

                # Check the type of cv2_img:
                # Should output: <class 'numpy.ndarray'>
                # st.write(type(cv2_img))

                # Check the shape of cv2_img:
                # Should output shape: (height, width, channels)
                # st.write(cv2_img.shape)
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
                font = cv2.FONT_HERSHEY_SIMPLEX
                # print(main_color)
                st.write("Detected Color is ",main_color)




