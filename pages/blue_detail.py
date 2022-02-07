from datetime import datetime

import dash
import visdcc
from dash_extensions.enrich import Output, Input, State

# import json
from apps.data import get_dynamic_data
from apps.utils import *


def status_bar(data):
    print('####### {}'.format(data))
    return [
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 1},
            title="Blueprint Identifier",
            value=data['id'] if 'id' in data else '',
            icon="info-circle",
            color="primary",
            width=2
        ),
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 2},
            title="Blueprint Type",
            value=data['type'] if 'type' in data else '',
            icon="project-diagram",
            color="secondary",
            width=2),
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 3},
            title="Supported Operations",
            value=len(data['supported_ops']) if 'supported_ops' in data else 0,
            icon="tasks",
            color="danger",
            width=2),
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 4},
            title="NFV Services",
            color="info",
            value=len(data['ns']) if 'ns' in data else 0,
            icon="cubes",
            width=2),
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 5},
            title="Deployment VIMs",
            color="warning",
            value=len(data['vims'] if 'vims' in data else []),
            icon="cloud",
            width=2),
        dac.InfoBox(
            id={"id": "blue_detail", "type": "widget", "index": 6},
            title="Processed Day2 Actions",
            color="success",
            value=len(data['primitives']) if 'primitives' in data else 0,
            icon="play-circle",
            width=2)
    ]


nsi_columns = [
    {"title": "Instance", "field": "name"},
    {"title": "State", "field": "nsState"},
    {"title": "Current Ops", "field": "currentOperation"},
    {"title": "Ops Status", "field": 'operational-status'},
    {"title": "Created at", "field": 'create-time'},
    {"title": "VIM", "field": "vim"},
    {"title": "vCPU [#]", "field": "vcpu"},
    {"title": "RAM [GB]", "field": "ram"},
    {"title": "Disk [GB]", "field": "disk"},
]

config_columns = [
    {"title": "Parameter", "field": "key"},
    {"title": "Value", "field": "value"}
]

action_columns = [
    {"title": "Primitive Name", "field": "primitive"},
    {"title": "Network Service", "field": "ns_name"},
    {"title": "Result", "field": "result_status"},
    {"title": "Time", "field": "time"}
]

vnf_column = [
    {"title": "Name", "field": "name"},
    {"title": "Type", "field": "type"},
    {"title": "Mgt IP", "field": "mgt_ip"},
    {"title": "VNF Id", "field": "vnf_id"},
    {"title": "VIM", "field": "vim"}
]


def blue_nsi_graph_data(blue_id, blue_item, nsi_, app):
    nodes = []
    edges = []

    blue_nsi_ids = [item['nsi_id'] for item in blue_item['ns']]
    nsi_ = [item for item in nsi_ if item['_id'] in blue_nsi_ids]
    for n in nsi_:
        nodes.append({
            'id': n['name'],
            'label': n['name'],
            'shape': 'image',
            'image': app.get_asset_url('nsi_icon.png')
        })
        for vld in n['vld']:
            if 'vim_info' not in vld or not list(vld['vim_info']):
                continue
            vim_info_label = list(vld['vim_info'])[0]
            # print('^__^ vim_info: {}'.format(vim_info_label))
            if vld['vim_info'][vim_info_label]['vim_network_name'] not in [n_['id'] for n_ in nodes]:
                nodes.append({
                    'id': vld['vim_info'][vim_info_label]['vim_network_name'],
                    'label': vld['vim_info'][vim_info_label]['vim_network_name'],
                    'shape': 'image',
                    'image': app.get_asset_url('net_icon.png')
                })
            edges.append({
                # 'id': '{}-{}'.format(vld['vim_info'][vim_info_label]['vim_network_name'], n['name']),
                'from': vld['vim_info'][vim_info_label]['vim_network_name'],
                'to': n['name'],
                'color': {'color': 'gray'},
                'dashes': False
            })
    return {'nodes': nodes, 'edges': edges}


def blue_nsi_data(blue_id, nsi_data, blue_detailed_):
    blue_nsi_ids = [item['nsi_id'] for item in blue_detailed_['ns']]
    res = [item for item in nsi_data if item['_id'] in blue_nsi_ids]
    # updating vim with names and processing flavors
    for item in res:

        vcpu = 0
        ram = 0
        disk = 0
        for flavor in item['flavor']:
            vcpu += int(flavor['vcpu-count'] if 'vcpu-count' in flavor else 0)
            ram += int(flavor['memory-mb'] if 'memory-mb' in flavor else 0) / 1024
            disk += int(flavor['storage-gb'] if 'storage-gb' in flavor else 0)
        item.update(
            {
                'vim': next(i['vim'] for i in blue_detailed_['ns'] if i['nsi_id'] == item['_id']),
                'vcpu': vcpu,
                'ram': ram,
                'disk': disk,
                'create-time': item['create-time'] if isinstance(item['create-time'], str) else datetime.fromtimestamp(
                    item['create-time']).strftime("%m/%d/%Y, %H:%M:%S")
            }
        )
    return res


