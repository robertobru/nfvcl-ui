import json

import dash_admin_components as dac
import dash_bootstrap_components as dbc
import dash_tabulator
from dash import html, dcc
from dash_extensions.javascript import Namespace

refresh_interval = 1
color = [
    'primary',
    'secondary',
    'danger',
    'warning',
    'info',
    'success',
    'dark'
]


def get_color(i: int):
    return color[i % len(color)]


class WebPage:
    def __init__(self, id_, children_, app_):
        self.content = dac.TabItem(id=id_, children=children_)
        self.callbacks = []
        self.app = app_

    def get(self):
        return self.content

    def get_callbacks(self, app):
        return self.callbacks


class Box:
    def __init__(self, title, children, **kwargs):
        if 'width' not in kwargs:
            kwargs['width'] = 12
        if 'color' not in kwargs:
            kwargs['color'] = 'primary'
        if 'content_id' in kwargs:
            body = dac.BoxBody(children=children, id=kwargs['content_id'])
            kwargs.pop('content_id')
        else:
            body = dac.BoxBody(children=children)
        self.box = dac.Box(
            [
                dac.BoxHeader(collapsible=True, closable=False, title=title),
                body
            ],
            **kwargs
        )

    def get(self):
        return self.box


def build_table(name, columns, data, bottom_buttons=None, intable_buttons=None, hrefs_=None, interval=None,
                data_function=None, groupby=None):
    res = []
    ns = Namespace("myNamespace", "tabulator")
    options = {"selectable": "false", 'cellClick': ns('cellLog')}
    if groupby:
        options["groupBy"] = groupby
    if isinstance(data, str):
        data = json.loads(data)
    for c in columns:
        c.update({"hozAlign": "left", "vertAlign": "middle", "headerFilter": False})

    if intable_buttons:
        if 'delete' in intable_buttons:
            columns.append({
                "field": "delete",
                "width": 50,
                "hozAlign": "center",
                "headerSort": False,
                "resizable": False,
                "formatter": ns('buttonDelete')
            })
            if hrefs_ and 'delete' in hrefs_ and data_function is None:
                # print('**** {}'.format(data))
                for item in data:
                    label = item['id'] if 'id' in item else item['name']
                    item['delete'] = "{}?id={}".format(hrefs_['delete'], label)

        if 'open' in intable_buttons:
            columns.append({
                "field": "open",
                "width": 50,
                "hozAlign": "center",
                "headerSort": False,
                "resizable": False,
                "formatter": ns('buttonInfo')
            })
            if hrefs_ and 'open' in hrefs_ and data_function is None:
                for item in data:
                    label = item['id'] if 'id' in item else item['name']
                    item['open'] = "{}?id={}".format(hrefs_['open'], label)

                # print(data)

    res.append(dash_tabulator.DashTabulator(
        id={'type': 'tabulator', 'name': name},
        columns=columns,
        data=data if data_function is None else data_function(data),
        options=options,
        theme='bootstrap/tabulator_bootstrap'
    ))
    if bottom_buttons:
        buttons = []
        for b in bottom_buttons:
            children_ = [html.I(className='fa {}'.format(b['icon'])), "  {}".format(b['label'])]
            if 'href' in b:
                buttons.append(dcc.Link(children=children_, href=b['href'],
                                        className="btn btn-{}".format(b['color']), style={'margin-left': '12px', 'width': '140px'}))
            else:
                buttons.append(dbc.Button(
                    children_,
                    id=b['id'],
                    color=b['color']
                ))
        res.append(dbc.Row(buttons, justify='end'))
    if interval:
        res.append(dcc.Interval(
            id='{}-topology-interval'.format(name),
            interval=interval['delta_t'] * 1000,  # in milliseconds
            n_intervals=0,
            max_intervals=0
        ))
    return res


def input_data_to_dict(raw_data):
    res = {}
    for input_ in raw_data:
        if isinstance(input_, list):
            for item in input_:
                if 'property' in item and 'value' in item and 'id' in item and 'id' in item['id']:
                    res[item['id']['id']] = item['value']
        else:
            if 'property' in input_ and 'value' in input_ and 'id' in input_ and 'id' in input_['id']:
                res[input_['id']['id']] = input_['value']
    return res


def schema_selector(id_, options_):
    options = [{'label': item, 'value': item} for item in options_]
    return dcc.Dropdown(
        id=id_,
        options=options,
    )


def config_input_panel_withopt(input_data, raw_data, type_tag, submit_button=True):
    # lets declare an initial form only with mandatory parameters
    form = [config_input_panel([item for item in input_data if item['mandatory']], type_tag, submit_button=False,
                               raw_data=raw_data)]
    optional_inputs = [item for item in input_data if not item['mandatory']]
    if optional_inputs:
        form.append(dbc.Row(dbc.Button([html.I(className='fas fa-add-circle'), " Options"],
                                       id='{}_addoptions_button'.format(type_tag), color="info")))
        form.append(dbc.Row(id='{}_optional_configs'.format(type_tag)))
    if submit_button:
        form.append(dbc.Row(dbc.Button("Submit", id='{}_submit_button'.format(type_tag), color="primary")))
        form.append(dbc.Row(html.Div(id='{}_submit_result'.format(type_tag))))
    return form


def config_input_panel(input_data, type_tag, submit_button=True, raw_data=None):
    form = []
    # input_data = {'label name': xxx, 'var name', type}
    for index, item in enumerate(input_data):
        if item['type'] == 'bool':
            input_element = dbc.Checklist(
                options=[{'value': 1}],
                # type=item['type'],
                id={'type': type_tag, 'index': index, 'id': item['id']},
                switch=True,
                value=[1]
            )
        elif item['type'] == 'network':
            options_ = [{'label': n['name'], 'value': n['name']} for n in raw_data['networks']]
            input_element = dcc.Dropdown(
                options=options_,
                className='input-group',
                id={'type': type_tag, 'index': index, 'id': item['id']}
            )
        else:
            input_element = dbc.Input(
                type=item['type'],
                id={'type': type_tag, 'index': index, 'id': item['id']},
                value=item['example']
            )

        form.append(
            dbc.Row(
                [
                    dbc.Label(item['label'], html_for=item['id'], width=2),
                    dbc.Col(input_element, width=10)
                ],
                className="mb-3"
            )
        )
    if submit_button:
        form.append(dbc.Row(dbc.Button("Submit", id='{}_submit_button'.format(type_tag), color="primary")))
        form.append(dbc.Row(html.Div(id='{}_submit_result'.format(type_tag))))
    return dbc.Form(form)


def getTile(body, color='light', title='', collapsible=False, closable=False, solid_header=False, elevation=4, width=2,
            style=None):
    if not style:
        style = {}
    return dac.Box(
        [
            dac.BoxHeader(
                collapsible=collapsible,
                closable=closable,
                title=title,
            ),
            dac.BoxBody(body)
        ],
        style=style,
        gradient_color=color,
        solid_header=solid_header,
        elevation=elevation,
        width=width,
        # className='info-box'
    )
