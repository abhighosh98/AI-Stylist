import streamlit as st
from datetime import datetime
from google.cloud import firestore
from hydralit import HydraApp
import pandas as pd
import time
from hydralit import HydraHeadApp

class dummyModule(HydraHeadApp):

        def run(self):
            print("Used Dummy")