class BlueDetailPage:
    def __init__(self, app):
        self.app = app
        """
        self.data = []
        self.nsi_data = []
        
        self.vis_data = {}
        self.config_data = []
        self.op_history_data = []
        """
        pass

    def get_data(self, blue_id):
        pass
        """
        self.data = next((item for item in blue_detailed if item['id'] == blue_id), [])
        self.nsi_data = blue_nsi_data(blue_id)
        self.vis_data = blue_nsi_graph_data(blue_id, self.app)
        self.config_data = [{'key': k, 'value': self.data['config'][k]} for k in self.data['config'].keys()]
        self.op_history_data = [{
            'ns_name': item['primitive']['ns-name'],
            'primitive': item['primitive']['primitive_data']['primitive'],
            'result_status': item['result']['charm_status'],
            'time': item['time']
        } for item in self.data['primitives']]
        """

    # ovrerride WebPage
    def get(self, blue_id):
        if blue_id and blue_id != '':
            live_data = get_dynamic_data()
            data = next((item for item in live_data['blue_detailed'] if item['id'] == blue_id), [])
            config_data = [{'key': k, 'value': data['config'][k]} for k in data['config'].keys()]
        else:
            data = []
            config_data = []

        if blue_id is not '':
            self.get_data(blue_id)

        nsi_box = Box("NFV Service instances", build_table("nsi", nsi_columns, []))
        vnf_box = Box("VNF instances", build_table("vnfi", vnf_column, []))
        graph_box = Box(
            "Blueprint Graph",
            html.Div(
                visdcc.Network(
                    id='blue_detail_graph',
                    options=dict(height='300px', width='100%', autoResize=True),
                    data={'nodes': [], 'edges': []}
                )
            )
        )
        operations_box = Box(
            "Blueprint Operations",
            dbc.Col([
                dbc.Row(dbc.Button(
                    [html.I(className="fas fa-play-circle"), "     {}".format(ops)],
                    color=get_color(index),
                    style={'text-align': 'left', 'padding-left': '20%',
                           'margin': '5px', 'width': '100%'},
                )) for index, ops in enumerate(data['supported_ops'] if 'supported_ops' in data else [])
            ]))

        config_box = Box("Blueprint Configuration", build_table("blue_detail_config", config_columns, config_data))
        action_box = Box("History of Day2 Actions", build_table("action_history", action_columns, []))

        self.content = html.Div([
            dbc.Col(
                dbc.Row(
                    status_bar(data)
                ),
                width=12
            ),
            dbc.Row(
                [
                    dbc.Col(
                        [
                            nsi_box.get(),
                            vnf_box.get()
                        ], width=10
                    ),
                    dbc.Col(
                        operations_box.get(), width=2
                    )
                ]
            ),
            dbc.Row([
                dbc.Col(
                    graph_box.get(), width=4
                ),
                dbc.Col(
                    config_box.get(), width=4
                ),
                dbc.Col(
                    action_box.get(), width=4
                )
            ]),

            dcc.Interval(
                id='blue_detail_refresh_interval',
                interval=refresh_interval * 1000,  # in milliseconds

            )
        ], style={'height': '900px'})
        return self.content

    def get_callbacks(self, app):
        @app.callback(
            [
                Output({"id": "blue_detail", "type": "widget", "index": 4}, "value"),
                Output({"id": "blue_detail", "type": "widget", "index": 5}, "value"),
                Output({"id": "blue_detail", "type": "widget", "index": 6}, "value"),
                Output({'type': 'tabulator', 'name': 'nsi'}, "data"),
                Output({'type': 'tabulator', 'name': 'vnfi'}, "data"),
                Output({'type': 'tabulator', 'name': 'action_history'}, "data"),
                Output({'type': 'tabulator', 'name': 'blue_detail_config'}, 'data'),
                Output('blue_detail_graph', 'data')
            ],
            Input('blue_detail_refresh_interval', 'n_intervals'),
            [
                State('url', 'search'),
                State({"id": "blue_detail", "type": "widget", "index": 1}, 'value'),
                State('blue_detail_graph', 'data')
            ]
        )
        def blue_detail_refresh(interval, search, widget_id, previous_graph_data):
            if not search or search == '':
                id_ = widget_id
            else:
                id_ = search
            # print("blue_detail_refresh id={}".format(id_))
            self.get_data(id_)
            live_data = get_dynamic_data()

            data = next((item for item in live_data['blue_detailed'] if item['id'] == id_), [])

            nsi_data = blue_nsi_data(id_, live_data['nsi_data'], data)

            blue_vnfi = live_data['vnf_data'][id_]
            vis_data = blue_nsi_graph_data(id_, data, nsi_data, self.app)
            if len(vis_data['nodes']) == len(previous_graph_data['nodes']) and \
                    len(vis_data['edges']) == len(previous_graph_data['edges']):
                vis_data = dash.no_update

            config_data = [{'key': k, 'value': data['config'][k]} for k in data['config'].keys()]
            op_history_data = [{
                'ns_name': item['primitive']['ns-name'],
                'primitive': item['primitive']['primitive_data']['primitive'],
                'result_status': item['result']['charm_status'],
                'time': item['time']
            } for item in data['primitives']]



            # print('?????????????????????')
            # print(config_data)
            # print(op_history_data)
            # print('?????????????????????')
            return \
                len(data['ns']), \
                len(data['vims']), \
                len(data['primitives']), \
                nsi_data, \
                blue_vnfi, \
                op_history_data, \
                config_data, \
                vis_data
