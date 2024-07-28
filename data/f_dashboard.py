from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import pandas as pd
import os
import plotly.graph_objects as go
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

    total = [f'รับ {a+b+c+d} คน' for a,b,c,d in zip(round_1, round_2, round_3, round_4)]
    return total

app = Dash(__name__)

data_file = "university.csv"
df = pd.read_csv(data_file)
# filtered_df = df[['name', 'university', 'ชื่อหลักสูตร',
#        'ชื่อหลักสูตรภาษาอังกฤษ', 'ประเภทหลักสูตร', 'วิทยาเขต', 
#        'ค่าใช้จ่าย', 'อัตราการสำเร็จการศึกษา', 'รอบ 1 Portfolio',
#        'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']]
selected_cols = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
df['ทั้งหมด'] = extract_and_sum(df, selected_cols)

filtered_df = df[['name', 'university', 'วิทยาเขต', 'ค่าใช้จ่าย',
       'ทั้งหมด', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 
       'รอบ 3 Admission', 'รอบ 4 Direct Admission']]
filtered_df = filtered_df.rename(columns={"name": "ชื่อหลักสูตรภาษาไทย", "university": "มหาวิทยาลัย"})

# with open('thailand_provinces.geojson', 'r', encoding='utf-8') as f:
#     geojson = json.load(f)

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
    # table
    dash_table.DataTable(
        data=filtered_df.to_dict('records'),
        page_size=5,
        style_cell={
            'textAlign': 'left',
            # 'maxWidth': 0
        },
        style_data={
            'whiteSpace': 'normal',
            'height': '50px',
            'lineHeight': 'auto'
        },
        style_table={'overflowX': 'auto'},
        style_header={
            'backgroundColor': 'rgb(50,50,50)',
            'color' : 'white',
            'textAlign': 'center',
            # 'fontWeight': 'bold'
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
                options=[{'label': university, 'value': university} for university in filtered_df['มหาวิทยาลัย'].unique()],
                value='จุฬาลงกรณ์มหาวิทยาลัย'  # default
            ),
        ],
        style={'margin-bottom': '30px'}
    ),

    # html.Div(
    #     [
    #         html.Label(
    #             "ตัวเลือกที่ต้องการแสดง",
    #             style={'font-weight':'bold'}
    #         ),
    #     ],
    #     style={'margin-bottom': '10px'}
    # ),

    # html.Div(
    #     [
    #         dcc.Checklist(
    #             id='checklist-selection',
    #             options=[
    #                 {'label': 'นักเรียนทั้งหมด', 'value': 'นักเรียนทั้งหมด'},
    #                 {'label': 'นักเรียนชาย', 'value': 'นักเรียนชาย'},
    #                 {'label': 'นักเรียนหญิง', 'value': 'นักเรียนหญิง'}
    #             ],
    #             value=['นักเรียนทั้งหมด'],  # default
    #             # inline=True
    #         ),
    #     ],
    #     style={'margin-bottom': '20px'}
    # ),

    # dcc.Graph(id="graph-content", style={'width': '100%'}),
    # dcc.Graph(id="map-content", style={'width': '100%'})
])

@callback(
    Output('graph-content', 'figure'),
    [
        Input('dropdown-selection', 'value'),
    #  Input('checklist-selection', 'value')
    ]
)

def update_graph(selected_province, selected_display):
    filtered_province_df = filtered_df[filtered_df["มหาวิทยาลัย"] == selected_province]

    melted_df = filtered_province_df.melt(id_vars=["จังหวัด"], value_vars=selected_display,
                                          var_name='Category', value_name='Count')

    fig = px.bar(
        melted_df,
        x='Category',
        y='Count',
        labels={'Category': 'ประเภทนักเรียน', 'Count': 'จำนวนนักเรียน (คน)'},
    )
    
    fig.update_layout(
        title={
            'text': f"จำนวนนักเรียนที่เรียนจบในจังหวัด {selected_province}",
            'font': {'size':20, 'weight':'normal'},
            'pad':{'t':-20},
            'y':0.9,
            'x':0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        # width=800,
        # bargap=0.8
    )

    fig.update_traces(
        width=0.2
    )
    
    return fig

@callback(
    Output('map-content', 'figure'),
    [Input('dropdown-selection', 'value')]
)

def update_map(selected_province):
    fig = px.choropleth(
        filtered_df,
        # geojson=geojson,
        locations='จังหวัด',
        featureidkey="properties.name",
        color='นักเรียนทั้งหมด',
        color_continuous_scale="YlOrRd",
        range_color=[filtered_df['นักเรียนทั้งหมด'].min(), filtered_df['นักเรียนทั้งหมด'].max()],
        labels={'นักเรียนทั้งหมด': 'นักเรียนทั้งหมด'},
        # width=2000,
    )
    
    fig.update_geos(fitbounds="locations", visible=True)
    
    fig.update_layout(
        title={
            'text': "จำนวนนักเรียนทั้งหมดที่เรียนจบในแต่ละจังหวัด",
            'font': {'size':20, 'weight':'normal'},
            'pad':{'t':-20},
            'y': 0.9,
            'x': 0.5,
            'xanchor': 'center',
            'yanchor': 'top'
        },
        coloraxis_colorbar={
            'title': 'จำนวนนักเรียนทั้งหมด (คน)',
            'x': 1.05,
            'len': 0.8
        }
    )
    
    return fig


if __name__ == "__main__":
    app.run(debug=True)