from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.express as px
import pandas as pd
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

filtered_df = df[['ชื่อหลักสูตร', 'university', 'ค่าใช้จ่าย',
       'ทั้งหมด', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 
       'รอบ 3 Admission', 'รอบ 4 Direct Admission']]
filtered_df = filtered_df.rename(columns={"university": "มหาวิทยาลัย"})

display_cols = ['ชื่อหลักสูตร', 'ค่าใช้จ่าย',
       'ทั้งหมด', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 
       'รอบ 3 Admission', 'รอบ 4 Direct Admission']
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
                value='มหาวิทยาลัยสงขลานครินทร์ หาดใหญ่'  # default
            ),
        ],
        style={'margin-bottom': '30px'}
    ),
    # table
    dash_table.DataTable(
        id='data_table',
        columns=[
            {"name": col, "id": col} for col in filtered_df[display_cols].columns
        ],
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
])

@app.callback(
    Output('data_table', 'data'),
    [Input('dropdown-selection', 'value')]
)

def update_table(selected_university):
    filtered_university_df = filtered_df[filtered_df["มหาวิทยาลัย"] == selected_university]
    # filtered_university_df = filtered_university_df[display_cols]
    return filtered_university_df.to_dict('records')

if __name__ == "__main__":
    app.run(debug=True)