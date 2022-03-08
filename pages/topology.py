import visdcc

from apps.data import *
from apps.utils import *


def topology_vis_data(data, pdu_data, app):
    print("------------data--------------\n{}\n------------------------------".format(data))
    nodes = []
    edges = []

    common_networks = []
    if 'networks' in data:
        for n in data['networks']:
            print('now working on {}'.format(n['name']))
            if n['type'] == "vlan":
                nodes.append({
                    'id': n['name'],
                    'label': n['name'],
                    'shape': 'image',
                    'image': app.get_asset_url('lan2.png')
                })
                common_networks.append(n['name'])

    if 'vims' in data:
        for v in data['vims']:
            print('now working on {}'.format(v['name']))
            nodes.append({
                'id': v['name'], 'label': "{}@{}".format(v['vim_tenant_name'], v['name']),
                'shape': 'image',
                'image': app.get_asset_url('dc.png')
            })
            for n in v['networks']:
                if n['name'] not in common_networks:
                    # in this case we have a different net instance per VIM
                    nodes.append({
                        'id': "{}_{}".format(n['name'], v['name']),
                        'label': "{}@{}".format(n['name'], v['name']),
                        'shape': 'image',
                        'image': app.get_asset_url('lan.png')
                    })
                    edges.append({
                        'id': '{}-{}'.format(n['name'], v['name']),
                        'from': v['name'],
                        'to': "{}_{}".format(n['name'], v['name']),
                        'color': {'color': 'gray'},
                        'dashes': True
                    })
                else:
                    # single net instance for all the openstack
                    edges.append({
                        'id': n['name'],
                        'from': v['name'],
                        'to': n['name'],
                        'color': {'color': 'gray'},
                        'dashes': True,
                        'length': 100
                    })
            for r in v['routers']:
                nodes.append({
                    'id': "{}_{}".format(r['name'], v['name']),
                    'label': "{}@{}".format(r['name'], v['name']),
                    'shape': 'image',
                    'image': app.get_asset_url('router.png')
                })
                edges.append({
                    'id': '{}-{}'.format(r['name'], v['name']),
                    'from': v['name'],
                    'to': "{}_{}".format(r['name'], v['name']),
                    'color': {'color': 'gray'},
                    'dashes': True
                })

                r_descriptor = next(item for item in data['routers'] if item['name'] == r['name'])
                for p in r_descriptor['ports']:
                    net_node_id = p['net'] if p['net'] in common_networks else '{}_{}'.format(p['net'], v['name'])
                    print("############ {} ------ {}".format(r_descriptor['name'], net_node_id))
                    edges.append({
                        'id': '{}_{}_{}'.format(r['name'], v['name'], net_node_id),
                        'from': net_node_id,
                        'to': "{}_{}".format(r['name'], v['name']),
                        'color': {'color': 'blue'},
                        'dashes': False
                    })

            for pdu in pdu_data:
                nodes.append({
                    'id': pdu['name'], 'label': pdu['name'], 'shape': 'image', 'image': app.get_asset_url('nb.png')
                })
                for i in pdu['interface']:
                    edges.append({
                        'id': "{}-{}".format(pdu['name'], i['vim-network-name']),
                        'from': pdu['name'],
                        'to': i['vim-network-name']
                    })

    res = {'nodes': nodes, 'edges': edges}

    return {'nodes': nodes, 'edges': edges}


vim_columns = [
    {"title": "Name", "field": "name"},
    {"title": "Type", "field": "vim_type"},
    {"title": "Tenant", "field": "vim_tenant_name"},
    {"title": "# Networks", "field": "no_networks"},
    {"title": "# Routers", "field": "no_routers"},
]


def topology_vimtable_dataproc(data):
    return [{
        'name': v['name'],
        'vim_type': v['vim_type'],
        'vim_tenant_name': v['vim_tenant_name'],
        'no_networks': len(v['networks']),
        'no_routers': len(v['routers']),
        'delete': '/del_vim?id={}'.format(v['name']),
        'open': '/show_vim?id={}'.format(v['name'])
    } for v in data['vims']]


vim_table = build_table(
    "vims",
    vim_columns,
    topology_data_raw,
    bottom_buttons=[{
        'icon': 'fa-plus-circle',
        'label': 'Add VIM',
        'id': 'add_vim',
        'color': 'primary',
        'href': '/addvim'
    }, {
        'icon': 'fa-edit',
        'label': 'Manage VIM',
        'id': 'add_net_vim',
        'color': 'info',
        'href': '/editvim'
    }

    ],
    intable_buttons=['delete', 'open'],
    interval={'delta_t': 3},
    data_function=topology_vimtable_dataproc,
    hrefs_={'delete': '/vim_delete', 'open': '/vim'}
)

nets_columns = [
    {"title": "Name", "field": "name"},
    {"title": "Type", "field": "type"},
    {"title": "External", "field": "external"},
    {"title": "cidr", "field": "cidr"},

]


