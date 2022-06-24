from hydralit import HydraApp
import streamlit as st
from sample_app import MySampleApp
from small_app import MySmallApp



if __name__ == '__main__':

    #this is the host application, we add children to it and that's it!
    app = HydraApp(title='Sample Hydralit App',favicon="🐙")
  
    #add all your application classes here
    app.add_app("Small App", icon="🏠", app=MySmallApp())
    app.add_app("Sample App",icon="🔊", app=MySampleApp())

    #run the whole lot
    app.run()