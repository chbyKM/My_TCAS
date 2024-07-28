from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.graph_objects as go
import pandas as pd
import re
import plotly.express as px
import json
from urllib.request import urlopen

def extract_number(s):
    number = re.findall(r'\d+', s)
    return int(number[0]) if number else 0

def extract_and_sum(filtered_df, selected_cols):
    round_1 = [extract_number(str(s)) for s in filtered_df[selected_cols[0]].tolist()]
    round_2 = [extract_number(str(s)) for s in filtered_df[selected_cols[1]].tolist()]
    round_3 = [extract_number(str(s)) for s in filtered_df[selected_cols[2]].tolist()]
    round_4 = [extract_number(str(s)) for s in filtered_df[selected_cols[3]].tolist()]

    total = [a + b + c + d for a, b, c, d in zip(round_1, round_2, round_3, round_4)]
    return [f'รับ {x} คน' for x in total]

app = Dash(__name__)

# Load university data
data_file = "university.csv"
df = pd.read_csv(data_file)

# Calculate totals and prepare data
selected_cols = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
df['ทั้งหมด'] = extract_and_sum(df, selected_cols)
filtered_df = df[['ชื่อหลักสูตร', 'university', 'ค่าใช้จ่าย'] + selected_cols]
cleaned_df = filtered_df.rename(columns={"university": "มหาวิทยาลัย"})

# Load location data
location_data_file = "assets/university_location_clean.csv"
location_df = pd.read_csv(location_data_file)

# Ensure 'location_df' contains the required columns
location_df = location_df.rename(columns={
    "ชื่อสถานศึกษา": "มหาวิทยาลัย", 
    "จังหวัด": "จังหวัด", 
    "LATITUDE": "latitude", 
    "LONGITUDE": "longitude"
})

# Create a mapping of universities to provinces, latitude, and longitude
uni_dict = {
    uni: {
        'จังหวัด': province,
        'latitude': lat,
        'longitude': lon
    } for uni, province, lat, lon in zip(location_df['มหาวิทยาลัย'], location_df['จังหวัด'], location_df['latitude'], location_df['longitude'])
}

# Convert uni_dict to a DataFrame
uni_df = pd.DataFrame.from_dict(uni_dict, orient='index').reset_index().rename(columns={'index': 'มหาวิทยาลัย'})

# Merge cleaned_df with uni_df to add the additional columns
cleaned_df = pd.merge(cleaned_df, uni_df, on='มหาวิทยาลัย', how='left')

# Load Thailand GeoJSON
with urlopen('https://raw.githubusercontent.com/apisit/thailand.json/master/thailandWithName.json') as response:
    thai_province = json.load(response)

# Initial choropleth map
fig_map = px.choropleth_mapbox(
    cleaned_df,
    geojson=thai_province,
    locations='จังหวัด',
    featureidkey="properties.PROVINCE_NAME",
    color='จังหวัด',
    color_discrete_sequence=["lightgrey"],  # Default color
    mapbox_style="carto-positron",
    center={"lat": 15.87, "lon": 100.9925},
    zoom=5,
    title='แผนที่ประเทศไทย',
    template='plotly_dark'
)

fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

app.layout = html.Div([
    html.H1(
        "My TCAS Dashboard (หลักสูตรวิศวกรรม)", 
        style={'textAlign': 'center', 'margin-top': '50px', 'margin-bottom': '20px'}
    ),
    html.Div(
        [html.Label("มหาวิทยาลัย", style={'font-weight': 'bold'})],
        style={'margin-bottom': '10px'}
    ),
    html.Div(
        [dcc.Dropdown(
            id='dropdown-selection',
            options=[{'label': university, 'value': university} for university in cleaned_df['มหาวิทยาลัย'].unique()],
            value='มหาวิทยาลัยสงขลานครินทร์ หาดใหญ่'  # default
        )],
        style={'margin-bottom': '30px'}
    ),
    dash_table.DataTable(
        id='data_table',
        columns=[{"name": col, "id": col} for col in cleaned_df.columns if col not in ['latitude', 'longitude']],
        data=cleaned_df.to_dict('records'),
        page_size=5,
        style_cell={'textAlign': 'left'},
        style_data={'whiteSpace': 'normal', 'height': '50px', 'lineHeight': 'auto'},
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(50,50,50)', 'color': 'white', 'textAlign': 'center'}
    ),
    dcc.Graph(id='bar_chart'),
    dcc.Graph(id='map', figure=fig_map)
])

@app.callback(
    [Output('data_table', 'data'),
     Output('bar_chart', 'figure'),
     Output('map', 'figure')],
    Input('dropdown-selection', 'value')
)
def update_content(selected_university):
    filtered_university_df = cleaned_df[cleaned_df["มหาวิทยาลัย"] == selected_university]
    
    if filtered_university_df.empty:
        return [], go.Figure(), fig_map  # Return an empty figure if no data is found
    
    # Prepare data for the bar chart
    rounds = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
    numbers = [extract_number(filtered_university_df[round].iloc[0]) for round in rounds]
    
    # Create the bar chart
    fig = go.Figure(data=[go.Bar(
        x=rounds,
        y=numbers,
        marker_color='indianred'
    )])
    fig.update_layout(
        title=f'จำนวนที่รับในแต่ละรอบสำหรับ {selected_university}',
        xaxis_title='รอบ',
        yaxis_title='จำนวนที่รับ',
        template='plotly_dark'
    )

    # Prepare data for the updated map
    selected_province = filtered_university_df['จังหวัด'].iloc[0]
    map_data = cleaned_df.copy()
    map_data['highlight'] = map_data['จังหวัด'].apply(lambda x: 'selected' if x == selected_province else 'other')
    
    fig_map = px.choropleth_mapbox(
        map_data,
        geojson=thai_province,
        locations='จังหวัด',
        featureidkey="properties.PROVINCE_NAME",
        color='highlight',
        color_discrete_map={'selected': 'red', 'other': 'lightgrey'},  # Highlight selected province
        mapbox_style="carto-positron",
        center={"lat": 15.87, "lon": 100.9925},
        zoom=5,
        title='แผนที่ประเทศไทย',
        template='plotly_dark'
    )

    fig_map.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

    return filtered_university_df.to_dict('records'), fig, fig_map

if __name__ == "__main__":
    app.run(debug=True)
