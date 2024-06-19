"""
An example data dashboard built using Plotly Dash

TODO:
    The plan is:
        - when someone chooses a dataset, check if 
"""

import argparse
import datetime
import json
from typing import Final

import dash
import dash_bootstrap_components as dbc
import plotly.express as px
from dash import Dash, dash_table, Input, Output, State, dcc, html, ctx, Patch, ALL
from dash.exceptions import PreventUpdate
from dash_auth import BasicAuth

import db

arg_parser = argparse.ArgumentParser()
arg_parser.add_argument(
    "-d",
    "--debug",
    help="Add diagnostic information to the dashboard",
    action="store_true",  # state if this flag is present
)
arg_parser.add_argument(
    "-e",
    "--expose_to_public_internet",
    help="Make dashboard available (over http) over public internet",
    action="store_true",  # state if this flag is present
)
args = arg_parser.parse_args()

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
if args.debug:
    debug_elements = [
        dbc.Col(html.P(id="debug-buttons")),
        dbc.Col(html.P(id="debug-user-session-data")),
    ]
else:
    debug_elements = []
content = dbc.Container(
    debug_elements
    + [
        dcc.Store(
            # stores user-specific state, caches datasets, logs user activity
            id="user-session-data",
            storage_type="session",
            data={
                "available_datasets": [],
                "cached_datasets": {},
                "currently_selected_dataset": None,
            },
        ),
        dbc.Stack(
            [
                dbc.Stack(
                    [
                        dbc.DropdownMenu(
                            label="Select Dataset",
                            menu_variant="dark",
                            id="dropdown-dataset-selector",
                            children=[],
                        ),
                        dbc.Button(
                            "Refresh Data",
                            id="refresh-data-button",
                            n_clicks=0,
                        ),
                    ],
                    direction="horizontal",
                    gap=3,
                    id="content-row1-stack",
                ),
                dbc.Modal(
                    [
                        dbc.ModalHeader(dbc.ModalTitle("Data Refreshed")),
                        dbc.ModalBody(
                            "The list of currently available datasets has been fetched from the database"
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
                    # children="No dataset selected",
                ),
            ],
            direction="vertical",
            gap=3,
            id="content-stack",
        ),
        dbc.Container(id="page-content"),
    ],
    id="main-content",
)

app.layout = dbc.Container(
    [dcc.Location(id="url"), navbar, content],
)

if args.debug:

    @app.callback(
        Output("debug-buttons", "children"),
        [
            Input("refresh-data-button", "n_clicks"),
            Input({"type": "selected-dataset", "index": ALL}, "n_clicks"),
        ],
    )
    def on_refresh_click(*args):
        button_clicked = ctx.triggered_id
        if button_clicked == "refresh-data-button":
            return (
                datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                + " clicked data-refresh-button"
            )
        else:
            return (
                datetime.datetime.now().strftime("%H:%M:%S.%f")[:-3]
                + " "
                + str(button_clicked)
            )

    @app.callback(
        Output("debug-user-session-data", "children"),
        Input(
            # see: https://github.com/plotly/dash-renderer/pull/81
            "user-session-data",
            "modified_timestamp",
        ),
        State("user-session-data", "data"),
    )
    def debug_user_session_data(_, user_session_data):
        return datetime.datetime.now().strftime("%H:%M:%S ") + str(user_session_data)


# Actions which update the user_session_data
@app.callback(
    [
        Output("dropdown-dataset-selector", "children"),
        Output("selected-dataset-alert", "children"),
        Output("user-session-data", "data"),
    ],
    [
        Input("refresh-data-button", "n_clicks"),
        Input({"type": "selected-dataset", "index": ALL}, "n_clicks"),
    ],
    State("user-session-data", "data"),
)
def update_user_session(data_refresh_n_clicks, data_select_n_clicks, user_session_data):
    if data_refresh_n_clicks is None or data_select_n_clicks is None:
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate
    current_dataset_alert_text = "No dataset selected"

    user_session_data = user_session_data or {
        "currently_selected_dataset": None,
        "available_datasets": db.list_available_datasets(),
        "cached_datasets": {},
    }

    button_clicked = ctx.triggered_id
    if button_clicked == "refresh-data-button":
        user_session_data = {
            "currently_selected_dataset": None,
            "available_datasets": db.list_available_datasets(),
            "cached_datasets": {},
        }

    if hasattr(button_clicked, "type") and button_clicked.type == "selected-dataset":
        selected_dataset_name = user_session_data["available_datasets"][
            button_clicked.index
        ]
        user_session_data["currently_selected_dataset"] = selected_dataset_name
        current_dataset_alert_text = f"Dataset Selected: [ {selected_dataset_name} ]"
        if selected_dataset_name not in user_session_data["cached_datasets"]:
            user_session_data["cached_datasets"][selected_dataset_name] = (
                db.get_dataset(selected_dataset_name)
            )

    # patched_children = Patch()
    patched_children = []
    for dataset_index, dataset_name in enumerate(
        user_session_data["available_datasets"]
    ):
        patched_children.append(
            dbc.DropdownMenuItem(
                dataset_name,
                id={"type": "selected-dataset", "index": dataset_index},
                n_clicks=0,
            )
        )

    return patched_children, current_dataset_alert_text, user_session_data


# Popup telling the user that the latest data has been fetched
# from the database
@app.callback(
    Output("data-refresh-popup", "is_open"),
    [
        Input("refresh-data-button", "n_clicks"),
        Input("close-data-refresh-popup", "n_clicks"),
    ],
    [State("data-refresh-popup", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open


@app.callback(
    Output("page-content", "children"),
    Input("url", "pathname"),
    State("user-session-data", "data"),
)
def render_page_content(pathname, user_session_data):
    """docstring TODO"""
    if pathname == "/":
        return dbc.Container(
            [
                html.Br(),
                "This is an example of a dashboard built in python using Plotly Dash.",
                html.Br(),
                html.Br(),
                "The current features are:",
                html.Ul(
                    [
                        html.Li(
                            "Dataset selector (user can choose their dataset) - at top of every page."
                        ),
                        html.Li(
                            "User dashboard state is stored in their browser session storage."
                        ),
                        html.Li(
                            "Datasets previously fetched are cached in user's browser session storage (reduces database calls)."
                        ),
                        html.Li("Responsive layout (responds to viewer device size)."),
                        html.Li("Basic user authentication (username+password)."),
                        html.Li(
                            "Grid of plots of the selected dataset (`Data Visualisations` page)."
                        ),
                        html.Li("Table-view of the raw data (`Raw Data` page)."),
                        html.Li(
                            "Button to download CSV version of the raw data (`Raw Data` page)."
                        ),
                        html.Li(
                            "User activity on the dashboard is logged (`Dashboard Activity Log` page)."
                        ),
                    ],
                ),
            ]
        )

    if pathname == "/data":
        if (
            user_session_data
            and user_session_data["currently_selected_dataset"]
            in user_session_data["cached_datasets"]
        ):
            current_dataset_table = dash_table.DataTable(
                user_session_data["cached_datasets"][
                    user_session_data["currently_selected_dataset"]
                ],
                **DATA_TABLE_STYLE,
            )
        else:
            current_dataset_table = html.P("Please select a dataset")

        return dbc.Stack(
            [
                dbc.Col(
                    dbc.Button("Download CSV", id="download_csv_button", n_clicks=0),
                ),
                dcc.Download(id="download-csv"),
                dbc.Col(
                    current_dataset_table,
                ),
            ],
            direction="vertical",
            gap=3,
        )


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
    if args.expose_to_public_internet:
        app.run_server(debug=False, host="0.0.0.0", port=8888)
    else:
        app.run_server(debug=True, port=8888)
