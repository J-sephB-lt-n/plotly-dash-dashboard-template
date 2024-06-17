"""
An example data dashboard built using Plotly Dash
"""

import datetime
from os import walk
import random
import string
from typing import Final

import dash
import dash_bootstrap_components as dbc
import pandas as pd
import plotly.express as px
from dash import Dash, dash_table, Input, Output, dcc, html
from dash_auth import BasicAuth

EXPOSE_TO_PUBLIC_INTERNET: Final[bool] = False

app = Dash(
    __name__,
    external_stylesheets=[dbc.themes.CYBORG, "assets/responsive_sizing.css"],
    # suppress_callback_exceptions=True,
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1.0"},
    ],
    title="Dash Dashboard Template",
)
server = app.server

BasicAuth(
    app, {"admin": "password"}, secret_key="It4cQgcRTMxfNp4hdgliBIZ6BTErcddYzo/b7UDN"
)

DATA_TABLE_STYLE: Final[dict] = {
    "page_size": 15,
    "style_as_list_view": True,
    "style_header": {
        "backgroundColor": "rgb(30, 30, 30)",
        "color": "white",
    },
    "style_data": {
        "backgroundColor": "rgb(0, 0, 0)",
        "color": "white",
    },
    "style_cell": {"border": "rgb(0,0,0)"},
}
PLOT_STYLE: Final[dict] = {
    "paper_bgcolor": "black",  # Background color of the entire figure
    "plot_bgcolor": "black",  # Background color of the plotting area,
    "font": dict(color="white"),  # Text color
    "xaxis": dict(
        showgrid=False,
        linecolor="white",
        tickcolor="white",
        title_font=dict(color="white"),
        tickfont=dict(color="white"),
    ),  # X-axis style
    "yaxis": dict(
        showgrid=False,
        linecolor="white",
        tickcolor="white",
        title_font=dict(color="white"),
        tickfont=dict(color="white"),
    ),  # Y-axis style
    "title_font": dict(color="white"),  # Title text color
    "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
}


