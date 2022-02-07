# import dash_html_components as html
import dash
import visdcc
from dash_extensions.enrich import Output, Input, State

from apps.data import *
from apps.utils import *
from pages.blue_detail import blue_nsi_data, blue_nsi_graph_data

home_elements = html.Div([
    dbc.Row([
        getTile(
            dbc.ListGroup(
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5("MetalCL"),
                                html.H5(html.I(className="fa fa-check-circle"), className="text-success"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("NFV Orchestrator"),
                                html.H5(html.I(className="fa fa-check-circle"), className="text-success"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("South-Bound OSS"),
                                html.H5(html.I(className="fa fa-exclamation-circle"), className="text-danger"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        )
                    ],
                    color="light"
                )
            ),
            style={'height': "250px"},
            color='primary',
            title="Connection Status",
            width=4
        ),
        getTile(
            dbc.ListGroup(
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5("Blueprint Instances"),
                                html.H5(id="home_no_blues"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("NFV Service Instances"),
                                html.H5(id="home_no_nsis"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("Day2 Primitives"),
                                html.H5(id="home_no_operations"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        )
                    ],
                    color="light"
                )
            ),
            style={'height': "250px"},
            color='info',
            title="Blueprints",
            width=4
        ),
        getTile(
            dbc.ListGroup(
                dbc.ListGroupItem(
                    [
                        html.Div(
                            [
                                html.H5("VIMs"),
                                html.H5(id="home_no_vims"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("Networks"),
                                html.H5(id="home_no_nets"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("Routers"),
                                html.H5(id="home_no_routers"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                        html.Div(
                            [
                                html.H5("Physical Deployment Units"),
                                html.H5(id="home_no_pdu"),
                            ],
                            className="d-flex w-100 justify-content-between"
                        ),
                    ],
                    color="light"
                )
            ),
            style={'height': "250px"},
            color='success',
            title="Virtual Topology",
            width=4
        )
    ]),
    dbc.Row(
        [
            getTile(
                html.Div(
                    visdcc.Network(
                        id='home_graph',
                        options=dict(height='500px', width='100%', autoResize=True),
                        data={'nodes': [], 'edges': []}
                    )
                ), title="Network Service Graph", color="light", width=6
            ),
            getTile(
                html.Div(
                    dcc.Graph(
                        id='home_bargraph',
                        figure={
                            'data': [
                                # {'x': [1, 2, 3], 'y': [4, 1, 2], 'type': 'bar', 'name': 'SF'},
                                # {'x': [1, 2, 3], 'y': [2, 4, 5], 'type': 'bar', 'name': u'Montréal'},
                            ],
                            'layout': {}
                        },
                    ),
                    style={'height': '500px'}
                ),
                width=6, color="light", title="Blueprint Instance Types",
            )
        ]
    ),
    dbc.Row(),
    dcc.Interval(
        id='home_refresh_interval',
        interval=refresh_interval * 1000,  # in milliseconds

    )
])


class homePage(WebPage):
    def __init__(self, app):
        super().__init__('topology_page', self.get_page_layout(), app)

    def get_page_layout(self):
        return home_elements

    def get_callbacks(self, app):
        @app.callback(
            [
                Output("home_no_blues", "children"),
                Output("home_no_nsis", "children"),
                Output("home_no_operations", "children"),
                Output("home_no_vims", "children"),
                Output("home_no_nets", "children"),
                Output("home_no_routers", "children"),
                Output("home_no_pdu", "children"),
                Output('home_graph', 'data'),
                Output('home_bargraph', 'figure')
            ],
            Input('home_refresh_interval', 'n_intervals'),
            State('home_graph', 'data')
        )
        def home_refresh(interval, previous_graph_data):
            live_data = get_dynamic_data()
            nodes = []
            edges = []
            bar_x = []
            bar_y = []
            no_operations = 0
            for blue in live_data['blue_detailed']:
                data = blue
                if blue['type'] not in bar_x:
                    bar_x.append(blue['type'])
                    bar_y.append(1)

                no_operations += len(blue['primitives'])
                nsi_data = blue_nsi_data(data['id'], live_data['nsi_data'], data)

                blue_vis_data = blue_nsi_graph_data(data['id'], data, nsi_data, self.app)
                edges += blue_vis_data['edges']
                for n in blue_vis_data['nodes']:
                    if n['id'] not in [item['id'] for item in nodes]:
                        nodes.append(n)

                if len(previous_graph_data['nodes']) == len(nodes) and len(previous_graph_data['edges']) == len(edges):
                    new_graph_data = dash.no_update
                else:
                    new_graph_data = {'nodes': nodes, 'edges': edges}

            return len(live_data['blue_detailed']), \
                   len(live_data['nsi_data']), \
                   no_operations, \
                   len(live_data['topology_data_raw']['vims']), \
                   len(live_data['topology_data_raw']['networks']), \
                   len(live_data['topology_data_raw']['routers']), \
                   len(live_data['pdu_data_raw']), \
                   new_graph_data, \
                   {'data': [{'x': bar_x, 'y': bar_y, 'type': 'bar'}]}
