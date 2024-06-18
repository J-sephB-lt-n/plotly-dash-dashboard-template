"""
An example data dashboard built using Plotly Dash

TODO:
    The plan is:
        - when someone chooses a dataset, check if 
"""

import datetime
import json
from os import walk
from typing import Final

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dash_table, Input, Output, State, dcc, html, ctx
from dash.dependencies import ALL
from dash.exceptions import PreventUpdate
from dash_auth import BasicAuth

import db

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
    ),
    "title_font": {"color": "white"},
    "legend": dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
}


def datetime_now_str() -> str:
    """Returns a string containing the current date and time (in user's system timezone)"""
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")


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
        dcc.Store(
            # stores user-specific state, caches datasets, logs user activity
            id="user-session-data",
            storage_type="session",
        ),
        dbc.Stack(
            [
                dbc.Stack(
                    [
                        dbc.DropdownMenu(
                            label="Select Dataset",
                            menu_variant="dark",
                            children=[
                                dbc.DropdownMenuItem(
                                    dataset_name,
                                    id=f"select-dataset-{dataset_name}",
                                    n_clicks=0,
                                )
                                for dataset_name in db.list_available_datasets()
                            ],
                            id="dropdown-dataset-selector",
                        ),
                        dbc.Button(
                            "Refresh Data",
                            id={"type": "data-refresh-button", "index": 0},
                            n_clicks=0,
                        ),
                    ],
                    direction="horizontal",
                    gap=3,
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Data Refreshed")),
                        dbc.ModalBody(
                            "The latest data has been fetched from the database"
                        ),
                        dbc.ModalFooter(
                            dbc.Button(
                                "Close",
                                id="close-data-refresh-popup",
                                className="ms-auto",
                                n_clicks=0,
                            )
                        ),
                    ],
                    id="data-refresh-popup",
                    is_open=False,
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


# Callback to update the list of available datasets
# in the user's session data
@app.callback(
    Output("user-session-data", "data"),
    Input({"type": "data-refresh-button", "index": ALL}, "n_clicks"),
    State("user-session-data", "data"),
)
def on_click(n_clicks, data):
    if n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate

    # Give a default data dict with 0 clicks if there's no data.
    data = {
        "currently_selected_dataset": None,
        "available_datasets": db.list_available_datasets(),
        "cached_datasets": {},
    }

    return data


# Callback to update the dataset selector dropdown
# (to reflect the updated list of available datasets)
@app.callback(
    Output("dropdown-dataset-selector", "children"),
    Input(
        # see: https://github.com/plotly/dash-renderer/pull/81
        "user-session-data",
        "modified_timestamp",
    ),
    State("user-session-data", "data"),
)
def update_dataset_selector(_, data):
    if data:
        return [
            dbc.DropdownMenuItem(
                dataset_name,
                id={"type": "single-dataset-selector", "index": idx},
                n_clicks=0,
            )
            for idx, dataset_name in enumerate(data["available_datasets"])
        ]


# Popup telling the user that the latest data has been fetched
# from the database
# @app.callback(
#     Output("data-refresh-popup", "is_open"),
#     [
#         Input("data-refresh-button", "n_clicks"),
#         Input("close-data-refresh-popup", "n_clicks"),
#     ],
#     [State("data-refresh-popup", "is_open")],
# )
# def toggle_modal(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open


# update the currently selected dataset
# when a new dataset is selected
# @app.callback(
#     Output("user-session-data", "data"),
#     Input({"type": "single-dataset-selector", "index": ALL}, "n_clicks"),
#     State("user-session-data", "data"),
#     prevent_initial_call=True,
# )
# def update_current_selected_dataset(_, data):
#     # ctx.triggered_id looks like this: {'index': 0, 'type': 'single-dataset-selector'}
#     triggered_id = ctx.triggered_id
#     data = data
#     if data and triggered_id:
#         data["currently_selected_dataset"] = data["available_datasets"][
#             triggered_id["index"]
#         ]
#         return data


# @app.callback(
#     Output("user-session-data", "data")
#     # Output("selected-dataset-alert", "children"),
#     [Input(f"select-dataset-{idx}", "n_clicks") for idx, _ in enumerate(data)],
# )
# def update_selected_dataset(*args):
#     """docstring TODO"""
#     ctx = dash.callback_context
#
#     if not ctx.triggered:
#         return "No dataset selected"
#     else:
#         button_id = ctx.triggered[0]["prop_id"].split(".")[0]
#
#     if button_id[:15] == "select-dataset-":
#         selected_dataset_idx: int = int(button_id.split("-")[2])
#         return "Dataset Selected: " + list(data.keys())[selected_dataset_idx]
#

# @app.callback(
#     Output("selected-dataset-alert", "children"),
#     [Input(f"select-dataset-{idx}", "n_clicks") for idx, _ in enumerate(data)],
# )
# def update_selected_dataset(*args):
#     """docstring TODO"""
#     ctx = dash.callback_context
#
#     if not ctx.triggered:
#         return "No dataset selected"
#     else:
#         button_id = ctx.triggered[0]["prop_id"].split(".")[0]
#
#     if button_id[:15] == "select-dataset-":
#         selected_dataset_idx: int = int(button_id.split("-")[2])
#         return "Dataset Selected: " + list(data.keys())[selected_dataset_idx]


# @app.callback(
#     Output("page-content", "children"),
#     [
#         Input("url", "pathname"),
#         #         Input("select-dataset1", "n_clicks"),
#         #         Input("select-dataset2", "n_clicks"),
#         #         Input("select-dataset3", "n_clicks"),
#     ],
# )
# def render_page_content(pathname):
#     """docstring TODO"""
# #     global global_log_strings
# # #     global global_current_dataset_id
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
# if pathname == "/":
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


# @app.callback(
#     Output("download-csv", "data"),
#     Input("download_csv_button", "n_clicks"),
#     prevent_initial_call=True,
# )
# def func(n_clicks):
#     global global_log_strings
#     global_log_strings = [
#         f"{datetime_now_str()} Downloaded dataset {global_current_dataset_id} (CSV)",
#         html.Br(),
#     ] + global_log_strings
#     csv_contents: str = (
#         ",".join(data[global_current_dataset_id][0].keys())
#         + "\n"
#         + "\n".join(
#             [
#                 ",".join(str(col) for col in row.values())
#                 for row in data[global_current_dataset_id]
#             ]
#         )
#     )
#     return dict(
#         content=csv_contents, filename=f"dataset_{global_current_dataset_id}.csv"
#     )


if __name__ == "__main__":
    # run local dev server #
    if EXPOSE_TO_PUBLIC_INTERNET:
        app.run_server(debug=False, host="0.0.0.0", port=8888)
    else:
        app.run_server(debug=True, port=8888)
