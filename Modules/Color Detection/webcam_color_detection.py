import webcolors
import cv2
import os
import io
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

cam = cv2.VideoCapture(0)
cam.set(cv2.CAP_PROP_AUTO_EXPOSURE, 3) # Setting exposure to fixed value
#cam.set(cv2.CAP_PROP_EXPOSURE, 1)
cv2.namedWindow("Capture Image of Clothing Item")
fgbg = cv2.createBackgroundSubtractorMOG2()
main_color = ''
while True:
    ret, frame = cam.read()
    cv2.putText(frame, "Color = " + main_color, 
                (220, 30), cv2.FONT_HERSHEY_SIMPLEX, 
                1, (0, 255, 255))
    if not ret:
        print("failed to grab frame")
        break
    cv2.imshow("Capture Image of Clothing Item", frame)

    k = cv2.waitKey(1)
    if k%256 == 27:
        # ESC pressed
        print("Escape hit, closing...")
        break
    elif k%256 == 32:
        # SPACE pressed
        img_name = "find_color_frame.png"
        cv2.imwrite(img_name, frame)
        # Image captured for finding color
        print("Frame Captured")
        
        
        temp_img = cv2.imread("find_color_frame.png")
        temp_img = cv2.cvtColor(temp_img, cv2.COLOR_BGR2RGB)
        # Average color across image. Need to make this region specific
        average = temp_img.mean(axis=0).mean(axis=0)
        pixels = np.float32(temp_img.reshape(-1, 3))
        # Top 5 colors
        n_colors = 5
        criteria = (cv2.TERM_CRITERIA_EPS + cv2.TERM_CRITERIA_MAX_ITER, 200, .1)
        flags = cv2.KMEANS_RANDOM_CENTERS

        _, labels, palette = cv2.kmeans(pixels, n_colors, None, criteria, 10, flags)
        _, counts = np.unique(labels, return_counts=True)

        # Finds most dominant color
        dominant = palette[np.argmax(counts)].astype(int)
        main_color = get_colour_name(dominant)
        font = cv2.FONT_HERSHEY_SIMPLEX
        print(main_color)


cam.release()
cv2.destroyAllWindows()