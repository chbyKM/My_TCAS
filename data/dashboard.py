from dash import Dash, dcc, html, Input, Output, callback, dash_table
import plotly.graph_objects as go
import pandas as pd
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

    total = [a + b + c + d for a, b, c, d in zip(round_1, round_2, round_3, round_4)]
    return [f'รับ {x} คน' for x in total]

app = Dash(__name__)

data_file = "university.csv"
df = pd.read_csv(data_file)
selected_cols = ['รอบ 1 Portfolio', 'รอบ 2 Quota', 'รอบ 3 Admission', 'รอบ 4 Direct Admission']
df['ทั้งหมด'] = extract_and_sum(df, selected_cols)

filtered_df = df[['ชื่อหลักสูตร', 'university', 'ค่าใช้จ่าย',
       'ทั้งหมด', 'รอบ 1 Portfolio', 'รอบ 2 Quota', 
       'รอบ 3 Admission', 'รอบ 4 Direct Admission']]
cleaned_df = filtered_df.rename(columns={"university": "มหาวิทยาลัย"})

location_df = pd.read_csv('assets/university_location_clean.csv')
location_df = location_df.rename(columns={"ชื่อสถานศึกษา": "มหาวิทยาลัย"})

uni_dict = {uni: province for uni, province in zip(location_df['มหาวิทยาลัย'].tolist(), location_df['จังหวัด'].tolist())}

# Assign province to universities in cleaned_df
cleaned_df['จังหวัด'] = cleaned_df['มหาวิทยาลัย'].map(uni_dict).fillna("")

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
    # graph
    dcc.Graph(id='bar_chart')
])

@app.callback(
    [Output('data_table', 'data'),
     Output('bar_chart', 'figure')],
    Input('dropdown-selection', 'value')
)
def update_content(selected_university):
    filtered_university_df = cleaned_df[cleaned_df["มหาวิทยาลัย"] == selected_university]
    
    if filtered_university_df.empty:
        return [], go.Figure()  # Return an empty figure if no data is found
    
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
    
    return filtered_university_df.to_dict('records'), fig

if __name__ == "__main__":
    app.run(debug=True)
