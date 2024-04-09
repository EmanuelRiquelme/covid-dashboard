import streamlit as st
import numpy as np
import pandas as pd
import geopandas as gpd
import plotly.express as px

st.set_page_config(page_title="COVID-19 Dashboard")

months_of_year = (
    "January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"
)

us_states = (
    "Alabama", "Alaska", "Arizona", "Arkansas", "California", "Colorado", "Connecticut", "Delaware",
    "Florida", "Georgia", "Hawaii", "Idaho", "Illinois", "Indiana", "Iowa", "Kansas", "Kentucky",
    "Louisiana", "Maine", "Maryland", "Massachusetts", "Michigan", "Minnesota", "Mississippi",
    "Missouri", "Montana", "Nebraska", "Nevada", "New Hampshire", "New Jersey", "New Mexico",
    "New York", "North Carolina", "North Dakota", "Ohio", "Oklahoma", "Oregon", "Pennsylvania",
    "Rhode Island", "South Carolina", "South Dakota", "Tennessee", "Texas", "Utah", "Vermont",
    "Virginia", "Washington", "West Virginia", "Wisconsin", "Wyoming"
)
def preprocessing_df(name_file = 'us-states.csv'):
    df = pd.read_csv(name_file)
    df['date'] = pd.to_datetime(df['date'])
    df['month'] = df['date'].dt.month
    df['year'] = df['date'].dt.year
    return df

def plot_map(df):
    custom_color_scale = ['#FFFFCC', '#FFA500', '#FF4500']
    map_file = 'cb_2018_us_state_500k/cb_2018_us_state_500k.shp'
    
    most_recent_dates = df.groupby(by=['state'])['date'].max()
    most_recent_df =  pd.merge(most_recent_dates, df, on=['state', 'date'], how='left')
   
    world = gpd.read_file(map_file)
    world.columns = ['STATEFP', 'STATENS', 'AFFGEOID', 'GEOID', 'State code', 'state', 'LSAD','ALAND', 'AWATER', 'geometry']
    map  = pd.merge(world,most_recent_df,on= 'state')

    choropleth = px.choropleth(
                        map,
                        locations='State code',
                        color='cases',
                        locationmode="USA-states",
                        color_continuous_scale=custom_color_scale,
                        hover_data={"cases": ":,.0f", "deaths": ":,.0f"},
                        scope="usa")
    
    choropleth.update_layout(title='Cases Over Time')
    return choropleth

def current_dataframe(df):
    most_recent_dates = df.groupby(by=['state'])['date'].max()
    most_recent_dates =  pd.merge(most_recent_dates, df, on=['state', 'date'], how='left')
    most_recent_dates =  most_recent_dates.drop(['date', 'fips','month','year'], axis=1)
    most_recent_dates.columns =  ['State','Cases','Deaths']
    most_recent_dates['Cases'] = most_recent_dates['Cases'].apply(lambda x: f"{x:,}")
    most_recent_dates['Deaths'] = most_recent_dates['Deaths'].apply(lambda x: f"{x:,}")
    return most_recent_dates

def get_cases_and_deaths_graph(month,year,state,df):
    months_to_numbers = {
        "January": 1,
        "February": 2,
        "March": 3,
        "April": 4,
        "May": 5,
        "June": 6,
        "July": 7,
        "August": 8,
        "September": 9,
        "October": 10,
        "November": 11,
        "December": 12
    }

    month_abbr = {
        1: 'Jan',
        2: 'Feb',
        3: 'Mar',
        4: 'Apr',
        5: 'May',
        6: 'Jun',
        7: 'Jul',
        8: 'Aug',
        9: 'Sep',
        10: 'Oct',
        11: 'Nov',
        12: 'Dec'
    }
    
    month = months_to_numbers[month]
    filtered_df = df[(df['state'] == state) & (df['year'] <= year)].reset_index(drop=True)
    
    death_cases_df = filtered_df.groupby(['year', 'month']).agg({'cases': 'max', 'deaths': 'max'}).reset_index()
    death_cases_df['month_abbr'] = death_cases_df['month'].map(month_abbr)
    death_cases_df['year-month'] = death_cases_df['year'].astype(str) + '-' + death_cases_df['month_abbr']

    #cases plot
    fig_cases = px.area(death_cases_df, x="year-month",y='cases')
    fig_cases.update_xaxes(title='Year-Month')
    fig_cases.update_yaxes(title='Cases')
    fig_cases.update_layout(title='Cases Over Time')

    #death plot
    
    fig_deaths = px.area(death_cases_df, x="year-month",y='deaths')
    fig_deaths.update_xaxes(title='Year-Month')
    fig_deaths.update_yaxes(title='Deaths')
    fig_deaths.update_layout(title='Deaths Over Time')

    return fig_cases,fig_deaths

st.markdown("<h1 style='text-align: center;'>COVID-19 in USA</h1>", unsafe_allow_html=True)

df = preprocessing_df()

st.markdown("<h2 style='text-align: center;'>Frequency Map</h2>", unsafe_allow_html=True)
frequency_map = plot_map(df)
st.plotly_chart(frequency_map)

st.markdown("<h2 style='text-align: center;'>Frequency Table</h2>", unsafe_allow_html=True)
frequency_table = current_dataframe(df)
frequency_table= frequency_table.to_html(index=False)

centered_table_html = f"""
<div style="display: flex; justify-content: center;">
    <div style="overflow-x: auto;">
        {frequency_table}
    </div>
</div>
"""

st.markdown(centered_table_html, unsafe_allow_html=True)


st.markdown("<h2 style='text-align: center;'>State-Specific COVID-19 Summary</h2>", unsafe_allow_html=True)

selectbox1, selectbox2,selectbox3 = st.columns(3)

with selectbox1:
    state = st.selectbox('Choose State', us_states)

# Second select box
with selectbox2:
    month = st.selectbox('Choose Month', months_of_year)

with selectbox3:
    year = st.selectbox('Choose Year', (2020,2021,2022,2023))


if st.button('Get Results'):
    fig_cases,fig_deaths = get_cases_and_deaths_graph(month,year,state,df)
    st.plotly_chart(fig_cases)
    st.plotly_chart(fig_deaths)
