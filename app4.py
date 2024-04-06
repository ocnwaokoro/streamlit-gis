import streamlit as st
import pandas as pd
import folium
from streamlit_folium import st_folium

APP_TITLE = "Fraud and Identity Theft Report"
APP_SUB_TITLE = "Source: Federal Trade Commission"

def display_fraud_facts(df, year, quarter, state_name, report_type, field_name, metric_title, number_format='${:,}',is_median=False):
    df = df[(df["Year"]==year) & 
            (df["Quarter"]==quarter) & 
            (df["Report Type"]==report_type)]
    if state_name:
        df = df[df["State Name"]==state_name]
    df = df.drop_duplicates()
    if is_median:
        total = df[field_name].sum() / len(df) if len(df) else 0
    else:
        total = df[field_name].sum()
    st.metric(metric_title, number_format.format(round(total)))
    
    
def display_map(df, year, quarter):
    df = df[(df['Year'] == year) & (df['Quarter'] == quarter)]
    _ = '''
    Ghana's own
    zoom = 7
    map = folium.Map(location=[7.9465,-1.0232], 
                    zoom_start=zoom, 
                    tiles="CartoDB Positron")
    '''
    map = folium.Map(location=[38,-96.5], 
                     zoom_start=4, 
                     max_zoom=4, 
                     min_zoom=2,
                     tiles="CartoDB Positron")
    
    choropleth = folium.Choropleth(
        geo_data="data/US/us-state-boundaries.geojson",
        data=df,
        columns=("State Name","State Total Reports Quarter"),
        key_on="feature.properties.name",
        line_opacity=0.8,
        highlight=True
    )
    choropleth.geojson.add_to(map)

    df = df.set_index("State Name")

    for feature in choropleth.geojson.data["features"]:
        state_name = feature["properties"]["name"]
        feature["properties"]["population"] = "Population: " + "{:,}".format(df.loc[state_name, 'State Pop'].iloc[0] if state_name in list(df.index) else 0)
        feature["properties"]["per_100k"] = "Reports/100K People: " + "{:,}".format(round(df.loc[state_name, 'Reports per 100K-F&O together'].iloc[0]) if state_name in list(df.index) else 0)
    
    choropleth.geojson.add_child(
        folium.features.GeoJsonTooltip(['name', "population", "per_100k"],
        labels=False)
    )
    st_map = st_folium(map, width=700, height=450)
    st.write(st_map["last_active_drawing"])
    pass

def main():
    # config for setting app title
    st.set_page_config(APP_TITLE)
    st.title(APP_TITLE)
    st.caption(APP_SUB_TITLE)

    # LOAD DATA
    df_contintental = pd.read_csv("data/US/AxS-Continental_Full Data_data.csv")
    df_fraud = pd.read_csv("data/US/AxS-Fraud Box_Full Data_data.csv")
    df_median = pd.read_csv("data/US/AxS-Median Box_Full Data_data.csv")
    df_loss = pd.read_csv("data/US/AxS-Losses Box_Full Data_data.csv")
    
    year = 2020
    quarter = 1
    state_name = ""
    report_type = "Fraud"
    
    # DISPLAY FILTERS & MAP
    display_map(df_contintental, year, quarter)

    # DISPLAY METRICS
    st.subheader(f'{state_name} {report_type} Facts')
    col1, col2, col3 = st.columns(3)
    with col1:
        field_name = "State Fraud/Other Count"
        metric_title = f"Number of {report_type} Reports"
        number_format='{:,}'
        display_fraud_facts(df_fraud, year, quarter, state_name, report_type, field_name, metric_title, number_format)
    with col2:
        field_name = "Overall Median Losses Qtr"
        metric_title = f"Median $ Loss"
        number_format='${:,}'
        display_fraud_facts(df_median, year, quarter, state_name, report_type, field_name, metric_title, number_format, is_median=True)
    with col3:
        field_name = "Total Losses"
        metric_title = f"Total $ Loss"
        number_format='${:,}'
        display_fraud_facts(df_loss, year, quarter, state_name, report_type, field_name, metric_title, number_format)

if __name__ == "__main__":
    main()
