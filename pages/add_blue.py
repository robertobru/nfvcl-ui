import dash
from dash_extensions.enrich import Output, Input, State, ALL

from apps.data import *
from apps.utils import *

# base_data_scheme = {
#     {'id': 'config', 'label': "Parameter Configuration", 'type': 'object'},
#     {'id': 'vims', 'label': "Selection of TACs and VIMs", 'type': 'list'}
# }

form_data = {
    'Open5GS': [
        {'id': 'plmn', 'label': 'PLMN', 'type': 'string', 'example': '00101', 'mandatory': True},
        {'id': 'mgt_net', 'label': 'Management Network', 'type': 'network', 'mandatory': True},
        {'id': 'sgi_net', 'label': 'Default DNN/SGI Network', 'type': 'network', 'mandatory': True},
        {'id': 'wan_net', 'label': 'Default DNN/SGI Network', 'type': 'network', 'mandatory': True},
        {'id': 'slice', 'label': '5G Slice SST/SD', 'type': 'string', 'mandatory': False}
    ],
    'Open5Gs_K8s': [
        {'id': 'plmn', 'label': 'PLMN', 'type': 'string', 'example': '00101', 'mandatory': True},
        {'id': 'mgt_net', 'label': 'Management Network', 'type': 'network', 'mandatory': True},
        {'id': 'sgi_net', 'label': 'Default DNN/SGI Network', 'type': 'network', 'mandatory': True},
        {'id': 'wan_net', 'label': 'Default WAN Network', 'type': 'network', 'mandatory': True},
        {'id': 'slice', 'label': '5G Slice SST/SD', 'type': 'string', 'mandatory': False}
    ],
    'UeRanSimBlue': [
        {'id': 'plmn', 'label': 'PLMN', 'type': 'string', 'example': '00101', 'mandatory': True},
        {'id': 'mgt_net', 'label': 'Management Network', 'type': 'network', 'mandatory': True},
        {'id': 'sgi_net', 'label': 'Default DNN/SGI Network', 'type': 'network', 'mandatory': True},
        {'id': 'wan_net', 'label': 'Default WAN Network', 'type': 'network', 'mandatory': True},
        {'id': 'ue', 'label': 'User Equipment', 'type': 'string', 'mandatory': False}
    ],
    'K8s': [
        {'id': 'mgt_net', 'label': 'Management Network', 'type': 'network', 'mandatory': True},
        {'id': 'sgi_net', 'label': 'Default DNN/SGI Network', 'type': 'network', 'mandatory': True},
        {'id': 'wan_net', 'label': 'Default WAN Network', 'type': 'network', 'mandatory': True},
        {'id': 'cni', 'label': 'Container Net Plugin', 'type': 'string', 'mandatory': False},
        {'id': 'lb_pool', 'label': 'Load Balancer Pool Net', 'type': 'string', 'mandatory': False}
    ]
}


