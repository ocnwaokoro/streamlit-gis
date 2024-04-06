import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
import numpy as np
import geopandas
import sys
import rasterio
import rasterio.plot

'''
st.set_option('deprecation.showPyplotGlobalUse', False)
world = geopandas.read_file(geopandas.datasets.get_path("naturalearth_lowres"))
germany = world[world.name=="Germany"]
germany.plot()
plt.axis("off")
st.pyplot(plt)
'''

fig, ax = plt.subplots(figsize=(15, 15))
raster = rasterio.open("data/gha_pd_2020_1km_UNadj.tif")
rasterio.plot.show(raster, ax=ax)
st.pyplot(plt)


