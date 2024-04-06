import streamlit as st
import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import rasterio
import rasterio.plot

# Load raster data
raster = rasterio.open("data/gha_pd_2020_1km_UNadj.tif")
data = raster.read(1)  # Assuming single band raster

# Compute quantiles
quantiles = np.percentile(data, [x/2.55 for x in list(range(1,230))])

# Define custom colormap
colors = plt.cm.viridis(np.linspace(0, 1, len(quantiles)))
cmap = matplotlib.colors.ListedColormap(colors)

# Plot
fig, ax = plt.subplots(figsize=(15, 15))
rasterio.plot.show(raster, ax=ax, cmap=cmap)

# plt.axis("off")
print(colors)

# Show plot in Streamlit
st.pyplot(plt)