class AddBluePage(WebPage):
    def __init__(self, app):
        self.app = app
        self.blue_types = [item['id'] for item in blue_type]
        super().__init__('add_blue_page', self.get_page_layout(), app)

    def get_page_layout(self):
        blue_form_ = dbc.Col(
            [
                dbc.Row(Box("Select Blueprint type", schema_selector('blue_type_dropdown', self.blue_types),
                            width=12).get()),
                dbc.Row([
                    Box("Blueprint Configuration Parameters", [], width=12, id='content_blue_config_form',
                        content_id='content_blue_config_form_body').get(),
                    Box("Blueprint Deployment Parameters",
                        [
                            dbc.Row([
                                dbc.Label("Select VIMs to be used", html_for='addblue_selected_vimlist', width=2),
                                dbc.Col(
                                    dcc.Dropdown(
                                        options=[],
                                        multi=True,
                                        className='input-group',
                                        id='addblue_selected_vimlist'
                                    ),
                                    width=10
                                )
                            ]),
                            dbc.Row(id='addblue_vim_config'),
                            dbc.Row(dbc.Button([html.I(className='fas fa-plus-circle'), "  Add TAC"],
                                               id='addblue_addtac_button', color="info")),
                            dbc.Row(dbc.Col([], id='addblue_tac_config'))
                        ],
                        width=12,
                        id='content_blue_deploy_form',
                        ).get()],
                    id='blue_form', style={"display": "none"}
                ),
                # dbc.Row([
                #     Box(
                #         "Blueprint Intent Editing",
                #         dash_ace.DashAceEditor(
                #             id='blue_intent_editor',
                #             value=[],
                #             theme='github',
                #             mode='json',
                #             tabSize=2,
                #         ),
                #         width=12,
                #         id='content_blue_edit',
                #         content_id='content_blue_config_form_body',
                #         style={"display": "none"}
                #     ).get(),
                # ]),

                dbc.Row([
                    dbc.Button(
                        [html.I(className='fas fa-arrow-circle-right'), " Submit"],
                        id='addblue_submit_button',
                        color="primary",
                        style={"display": "none", "margin-left": "6px"}
                    ),
                    dbc.Button(
                        [html.I(className='fas fa-edit'), " Edit"],
                        id='addblue_edit_button',
                        color="info",
                        style={"display": "none", "margin-left": "20px"}
                    )
                ]
                ),
                dbc.Row(dbc.Col([], id='addblue_submit_result', width=12))

            ], width=12)

        return blue_form_

    def get_callbacks(self, app):

        @app.callback(
            [
                Output('content_blue_config_form_body', 'children'),
                Output('addblue_selected_vimlist', "options", ),
                Output('blue_form', 'style'),
                Output('addblue_submit_button', 'style'),
                Output('addblue_edit_button', 'style'),
                # Output('content_blue_edit', 'style'),
            ],
            Input('blue_type_dropdown', 'value'),
        )
        def display_vim_form(value):
            if value in self.blue_types:
                config_fields = form_data[value] if value in form_data else []
                vims_list = [{'label': item['name'], 'value': item['name']} for item in topology_data_raw['vims']]
                config_params = config_input_panel_withopt(
                    config_fields, topology_data_raw, 'blue_add_data', submit_button=False
                )
                return config_params, vims_list, {"display": "block"}, {"display": "block", "margin-left": "6px"}, \
                       {"display": "block", "margin-left": "20px"}, \
                    # {"display": "block"}

        @app.callback(
            Output('blue_add_data_optional_configs', 'children'),
            Input('blue_add_data_addoptions_button', 'n_clicks'),
            [
                State('blue_add_data_optional_configs', 'children'),
                State('blue_type_dropdown', 'value')
            ]
        )
        def add_config_options(click, children, blue):
            optional_inputs = [{
                'label': item['label'],
                'value': item['id'],
            } for item in form_data[blue] if not item['mandatory']]
            if children is None:
                children = []

            # inputs_lines = []
            # if optional_inputs['type'] == 'object':
            #    for

            children.append(
                # dbc.Col(
                dbc.Label(dcc.Dropdown(
                    options=optional_inputs,
                    id={'type': 'config', 'index': len(children), 'id': 'label'}
                ), width=2,
                )
            )
            # if optional_inputs['type'] == 'textarea':
            #     children.append(dbc.Col(
            #         dbc.Textarea(
            #             type=optional_inputs['type'],
            #             id={'type': 'config', 'index': len(children), 'id': 'value'}
            #         ), width=10, style={'margin-top': '6px'}))
            # else:
            children.append(dbc.Col(
                dbc.Input(
                    # type=optional_inputs['type'],
                    id={'type': 'config', 'index': len(children), 'id': 'value'}
                ), width=10, style={'margin-top': '6px'}))

            return children

        @app.callback(Output('addblue_tac_config', 'children'),
                      Input('addblue_addtac_button', 'n_clicks'),
                      [State('addblue_tac_config', 'children'), State('addblue_selected_vimlist', 'value')])
        def addblue_addtac_button(click, value, selected_vims):
            index = len(value)
            vim_options_ = [{'label': item, 'value': item} for item in selected_vims]

            input_element = dbc.Input(
                type='number',
                id={'type': 'tac', 'index': index, 'id': 'tac'}
            )
            vim_selection = dcc.Dropdown(
                options=vim_options_,
                className='input-group',
                id={'type': 'tac', 'index': index, 'id': 'vim'}
            )

            res = dbc.Row(
                [
                    dbc.Label('TAC identifier', width=2),
                    dbc.Col(input_element, width=4),
                    dbc.Label('VIM to select', width=2),
                    dbc.Col(vim_selection, width=4),
                ],
                className="mb-3"
            )

            value.append(res)
            return value

        @app.callback(Output('addblue_vim_config', 'children'),
                      Input('addblue_selected_vimlist', 'value'))
        def addblue_vim_config(value):
            print(value)
            self.selected_vims = value
            options_ = [{'label': item, 'value': item} for item in value]
            res = [
                dbc.Label("VIM where to deploy core functions", html_for='addblue_selected_corevim', width=2),
                dbc.Col(
                    dcc.Dropdown(
                        options=options_,
                        className='input-group',
                        id='addblue_core_vim'
                    ),
                    width=10
                )
            ]

            return res

        @app.callback(
            Output('addblue_submit_result', 'children'),
            Input('addblue_submit_button', 'n_clicks'),
            [
                State('blue_type_dropdown', 'value'),
                State({'type': 'blue_add_data', 'index': ALL, 'id': ALL}, 'value'),
                State('addblue_selected_vimlist', 'value'),
                State({'type': 'tac', 'index': ALL, 'id': ALL}, 'value'),
                State('addblue_core_vim', 'value')
            ]
        )
        def update_output(clicks, *args):
            print('button clicked')
            if clicks is not None:
                print('@@@@@@@@@@@@@@@@@@@@')
                print(dash.callback_context.states_list)
                print(input_data_to_dict(dash.callback_context.states_list))
                print('@@@@@@@@@@@@@@@@@@@@')

                blue_type = next((item['value'] for item in dash.callback_context.states_list \
                                  if item['id'] == 'blue_type_dropdown'), None)

                msg_body = {
                    'type': blue_type,
                    'config': {},
                    'vims': []
                }
                if blue_type == 'Open5Gs_K8s':
                    plmn = next((item['value'] for item in dash.callback_context.states_list[1] \
                                 if item['id']['id'] == 'plmn'), None)

                    msg_body.update({'plmn': plmn})
                    wan = next((item['value'] for item in dash.callback_context.states_list[1] \
                                if item['id']['id'] == 'wan_net'), None)
                    mgt = next((item['value'] for item in dash.callback_context.states_list[1] \
                                if item['id']['id'] == 'mgt_net'), None)
                    sgi = next((item['value'] for item in dash.callback_context.states_list[1] \
                                if item['id']['id'] == 'sgi_net'), None)
                    vim_list = next((item['value'] for item in dash.callback_context.states_list \
                                     if isinstance(item, dict) and item['id'] == 'addblue_selected_vimlist'), [])
                    vim_core = next((item['value'] for item in dash.callback_context.states_list \
                                     if isinstance(item, dict) and item['id'] == 'addblue_core_vim'), None)
                    for v in vim_list:
                        msg_body['vims'].append(
                            {
                                'name': v,
                                'tenant': 'admin',
                                'core': True if v == vim_core else False,
                                'wan': {
                                    'id': wan
                                },
                                'mgt': mgt,
                                'sgi': sgi,
                                'tacs': []
                            }
                        )
                    print(msg_body)
                    code, rmesg = add_blue(msg_body)
                    if code < 300 and code > 199:
                        color = 'success'
                    else:
                        color = 'danger'

                    return [dbc.Badge(code, color=color), json.dumps(rmesg)]