import dash
from dash_extensions.enrich import Output, Input, State
# from dash_extensions.javascript import Namespace

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
            Input('blueprints_interval', 'n_intervals'),
            State({'type': 'tabulator', 'name': 'blueprints'}, "data")
        )
        def blueprints_refresh(interval, old_data):
            data = get_dynamic_data()['blue_data_generic']
            for item in data:
                label = item['id'] if 'id' in item else item['name']
                item['open'] = "{}?id={}".format('/showblue', label)
                item['delete'] = "{}?id={}".format('/delblue', label)
            need_update = len(data) != len(old_data)

            if not need_update:
                for item in data:
                    for old in old_data:
                        if old['id'] == item['id']:
                            if item['status'] != old['status'] or item['detailed_status'] != old['detailed_status']:
                                print("------ {} != {} or {} != {} ----update True".format(item['status'], old['status'], item['detailed_status'], old['detailed_status']))
                                need_update = True
                                break
            res = data if need_update else dash.no_update
            return res  # , blue_columns

