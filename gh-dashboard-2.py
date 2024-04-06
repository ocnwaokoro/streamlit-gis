import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium
import branca

APP_TITLE = "Ghana Health Access & Population Report"
APP_SUB_TITLE = "Source: Ghana Statistical Service & Clinton Health Access Initiative"

def display_region_facts(df, region, metric_title, number_format='{:,}', is_pop=False):
        df = df[df["Region_202"]==region]
        if is_pop:
            total = df["VALUE"].sum()
        else:
            total = len(df)
        st.metric(metric_title, number_format.format(round(total)))

def display_map(df):
    map = folium.Map(location=[7.9465,-1.0232], 
                     zoom_start=7, 
                     tiles="CartoDB Positron")
    
    min_scale = min(df["population"])
    max_scale = max(df["population"])
    cmap = branca.colormap.linear.YlGn_09.scale(min_scale, max_scale)
    cmap = cmap.to_step(index=[min_scale,
                               min_scale+(max_scale-min_scale)*1/4, 
                               min_scale+(max_scale-min_scale)*2/4,
                               min_scale+(max_scale-min_scale)*3/4, 
                               max_scale])
    cmap.caption = "Population"
    cmap.add_to(map)

    pop_dict = df.set_index("region")["population"]

    regionPolygons= folium.GeoJson(
        data="data/GH/gh-regions-polygons.geojson",
        name="regions",
        marker=folium.Circle(radius=1028, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
        tooltip=folium.GeoJsonTooltip(fields=["Region_202"], labels=False),
        overlay=True,
        style_function=lambda feature: {
        "fillColor": cmap(pop_dict[feature["properties"]["Region_202"]]),
        "color": "black",
        "weight": 1,
        "fillOpacity": 0.9,
        },
        zoom_on_click=True,
    )
    regionPolygons.add_to(map)

    folium.GeoJson(
        data="data/GH/gh-facilities-per-district.geojson",
        marker=folium.Circle(radius=1028, fill_color="orange", fill_opacity=0.4, color="black", weight=1),
        tooltip=folium.GeoJsonTooltip(fields=["FACILITY"], labels=False),
        overlay=True,
    ).add_to(map)
    folium.LayerControl().add_to(map)

    df = df.set_index("region")
    for feature in regionPolygons.data["features"]:
        region = feature["properties"]["Region_202"]
        feature["properties"]["region"] = region
        feature["properties"]["region_title"] = f"{region} Region"
        feature["properties"]["population"] = "Population: " + "{:,}".format(round(df.loc[region, "population"]) if region in list(df.index) else 0)
        feature["properties"]["num_facilities"] = "# of Health Facilities: " + "{:,}".format(round(df.loc[region, "facilities"]) if region in list(df.index) else 0)
    regionPolygons.add_child(
        folium.features.GeoJsonTooltip(["region_title", "population", "num_facilities"],
        labels=False)
    )

    st_map = st_folium(map, width=550, height=700)
    region = ""
    if (st_map["last_active_drawing"] and 
        (st_map["last_clicked"] == st_map["last_object_clicked"])):
        region = st_map["last_active_drawing"]["properties"]["Region_202"]        
    return region

def main():
    # config for setting app title
    st.set_page_config(APP_TITLE, layout="wide")
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    column1, column2 = st.columns(2)

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
    with column1:
        region = display_map(df_fac_pop_reg)

    # DISPLAY METRICS
    with column2:
        if region:
            st.subheader(f'{region} Region Facts')
            col1, col2 = st.columns(2)
            with col1:
                metric_title = f"Number of Health Facilities"
                st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"facilities"])))
            with col2:
                metric_title = f"Population"
                st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg.loc[list(df_fac_pop_reg["region"]).index(region),"population"])))
            st.write(df_fac_reg
                    [df_fac_reg["Region_202"]==region]
                    [["FACILITY","REGION","DISTRICT","OWNERSHIP"]]
                    .reset_index(drop=True)
                    .reset_index(drop=False)
                    .rename(columns={'index': 'new_index'})
                    .assign(new_index=lambda x: x['new_index'] + 1)
                    .set_index("new_index")
                    .rename_axis(None, axis=0))
        else:
            st.subheader("Overall Facts")
            col1, col2 = st.columns(2)
            with col1:
                metric_title = f"Total Number of Health Facilities"
                st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg["facilities"].sum())))
            with col2:
                metric_title = f"Total Population"
                st.metric(metric_title, '{:,}'.format(round(df_fac_pop_reg["population"].sum())))
            st.write(df_fac_reg
                [["FACILITY","REGION","DISTRICT","OWNERSHIP"]]
                .sample(frac=1)
                .reset_index(drop=True)
                .reset_index(drop=False)
                .rename(columns={'index': 'new_index'})
                .assign(new_index=lambda x: x['new_index'] + 1)
                .set_index("new_index")
                .rename_axis(None, axis=0)
            )
        
if __name__ == "__main__":
    main()