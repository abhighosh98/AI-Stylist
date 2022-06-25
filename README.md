# AI Stylist
AI Stylist is for people with color blindness which will help them select clothes from their wardrobe and give them the ability to dress better by overcoming the drawbacks due to color blindness. It can also help others save precious time that is wasted daily on choosing an outfit. 

![Website](https://drive.google.com/uc?export=view&id=1y1hjBTBdiUDiUQFS_5HL4ZVr5QOSvDj9)

# Architecture 
![Architecture](https://drive.google.com/uc?export=view&id=1-VTYLb5dPyI5aCCsY_2g_ZFPBlYmyrjO)

* Web Interface communicating with Firestore: The app has been built using Streamlit which natively does not support multipage apps but the Hydralit allows this functionality. The landing page allows new users to sign up and existing users to login. User data, image tags, urls are stored on Firestore and images are stored on GCS

![Sign in and sign up](https://drive.google.com/uc?export=view&id=11ibX_g_jETPzq9lWh0zdTFvDwna0VU7q)

* Personal Wardrobe: This personal wardrobe has images of the user’s clothes that they upload. Images and tags are stored in Firestore and retrieved when the user opens the “Digital Wardrobe” page. This part of the web application loads images from GCS for a user and displays it in an image carousel. 

![Personal Wardrobe](https://drive.google.com/uc?export=view&id=1Js0oym7FSscqfa_PhlbpBiQuFUm9WUZY)

* Module for recognising color: As the color blind users will go out to purchase new clothing items, or select from their current physical wardrobe, they can use this module to understand what color they are looking at (in case there is any uncertainty). This module uses OpenCV to perform image processing on the image to convert BGR to RGB channels and get the numpy array in the correct shape. After this the numpy array is fed to a KMeans model which creates 5 major color clusters for a given image. The most dominant of these clusters is returned as the color of the image.

![Color recognition](https://drive.google.com/uc?export=view&id=1cO6l_gALSW7XZSeIS9KHI7uiqMKDAGVE)

In the image, the user showed a specific color using a phone display. The recognised color is shown below the camera feed. 