def topology_nettable_dataproc(data):
    return data['networks']


nets_table = build_table(
    "nets",
    nets_columns,
    topology_data_raw,
    bottom_buttons=[{
        'icon': 'fa-plus-circle',
        'label': 'Add Network',
        'id': 'add_net',
        'color': 'primary',
        'href': '/addnet',
        'width': '50px'
    }],
    intable_buttons=['delete', 'open'],
    interval={'delta_t': 3},
    data_function=topology_nettable_dataproc,
    hrefs_={'delete': '/net_delete', 'open': '/net'},
    groupby="type"
)

routers_columns = [
    {"title": "Name", "field": "name"},
    {"title": "# Networks", "field": "no_nets"},
    {"title": "IP Addresses", "field": "net_list", "width": 250}
]


def topology_routertable_dataproc(data):
    return [{
        'name': r['name'],
        'no_nets': len(r['ports']),
        'net_list': ' '.join(["{} ".format(p['ip_addr']) for p in r['ports']])
    } for r in data['routers']]


routers_table = build_table(
    "routers",
    routers_columns,
    topology_data_raw,
    bottom_buttons=[{
        'icon': 'fa-plus-circle',
        'label': 'Add Router',
        'id': 'add_router',
        'color': 'primary',
        'href': '/addrouter'
    }],
    intable_buttons=['delete', 'open'],
    interval={'delta_t': 3},
    data_function=topology_routertable_dataproc,
    hrefs_={'delete': '/router_delete', 'open': '/router'}
)

pdu_columns = [
    {"title": "Name", "field": "name"},
    {"title": "Type", "field": "type"},
    {"title": "TAC", "field": "tac"},
    {"title": "Implementation", "field": "implementation"},
    {"title": "No. Networks", "field": "no_nets"},
    {"title": "Mgt IP Address", "field": "mgt_ip"}
]


def topology_pdu_dataproc(data):
    print('???????????? {}'.format(data))
    return [{
        'name': r['name'],
        'type': r['type'],
        'tac': r['tac'],
        'implementation': r['implementation'],
        'no_nets': len(r['interface']),
        'mgt_ip': '{}'.format(next((i['ip-address'] for i in r['interface'] if 'mgmt' in i and i['mgmt']), ''))
    } for r in data]


pdu_table = build_table(
    "pdu",
    pdu_columns,
    topology_pdu_dataproc(pdu_data_raw),
    bottom_buttons=[{
        'icon': 'fa-plus-circle',
        'label': 'Add PDU',
        'id': 'add_pdu',
        'color': 'primary',
        'href': '/addpdu'
    }],
    intable_buttons=['delete', 'open'],
    interval={'delta_t': 3},
    # data_function=topology_pdu_dataproc,
    hrefs_={'delete': '/router_delete', 'open': '/router'}
)


class TopologyPage(WebPage):
    def __init__(self, app):
        self.vim_box = Box("VIMs", vim_table)
        self.net_box = Box("Networks", nets_table)
        self.router_box = Box("Routers", routers_table)
        self.pdu_box = Box("Physical Deployment Units", pdu_table)
        self.topology_graph_box = Box(
            "Topology",
            html.Div([
                visdcc.Network(
                    id='net',
                    options=dict(height='800px', width='100%', autoResize=True),
                    data=topology_vis_data(topology_data_raw, pdu_data_raw, app)
                ),
                dcc.Interval(
                    id='interval-component',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=0
                )
            ])
        )

        super().__init__('topology_page', self.get_page_layout(), app)

    def get_page_layout(self):
        return dbc.Row(
            [
                dbc.Col([
                    self.vim_box.get(),
                    self.net_box.get(),
                    self.router_box.get(),
                    self.pdu_box.get()
                ], width=7),
                dbc.Col(self.topology_graph_box.get(), width=5)
            ], id='topology_overview')

    def get_callbacks(self, app):
        """
        @app.callback(Output('output', 'children'), [Input('vims_table', 'cellClick')])
        def display_table_button(cell_raw):
            print(cell_raw)
            try:
                cell = json.loads(cell_raw)
                if 'field' in cell['column']:
                    if cell['column']['field'] == 'delete':
                        vim_id = cell['value']['name']
                        print('pressed button to delete vim {}'.format(vim_id))
                        return 'pressed button to delete vim {}'.format(vim_id)
                    if cell['column']['field'] == 'open':
                        vim_id = cell['value']['name']
                        print('press button to open vim {}'.format(vim_id))
                        return 'pressed button to open vim {}'.format(vim_id)
                return
            except Exception as e:
                print("[display_output] received exception: {}".format(e))



        @app.callback(Output('net', 'children'), [Input('addVim', 'n_clicks')])
        def topology_add_vim_button(click):
            print("AddVim clicked ---- {}".format(click))
            return 'AddVim clicked'
"""
