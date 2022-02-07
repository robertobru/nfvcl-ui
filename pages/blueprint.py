from dash_extensions.enrich import Output, Input
from dash_extensions.javascript import Namespace

from apps.data import get_dynamic_data
from apps.utils import *


def blue_table_data(data, app):
    return


ns = Namespace("myNamespace", "tabulator")

blue_columns = [
    {"title": "Name", "field": "id"},
    {"title": "Type", "field": "type"},
    {"title": "Status", "field": "status", "width": 50, "hozAlign": "center", "resizable": False,
     "formatter": ns('statusled')},
    {"title": "Progress", "field": "detailed_status"},
    {"title": "Operation", "field": "current_operation"},
    {"title": "Created", "field": "created"},
    {"title": "Modified", "field": "modified"},
    {"title": "# VIMs", "field": "no_vims"},
    {"title": "# Network Services", "field": "no_nsd"},
    {"title": "# Primitives", "field": "no_primitives"},
]

blue_table = build_table(
    "blueprints",
    blue_columns,
    [],
    bottom_buttons=[{
        'icon': 'fa-plus-circle',
        'label': 'Add Blueprint',
        'id': 'add_blue',
        'color': 'primary',
        'href': '/addblue'
    }],
    intable_buttons=['delete', 'open'],
    hrefs_={'delete': '/blue_delete', 'open': '/blue_detail'}
)


class BluePage(WebPage):
    def __init__(self, app):
        self.blue_box = Box("Blueprint Instances", blue_table, width=12)
        super().__init__('topology_page', self.get_page_layout(), app)

    def get_page_layout(self):
        return dbc.Row(
            [
                dbc.Col(
                    [
                        self.blue_box.get(),
                    ],
                    width={"size": 12}),
                dcc.Interval(
                    id='blueprints_interval',
                    interval=1 * 1000,  # in milliseconds
                    n_intervals=1,
                    max_intervals=-1
                )
            ], id='blue_overview')

    def get_callbacks(self, app):
        @app.callback(
            [
                Output({'type': 'tabulator', 'name': 'blueprints'}, "data"),
                # Output("blueprints_table", "columns")
            ],
            Input('blueprints_interval', 'n_intervals')
        )
        def blueprints_refresh(interval):
            global blue_data_generic

            # labels = [b['id'] for b in get_dynamic_data()['blue_data_generic']]
            # print('---------- blueprints_refresh {}'.format(labels))
            data = get_dynamic_data()['blue_data_generic']
            for item in data:
                label = item['id'] if 'id' in item else item['name']
                item['open'] = "{}?id={}".format('/showblue', label)
                item['delete'] = "{}?id={}".format('/delblue', label)
            return data  # , blue_columns

        """
        @app.callback(
            [
                Output('url', 'href'),
                #Output('url', 'search')
            ],
            Input("blueprints_table", "cellClick")
        )
        def redirect_by_button(cell):
            print(isinstance(cell, str))
            print(cell)
            cell = json.loads(cell)
            print(isinstance(cell, dict))
            print("$$$ {}".format(cell['column']['field']))
            if cell['column']['field'] == 'open':
                print(cell['value']['open'])
                return cell['value']['open']
            if cell['column']['field'] == 'delete':
                print(cell['value']['delete'])
                return cell['value']['delete']
            print('no match')
            PreventUpdate
        """
