import streamlit as st
import pandas as pd
import numpy as np

df = pd.DataFrame( 
    np.random.randn(1000, 2) / [50, 50] + [37.76, -122.4],
    columns=['lat', 'lon'])


df2 = pd.read_csv("data/gh_health_facilities.csv")
st.map(df2)
df3 = pd.read_csv("data/GSS_health_facilities_with_coordinates.csv")
st.map(df3)