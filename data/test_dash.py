from dash import Dash, dcc, html, Input, Output, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import re

def extract_number(s):
    """Extract the first number from a string."""
    s = str(s)  # Ensure input is a string
    number = re.findall(r'\d+', s)
    return int(number[0]) if number else 0

def extract_and_sum(filtered_df, selected_cols):
    """Calculate the total for each row across selected columns."""
    round_1 = [extract_number(str(s)) for s in filtered_df[selected_cols[0]].fillna('').tolist()]
    round_2 = [extract_number(str(s)) for s in filtered_df[selected_cols[1]].fillna('').tolist()]
    round_3 = [extract_number(str(s)) for s in filtered_df[selected_cols[2]].fillna('').tolist()]
    round_4 = [extract_number(str(s)) for s in filtered_df[selected_cols[3]].fillna('').tolist()]
    return [a + b + c + d for a, b, c, d in zip(round_1, round_2, round_3, round_4)]

# Initialize the Dash app
app = Dash(__name__)

# Load data
data_file = "university.csv"
df = pd.read_csv(data_file)

# Define the columns and process data
selected_cols = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
df['ทั้งหมด'] = extract_and_sum(df, selected_cols)

# Filter and clean data
filtered_df = df[['ชื่อหลักสูตร', 'university', 'ค่าใช้จ่าย', 'ทั้งหมด'] + selected_cols]
cleaned_df = filtered_df.rename(columns={"university": "มหาวิทยาลัย"})

# Load location data
location_df = pd.read_csv('university_locations.csv')
location_df = location_df.rename(columns={"university": "มหาวิทยาลัย", "province": "จังหวัด"})

# Create dictionary for university locations
uni_dict = {uni: province for uni, province in zip(location_df['มหาวิทยาลัย'].tolist(), location_df['จังหวัด'].tolist())}
uni_dict_keys = list(uni_dict.keys())

# Add province information to the cleaned dataframe
cleaned_df['จังหวัด'] = cleaned_df['มหาวิทยาลัย'].apply(lambda x: uni_dict.get(x, ""))

# Reorder columns
last_column = cleaned_df.pop('จังหวัด')
cleaned_df.insert(2, 'จังหวัด', last_column)

# Load geojson file for the map
with open('assets/thailand_provinces.geojson', 'r', encoding='utf-8') as f:
    geojson = json.load(f)

# Define the app layout
app.layout = html.Div([
    html.H1(
        "My TCAS Dashboard (หลักสูตรวิศวกรรม)", 
        style={'textAlign': 'center', 'margin-top': '50px', 'margin-bottom': '20px'}
    ),
    html.Div(
        [html.Label("มหาวิทยาลัย", style={'font-weight':'bold'})],
        style={'margin-bottom': '10px'}
    ),
    html.Div(
        [dcc.Dropdown(
            id='dropdown-selection',
            options=[{'label': university, 'value': university} for university in cleaned_df['มหาวิทยาลัย'].unique()],
            value='มหาวิทยาลัยสงขลานครินทร์ หาดใหญ่'  # Default value
        )],
        style={'margin-bottom': '30px'}
    ),
    dash_table.DataTable(
        id='data_table',
        columns=[{"name": col, "id": col} for col in cleaned_df.columns],
        data=cleaned_df.to_dict('records'),
        page_size=5,
        style_cell={'textAlign': 'left'},
        style_data={'whiteSpace': 'normal', 'height': '50px', 'lineHeight': 'auto'},
        style_table={'overflowX': 'auto'},
        style_header={'backgroundColor': 'rgb(50,50,50)', 'color': 'white', 'textAlign': 'center'},
    ),
    dcc.Graph(id='bar-chart', style={'width': '100%', 'height': '400px'}),
    dcc.Graph(id='map-content', style={'width': '100%', 'height': '600px'})
])

@app.callback(
    [Output('data_table', 'data'),
     Output('map-content', 'figure'),
     Output('bar-chart', 'figure')],
    [Input('dropdown-selection', 'value')]
)
def update_table_map_and_bar_chart(selected_university):
    # Filter the data for the selected university
    filtered_university_df = cleaned_df[cleaned_df["มหาวิทยาลัย"] == selected_university]

    # Aggregate intake data for the selected university
    aggregated_data = filtered_university_df[selected_cols].applymap(extract_number).sum()

    # Create choropleth map
    fig_map = px.choropleth(
        cleaned_df,
        geojson=geojson,
        locations='จังหวัด',
        featureidkey="properties.name",
        color='ทั้งหมด',
        color_continuous_scale="YlOrRd",
        range_color=[cleaned_df['ทั้งหมด'].min(), cleaned_df['ทั้งหมด'].max()],
        labels={'ทั้งหมด':'จำนวนรับทั้งหมด'},
        projection="mercator",
    )
    fig_map.update_geos(fitbounds="locations", visible=True)
    fig_map.update_layout(
        title={
            'text': "แผนที่มหาวิทยาลัย",
            'font': {'size':20, 'weight':'normal'},
            'pad':{'t':-40},
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        coloraxis_colorbar={
            'title': 'จำนวนรับทั้งหมด (คน)',
            'x': 1.05,
            'len': 0.8
        },
    )

    # Create bar chart with aggregated intake data for the selected university
    fig_bar = go.Figure()
    for round_name in selected_cols:
        fig_bar.add_trace(go.Bar(
            x=[round_name],
            y=[aggregated_data[round_name]],
            name=round_name
        ))
    
    fig_bar.update_layout(
        title=f"จำนวนที่รับรวมในแต่ละรอบของ {selected_university}",
        xaxis_title="รอบการรับ",
        yaxis_title="จำนวนที่รับ",
        barmode='group'
    )

    # Return the table data, map figure, and bar chart figure
    return filtered_university_df.to_dict('records'), fig_map, fig_bar

if __name__ == "__main__":
    app.run(debug=True)
