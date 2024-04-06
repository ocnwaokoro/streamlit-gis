import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = "Ghana Health & Population Report"
APP_SUB_TITLE = "Source: Ghana Statistical Service & Clinton Health Access Initiative"

def display_region_facts(df, region, metric_title, number_format='{:,}',is_pop=False):
        df = df[df["Region_202"]==region]
        if is_pop:
            total = df["VALUE"].sum()
        else:
            total = len(df)
        st.metric(metric_title, number_format.format(round(total)))

def display_map(df):
    map = folium.Map(location=[7.9465,-1.0232], 
                     zoom_start=7, 
                     max_zoom=7, 
                     min_zoom=7,
                     zoom_control=False,
                     tiles="CartoDB Positron")
    choropleth = folium.Choropleth(
        geo_data="data/GH/gh-regions-polygons.geojson",
        data=df,
        columns=("region","population","facilities"),
        key_on="feature.properties.Region_202",
        overlay=True,
        line_opacity=0.8,
        fill_color="YlGn",
        fill_opacity=1,
        highlight=True,
        dragging=False,
        legend_name="Mapa",
        control=False,
        bins=5
    )
    choropleth.geojson.add_to(map)

    df = df.set_index("region")

    for feature in choropleth.geojson.data["features"]:
        region = feature["properties"]["Region_202"]
        feature["properties"]["region"] = region
        feature["properties"]["region_title"] = f"{region} Region"
        feature["properties"]["population"] = "Population: " + "{:,}".format(round(df.loc[region, "population"]) if region in list(df.index) else 0)
        feature["properties"]["num_facilities"] = "# of Health Facilities: " + "{:,}".format(round(df.loc[region, "facilities"]) if region in list(df.index) else 0)
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(["region_title", "population", "num_facilities"],
        labels=False)
    )
    st_map = st_folium(map, width=700, height=600)
    region = ""
    if (st_map["last_active_drawing"] and (st_map["last_clicked"] == st_map["last_object_clicked"])):
        region = st_map["last_active_drawing"]["properties"]["region"]        
    return region

def main():
    # config for setting app title
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # LOAD DATA
    # df_fac_dis = pd.read_csv("data/GH/gh-facilities-per-district.csv")
    df_fac_reg = pd.read_csv("data/GH/gh-facilities-per-region.csv")
    # df_pop_dis = pd.read_csv("data/GH/gh-population-count-per-district.csv")
    df_pop_reg = pd.read_csv("data/GH/gh-population-count-per-region.csv")

    df_fac_pop_reg = pd.DataFrame()
    df_fac_pop_reg["region"] = df_fac_reg["Region_202"].unique()
    df_fac_pop_reg = df_fac_pop_reg.dropna()
    for region in df_fac_pop_reg["region"]:
        pop = df_pop_reg[df_pop_reg["Region_202"]==region]["VALUE"].sum()
        df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"population"] = pop
        fac = len(df_fac_reg[df_fac_reg["Region_202"]==region])
        df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"facilities"] = fac
           
    # DISPLAY FILTERS & MAP
    region = display_map(df_fac_pop_reg)

    # DISPLAY METRICS
    if region:
        st.subheader(f'{region} Region Facts')
        col1, col2 = st.columns(2)
        with col1:
            metric_title = f"Number of Health Facilities"
            st.metric(metric_title, '{:,}'.format(df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"facilities"]))
        with col2:
            metric_title = f"Population"
            st.metric(metric_title, '{:,}'.format(df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"population"]))
        st.write((df_fac_reg[df_fac_reg["Region_202"]==region])
                 .loc[:, df_fac_reg.columns[:-7]]
                 .drop(["SUBDIS","GHS_SUBDIS","LOCALITY","GHS_FACILITY","TYPE"]))
    else:
        st.subheader("Total Facts")
        col1, col2 = st.columns(2)
        with col1:
            metric_title = f"Total Number of Health Facilities"
            st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg["facilities"].sum())))
        with col2:
            metric_title = f"Total Population"
            st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg["population"].sum())))
        st.write((df_fac_reg
                  .loc[:, df_fac_reg.columns[:-7]])
                  .sample(frac=1)
                  .drop(["SUBDIS","GHS_SUBDIS","LOCALITY","GHS_FACILITY","TYPE"]))

if __name__ == "__main__":
    main()