def datetime_now_str() -> str:
    """Returns a string containing the current date and time (in user's system timezone)"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


global_log_strings = [f"{datetime_now_str()} Started session"]
global_current_dataset_id = 1
global_current_page_url = "/"


def simulate_data(
    n_datasets: int, n_groups: int, n_rows_per_group: int
) -> dict[int, list[dict]]:
    """Randomly simulates datasets"""
    if n_groups > 26:
        raise ValueError("Cannot simulate more than 26 groups")
    datasets = {}
    for idx in range(1, n_datasets + 1):
        dataset_id = f"Data for period {idx}"
        datasets[dataset_id] = []
        for group, group_mean in (
            (string.ascii_uppercase[i], random.randint(10, 100))
            for i in range(n_groups)
        ):
            for t in range(n_rows_per_group):
                datasets[dataset_id].append(
                    {
                        "time": t,
                        "group": group,
                        "amount": int(random.gauss(group_mean, 20)),
                    }
                )
    return datasets


data = simulate_data(n_datasets=4, n_groups=2, n_rows_per_group=100)


navbar = dbc.Nav(
    [
        dbc.Stack(
            [
                dbc.Col(
                    html.H2(
                        "Plotly Dash Dashboard Template",
                    )
                ),
                dbc.Nav(
                    [
                        dbc.NavLink("Welcome", href="/", active="exact"),
                        dbc.NavLink("Raw Data", href="/data", active="exact"),
                        dbc.NavLink(
                            "Data Visualisations", href="/dataviz", active="exact"
                        ),
                        dbc.NavLink(
                            "Dashboard Activity Log", href="/log", active="exact"
                        ),
                    ],
                    vertical=True,
                    pills=True,
                ),
            ],
            direction="vertical",
        )
    ],
    id="nav-bar",
)

# content = html.Div(
content = dbc.Container(
    [
        dbc.Stack(
            [
                dbc.DropdownMenu(
                    label="Select Dataset",
                    menu_variant="dark",
                    children=[
                        dbc.DropdownMenuItem(
                            dataset_name,
                            id=f"select-dataset-{dataset_idx}",
                            n_clicks=0,
                        )
                        for dataset_idx, dataset_name in enumerate(data)
                    ],
                    # children=[
                    #     dbc.DropdownMenuItem(
                    #         "Dataset 1",
                    #         id="select-dataset-1",
                    #         n_clicks=0,
                    #     ),
                    #     dbc.DropdownMenuItem(
                    #         "Dataset 2",
                    #         id="select-dataset-2",
                    #         n_clicks=0,
                    #     ),
                    #     dbc.DropdownMenuItem(
                    #         "Dataset 3",
                    #         id="select-dataset-3",
                    #         n_clicks=0,
                    #     ),
                    # ],
                ),
                dbc.Alert(
                    id="selected-dataset-alert",
                    color="light",
                    children="No dataset selected",
                ),
            ],
            direction="vertical",
            gap=3,
        ),
        dbc.Container(id="page-content"),
    ],
    id="main-content",
)

app.layout = dbc.Container(
    [dcc.Location(id="url"), navbar, content],
)


@app.callback(
    Output("selected-dataset-alert", "children"),
    [
        Input(f"select-dataset-{idx}", "n_clicks")
        for idx, _ in enumerate(data)
        # Input("select-dataset-1", "n_clicks"),
        # Input("select-dataset-2", "n_clicks"),
        # Input("select-dataset-3", "n_clicks"),
    ],
)
def update_selected_dataset(*args):
    """docstring TODO"""
    ctx = dash.callback_context

    if not ctx.triggered:
        return "No dataset selected"
    else:
        button_id = ctx.triggered[0]["prop_id"].split(".")[0]

    if button_id[:15] == "select-dataset-":
        selected_dataset_idx: int = int(button_id.split("-")[2])
        return "Dataset Selected: " + list(data.keys())[selected_dataset_idx]
    # if button_id == "select-dataset-1":
    #     return "Dataset 1 selected"
    # elif button_id == "select-dataset-2":
    #     return "Dataset 2 selected"
    # elif button_id == "select-dataset-3":
    #     return "Dataset 3 selected"


# @app.callback(
#     Output("page-content", "children"),
#     [
#         Input("url", "pathname"),
#         Input("select-dataset1", "n_clicks"),
#         Input("select-dataset2", "n_clicks"),
#         Input("select-dataset3", "n_clicks"),
#     ],
# )
# def render_page_content(pathname, select_dataset1, select_dataset2, select_dataset3):
#     global global_log_strings
#     global global_current_dataset_id
#     global global_current_page_url
#
#     ctx = dash.callback_context
#     if ctx.triggered_id in ("select-dataset1", "select-dataset2", "select-dataset3"):
#         dataset_id = int(ctx.triggered_id[-1])
#         if dataset_id != global_current_dataset_id:
#             global_current_dataset_id = dataset_id
#             global_log_strings = [
#                 f"{datetime_now_str()} Selected dataset {dataset_id}",
#                 html.Br(),
#             ] + global_log_strings
#
#     if pathname == "/":
#         if global_current_page_url != pathname:
#             global_current_page_url = pathname
#             global_log_strings = [
#                 f"{datetime_now_str()} Visited Welcome page",
#                 html.Br(),
#             ] + global_log_strings
#         return dbc.Container(
#             [
#                 html.Br(),
#                 "This is an example of a dashboard built in python using Plotly Dash.",
#                 html.Br(),
#                 html.Br(),
#                 "The current features are:",
#                 html.Ul(
#                     [
#                         html.Li("Responsive layout (responds to viewer device size)."),
#                         html.Li("Basic user authentication (username+password)."),
#                         html.Li(
#                             "Dataset selector (user can choose their dataset) - at top of every page."
#                         ),
#                         html.Li(
#                             "Grid of plots of the selected dataset (`Data Visualisations` page)."
#                         ),
#                         html.Li("Table-view of the raw data (`Raw Data` page)."),
#                         html.Li(
#                             "Button to download CSV version of the raw data (`Raw Data` page)."
#                         ),
#                         html.Li(
#                             "User activity on the dashboard is logged (`Dashboard Activity Log` page)."
#                         ),
#                     ],
#                 ),
#                 html.Br(),
#                 html.P("In future I want to add:"),
#                 html.Ul(
#                     [
#                         html.Li("Page loading animations"),
#                         html.Li("User can switch between light and dark mode."),
#                     ],
#                 ),
#             ]
#         )
#     elif pathname == "/data":
#         if global_current_page_url != pathname:
#             global_current_page_url = pathname
#             global_log_strings = [
#                 f"{datetime_now_str()} Visited Raw Data page",
#                 html.Br(),
#             ] + global_log_strings
#         return dbc.Stack(
#             [
#                 dbc.Col(
#                     dbc.Button("Download CSV", id="download_csv_button", n_clicks=0),
#                 ),
#                 dcc.Download(id="download-csv"),
#                 dbc.Col(
#                     dash_table.DataTable(
#                         data[global_current_dataset_id],
#                         **DATA_TABLE_STYLE,
#                     ),
#                 ),
#             ],
#             direction="vertical",
#             gap=3,
#         )
#     elif pathname == "/dataviz":
#         if global_current_page_url != pathname:
#             global_current_page_url = pathname
#             global_log_strings = [
#                 f"{datetime_now_str()} Visited Data Visualisations page",
#                 html.Br(),
#             ] + global_log_strings
#         selected_dataset_df = pd.DataFrame(data[global_current_dataset_id])
#         return dbc.Stack(
#             [
#                 dbc.Col(
#                     dcc.Graph(
#                         figure=px.line(
#                             selected_dataset_df,
#                             x="time",
#                             y="amount",
#                             color="group",
#                             title="Line Plots",
#                         ).update_layout(**PLOT_STYLE),
#                     ),
#                 ),
#                 dbc.Col(
#                     dcc.Graph(
#                         figure=px.bar(
#                             selected_dataset_df,
#                             x="time",
#                             y="amount",
#                             color="group",
#                             title="Stacked Bar Chart",
#                         ).update_layout(**PLOT_STYLE)
#                     )
#                 ),
#                 dbc.Stack(
#                     [
#                         dbc.Col(
#                             dcc.Graph(
#                                 figure=px.histogram(
#                                     data[global_current_dataset_id],
#                                     x="amount",
#                                     # y="",
#                                     color="group",
#                                     marginal="box",
#                                     title="Overlaid Histograms",
#                                 ).update_layout(**PLOT_STYLE)
#                                 # figure=ff.create_distplot(
#                                 #     [
#                                 #         [
#                                 #             x["amount"]
#                                 #             for x in data[global_current_dataset_id]
#                                 #             if x["group"] == group
#                                 #         ]
#                                 #         for group in ("A", "B", "C")
#                                 #     ],
#                                 #     ["A", "B", "C"],
#                                 # ).update_layout(**PLOT_STYLE)
#                             ),
#                             width=8,
#                         ),
#                         dbc.Col(
#                             dcc.Graph(
#                                 figure=px.pie(
#                                     selected_dataset_df.groupby("group")
#                                     .agg(sum_amount=("amount", "sum"))
#                                     .reset_index(),
#                                     values="sum_amount",
#                                     names="group",
#                                     title="Pie Chart",
#                                 ).update_layout(**PLOT_STYLE)
#                             ),
#                             width=4,
#                         ),
#                     ],
#                     direction="horizontal",
#                 ),
#             ],
#             direction="vertical",
#             gap=0,
#             id="plot-stack",
#         )
#     elif pathname == "/log":
#         if global_current_page_url != pathname:
#             global_current_page_url = pathname
#         return html.P(global_log_strings)
#     # If the user tries to reach a different page, return a 404 message
#     return html.Div(
#         [
#             html.H1("404: Not found", className="text-danger"),
#             html.Hr(),
#             html.P(f"The page {pathname} does not exist."),
#         ],
#     )


# @app.callback(
#     Output("selected-dataset-alert", "children"),
#     [
#         Input("url", "pathname"),
#         Input("select-dataset1", "n_clicks"),
#         Input("select-dataset2", "n_clicks"),
#         Input("select-dataset3", "n_clicks"),
#     ],
# )
# def show_selected_dataset(*args):
#     ctx = dash.callback_context
#     if ctx.triggered_id:
#         return f"Dataset {ctx.triggered_id[-1]}"


@app.callback(
    Output("download-csv", "data"),
    Input("download_csv_button", "n_clicks"),
    prevent_initial_call=True,
)
def func(n_clicks):
    global global_log_strings
    global_log_strings = [
        f"{datetime_now_str()} Downloaded dataset {global_current_dataset_id} (CSV)",
        html.Br(),
    ] + global_log_strings
    csv_contents: str = (
        ",".join(data[global_current_dataset_id][0].keys())
        + "\n"
        + "\n".join(
            [
                ",".join(str(col) for col in row.values())
                for row in data[global_current_dataset_id]
            ]
        )
    )
    return dict(
        content=csv_contents, filename=f"dataset_{global_current_dataset_id}.csv"
    )


if __name__ == "__main__":
    # run local dev server #
    if EXPOSE_TO_PUBLIC_INTERNET:
        app.run_server(debug=False, host="0.0.0.0", port=8888)
    else:
        app.run_server(debug=True, port=8888)
