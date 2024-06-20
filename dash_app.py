"""
An example data dashboard built using Plotly Dash

TODO:
    The plan is:
        - when someone chooses a dataset, check if 
"""

import argparse
import datetime
import itertools
from typing import Final

import dash_bootstrap_components as dbc
import dash_loading_spinners as dls
import plotly.express as px
from dash import Dash, dash_table, Input, Output, State, dcc, html, ctx, ALL
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
    suppress_callback_exceptions=True,
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
                        dbc.NavLink(
                            "Welcome", href="/", active="exact", id="welcome-pagelink"
                        ),
                        dbc.NavLink(
                            "Raw Data", href="/data", active="exact", id="data-pagelink"
                        ),
                        dbc.NavLink(
                            "Data Visualisations",
                            href="/dataviz",
                            active="exact",
                            id="dataviz-pagelink",
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
                "current_page": "/",
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
                # dbc.Modal(
                #     [
                #         dbc.ModalHeader(dbc.ModalTitle("Data Refreshed")),
                #         dbc.ModalBody(
                #             "The list of currently available datasets has been fetched from the database"
                #         ),
                #         dbc.ModalFooter(
                #             dbc.Button(
                #                 "Close",
                #                 id="close-data-refresh-popup",
                #                 className="ms-auto",
                #                 n_clicks=0,
                #             )
                #         ),
                #     ],
                #     id="data-refresh-popup",
                #     is_open=False,
                # ),
                dls.Triangle(
                    dbc.Alert(
                        id="selected-dataset-alert",
                        color="light",
                        # children="No dataset selected",
                    ),
                    color="#2a9fd6",
                    # debounce=500,
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

app.layout = dbc.Container([dcc.Location(id="url"), navbar, content])

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
        return datetime.datetime.now().strftime("%H:%M:%S ") + str(
            {
                k: (list(v.keys()) if k == "cached_datasets" else v)
                for k, v in user_session_data.items()
            }
        )


# Actions triggered by global buttons
@app.callback(
    [
        Output("dropdown-dataset-selector", "children"),
        Output("selected-dataset-alert", "children"),
        Output("user-session-data", "data"),
    ],
    [
        Input("refresh-data-button", "n_clicks"),
        Input({"type": "selected-dataset", "index": ALL}, "n_clicks"),
        Input("welcome-pagelink", "n_clicks"),
        Input("data-pagelink", "n_clicks"),
        Input("dataviz-pagelink", "n_clicks"),
    ],
    State("user-session-data", "data"),
)
def update_user_session(
    data_refresh,
    data_select,
    welcome,
    data,
    dataviz,
    user_session_data,
):
    if all(var is None for var in (data_refresh, data_select, welcome, data, dataviz)):
        # prevent the None callbacks is important with the store component.
        # you don't want to update the store for nothing.
        raise PreventUpdate

    user_session_data = user_session_data or {
        "currently_selected_dataset": None,
        "available_datasets": db.list_available_datasets(),
        "cached_datasets": {},
        "current_page": "/",
    }

    button_clicked = ctx.triggered_id

    if button_clicked == "refresh-data-button":
        user_session_data = {
            "currently_selected_dataset": None,
            "available_datasets": db.list_available_datasets(),
            "cached_datasets": {},
            "current_page": user_session_data.get("current_page"),
        }

    if hasattr(button_clicked, "type") and button_clicked.type == "selected-dataset":
        selected_dataset_name = user_session_data["available_datasets"][
            button_clicked.index
        ]
        user_session_data["currently_selected_dataset"] = selected_dataset_name
        if selected_dataset_name not in user_session_data["cached_datasets"]:
            user_session_data["cached_datasets"][selected_dataset_name] = (
                db.get_dataset(selected_dataset_name)
            )

    if button_clicked == "welcome-pagelink":
        user_session_data["current_page"] = "/"
    if button_clicked == "data-pagelink":
        user_session_data["current_page"] = "data"
    if button_clicked == "dataviz-pagelink":
        user_session_data["current_page"] = "dataviz"

    # patched_children = Patch()
    dataset_selection_options = [
        dbc.DropdownMenuItem(
            dataset_name,
            id={"type": "selected-dataset", "index": dataset_index},
            n_clicks=0,
        )
        for dataset_index, dataset_name in enumerate(
            user_session_data["available_datasets"]
        )
    ]

    current_dataset_name = user_session_data.get("currently_selected_dataset")
    if current_dataset_name is None:
        current_dataset_alert_text = "No dataset selected"
    else:
        current_dataset_alert_text = f"Dataset Selected: [ {current_dataset_name} ]"

    return dataset_selection_options, current_dataset_alert_text, user_session_data


# # Popup telling the user that the latest data has been fetched
# # from the database
# @app.callback(
#     Output("data-refresh-popup", "is_open"),
#     [
#         Input("refresh-data-button", "n_clicks"),
#         Input("close-data-refresh-popup", "n_clicks"),
#     ],
#     [State("data-refresh-popup", "is_open")],
# )
# def toggle_modal(n1, n2, is_open):
#     if n1 or n2:
#         return not is_open
#     return is_open


@app.callback(
    Output("page-content", "children"),
    [
        Input("url", "pathname"),
        Input({"type": "selected-dataset", "index": ALL}, "n_clicks"),
    ],
    State("user-session-data", "data"),
)
def render_page_content(pathname, select_dataset, user_session_data):
    """docstring TODO"""
    if pathname is None:
        pathname = user_session_data["current_page"]
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
                    ],
                ),
            ]
        )

    if pathname == "/data":
        selected_dataset_name = user_session_data["currently_selected_dataset"]
        selected_dataset = user_session_data["cached_datasets"].get(
            selected_dataset_name
        )

        if selected_dataset_name is None:
            current_dataset_table = dbc.Alert("Please select a dataset", color="light")
        else:
            current_dataset_table = dash_table.DataTable(
                selected_dataset,
                **DATA_TABLE_STYLE,
            )

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

    if pathname == "/dataviz":
        if not (
            user_session_data is not None
            and user_session_data["currently_selected_dataset"]
            in user_session_data["cached_datasets"]
        ):
            return dbc.Alert("Please select a dataset", color="light")
        else:
            current_dataset_name = user_session_data["currently_selected_dataset"]
            current_dataset = user_session_data["cached_datasets"][current_dataset_name]
            grouped_current_dataset = [
                # to understand this complex comprehension, refer to:
                # https://github.com/J-sephB-lt-n/useful-code-snippets/blob/main/snippets/python/data/native_groupby_agg.py
                {
                    "group": group_name,
                    "sum_amount": sum([row["amount"] for row in group_rows]),
                }
                for group_name, group_rows in itertools.groupby(
                    sorted(current_dataset, key=lambda x: x["group"]),
                    key=lambda x: x["group"],
                )
            ]
            return dbc.Stack(
                [
                    dbc.Col(
                        # dash_table.DataTable(current_dataset)
                        dcc.Graph(
                            figure=px.line(
                                current_dataset,
                                x="time",
                                y="amount",
                                color="group",
                                title="Line Plots",
                            ).update_layout(**PLOT_STYLE),
                        ),
                    ),
                    dbc.Col(
                        dcc.Graph(
                            figure=px.bar(
                                current_dataset,
                                x="time",
                                y="amount",
                                color="group",
                                title="Stacked Bar Chart",
                            ).update_layout(**PLOT_STYLE)
                        )
                    ),
                    dbc.Stack(
                        [
                            dbc.Col(
                                dcc.Graph(
                                    figure=px.histogram(
                                        current_dataset,
                                        x="amount",
                                        color="group",
                                        marginal="box",
                                        title="Overlaid Histograms",
                                    ).update_layout(**PLOT_STYLE)
                                ),
                                width=8,
                            ),
                            dbc.Col(
                                # dash_table.DataTable(
                                #     grouped_current_dataset,
                                #     **DATA_TABLE_STYLE,
                                # ),
                                dcc.Graph(
                                    figure=px.pie(
                                        grouped_current_dataset,
                                        values="sum_amount",
                                        names="group",
                                        title="Pie Chart",
                                        category_orders={
                                            "group": [
                                                x["group"]
                                                for x in grouped_current_dataset
                                            ]
                                        },
                                    ).update_layout(**PLOT_STYLE)
                                ),
                                width=4,
                            ),
                        ],
                        direction="horizontal",
                    ),
                ],
                direction="vertical",
                gap=0,
                id="plot-stack",
            )


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
    State("user-session-data", "data"),
    prevent_initial_call=True,
)
def download_csv(n_clicks, user_session_data):
    if (
        user_session_data
        and user_session_data["currently_selected_dataset"]
        in user_session_data["cached_datasets"]
    ):
        current_dataset_name = user_session_data["currently_selected_dataset"]
        current_dataset = user_session_data["cached_datasets"].get(current_dataset_name)
        if current_dataset:
            csv_contents: str = (
                ",".join(current_dataset[0].keys())
                + "\n"
                + "\n".join(
                    [
                        ",".join(str(col) for col in row.values())
                        for row in current_dataset
                    ]
                )
            )
            return dict(
                content=csv_contents,
                filename=f"dataset_{current_dataset_name}.csv",
            )


if __name__ == "__main__":
    if args.expose_to_public_internet:
        app.run_server(debug=False, host="0.0.0.0", port=8888)
    else:
        app.run_server(debug=True, port=8888)
