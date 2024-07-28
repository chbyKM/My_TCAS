from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
import json
import re

def extract_number(s):
    number = re.findall(r'\d+', s)
    if number:
        return int(number[0])
    else:
        return 0

def extract_and_sum(filtered_df, selected_cols):
    round_1 = [extract_number(str(s)) for s in filtered_df[selected_cols[0]].tolist()]
    round_2 = [extract_number(str(s)) for s in filtered_df[selected_cols[1]].tolist()]
    round_3 = [extract_number(str(s)) for s in filtered_df[selected_cols[2]].tolist()]
    round_4 = [extract_number(str(s)) for s in filtered_df[selected_cols[3]].tolist()]

    total = [f'{a+b+c+d}' for a,b,c,d in zip(round_1, round_2, round_3, round_4)]
    return total

app = Dash(__name__)

data_file = "university.csv"
df = pd.read_csv(data_file)
selected_cols = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
df['ทั้งหมด'] = extract_and_sum(df, selected_cols)

filtered_df = df[['ชื่อหลักสูตร', 'university', 'ค่าใช้จ่าย',
       'ทั้งหมด', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 
       'รอบ 3 Admission', 'รอบ 4 Direct Admission']]
cleaned_df = filtered_df.rename(columns={"university": "มหาวิทยาลัย"})

location_df = pd.read_csv('university_locations.csv')
location_df = location_df.rename(columns={"university": "มหาวิทยาลัย"})
location_df = location_df.rename(columns={"province": "จังหวัด"})

uni_dict = {uni: province for uni, province in zip(location_df['มหาวิทยาลัย'].tolist(), location_df['จังหวัด'].tolist())}
uni_dict_keys = list(uni_dict.keys())
for i in range(len(cleaned_df)):
    if cleaned_df.loc[[i], ['มหาวิทยาลัย']].iloc[0, 0] not in uni_dict_keys:
        cleaned_df.loc[[i], ['จังหวัด']] = ""
    else:
        cleaned_df.loc[[i], ['จังหวัด']] = uni_dict[cleaned_df.loc[[i], ['มหาวิทยาลัย']].iloc[0, 0]]

last_column = cleaned_df.pop('จังหวัด')
cleaned_df.insert(2, 'จังหวัด', last_column) 

with open('assets/thailand_provinces.geojson', 'r', encoding='utf-8') as f:
    geojson = json.load(f)

app.layout = html.Div([
    # Main header
    html.H1(
        "My TCAS Dashboard (หลักสูตรวิศวกรรม)", 
        style={
            'textAlign': 'center', 
            'margin-top': '50px',
            'margin-bottom': '20px'
        },
    ),
    # header of dropdown
    html.Div(
        [
            html.Label(
                "มหาวิทยาลัย",
                style={'font-weight':'bold'}
            ),
        ],
        style={'margin-bottom': '10px'}
    ),
    # dropdown
    html.Div(
        [
            dcc.Dropdown(
                id='dropdown-selection',
                options=[{'label': university, 'value': university} for university in cleaned_df['มหาวิทยาลัย'].unique()],
                value='มหาวิทยาลัยสงขลานครินทร์ หาดใหญ่'  # default
            ),
        ],
        style={'margin-bottom': '30px'}
    ),
    # table
    dash_table.DataTable(
        id='data_table',
        columns=[
            {"name": col, "id": col} for col in cleaned_df.columns
        ],
        data=cleaned_df.to_dict('records'),
        page_size=5,
        style_cell={
            'textAlign': 'left',
        },
        style_data={
            'whiteSpace': 'normal',
            'height': '50px',
            'lineHeight': 'auto'
        },
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(50,50,50)',
            'color': 'white',
            'textAlign': 'center',
        },
    ),
    # bar chart
    dcc.Graph(id='bar-chart', style={'width': '100%', 'height': '400px'}),
    # map
    dcc.Graph(id='map-content', style={'width': '100%', 'height': '600px'})
])

@app.callback(
    [
        Output('data_table', 'data'),
        Output('map-content', 'figure'),
        Output('bar-chart', 'figure')
    ],
    [
        Input('dropdown-selection', 'value')
    ]
)
def update_table_map_and_bar_chart(selected_university):
    filtered_university_df = cleaned_df[cleaned_df["มหาวิทยาลัย"] == selected_university]

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

    # Create bar chart
    fig_bar = go.Figure()
    for round_name in selected_cols:
        fig_bar.add_trace(go.Bar(
            x=[round_name],
            y=[extract_number(str(filtered_university_df[round_name].values[0]))],
            name=round_name
        ))
    
    fig_bar.update_layout(
        title=f"จำนวนที่รับในแต่ละรอบของ {selected_university}",
        xaxis_title="รอบการรับ",
        yaxis_title="จำนวนที่รับ",
        barmode='group'
    )

    return filtered_university_df.to_dict('records'), fig_map, fig_bar

if __name__ == "__main__":
    app.run(debug=True)
