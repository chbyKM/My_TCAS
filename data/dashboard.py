from dash import dcc, html, Dash, callback, Input, Output
import plotly.graph_objects as go
import pandas as pd

# Load DataFrame
df = pd.read_csv('university_test_data.csv')

# Initialize the Dash app
app = Dash(__name__, external_stylesheets=['https://codepen.io/chriddyp/pen/bWLwgP.css'])

#################### CHARTS #####################################
def create_filtered_table(University="University", Course="Course"):
    filtered_df = df[(df.University == University) & (df.Course == Course)]
    
    if filtered_df.empty:
        return go.Figure()  # Return an empty figure if no data matches the filter

    fig = go.Figure(data=[go.Table(
        header=dict(values=filtered_df.columns, align='left'),
        cells=dict(values=[filtered_df[col].tolist() for col in filtered_df.columns], align='left'))
    ])
    fig.update_layout(paper_bgcolor="#e5ecf6", margin={"t":0, "l":0, "r":0, "b":0}, height=700)
    return fig

##################### WIDGETS ####################################
# Create dropdown options
university_options = [{'label': uni, 'value': uni} for uni in df.University.unique()]
course_options = [{'label': course, 'value': course} for course in df.Course.unique()]

University_drop = dcc.Dropdown(id="university_drop", options=university_options, value=df.University.iloc[0], clearable=False)
Course_drop = dcc.Dropdown(id="course_drop", options=course_options, value=df.Course.iloc[0], clearable=False)

##################### APP LAYOUT ####################################
app.layout = html.Div([
    html.Div([
        html.H1("My TCAS Dashboard", className="text-center fw-bold m-2"),
        html.Br(),
        dcc.Tabs([
            dcc.Tab([
                html.Br(),
                html.Div([
                    "University: ", University_drop, html.Br(),
                    "Course: ", Course_drop, html.Br(),
                    dcc.Graph(id="table")  # This is for the table
                ])
            ], label="Detail")
        ])
    ], className="col-8 mx-auto"),
], style={"background-color": "#e5ecf6", "height": "100vh"})

##################### CALLBACKS ####################################
@callback(
    Output("table", "figure"),
    [Input("university_drop", "value"), Input("course_drop", "value")]
)
def update_table(University, Course):
    return create_filtered_table(University, Course)

if __name__ == "__main__":
    app.run(debug=True)
