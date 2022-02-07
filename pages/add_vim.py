import dash
from dash_extensions.enrich import Output, Input, State, ALL

from apps.utils import *


class AddVimPage(WebPage):
    def __init__(self, app):
        self.app = app
        self.vim_types = ['openstack']
        self.data = [
            {'id': 'name', 'label': 'Name', 'type': 'string', 'example': 'os-#'},
            {'id': 'vim_url', 'label': 'Idendity URL', 'type': 'url', 'example': 'http://os-#.maas:5000/v3'},
            {'id': 'vim_user', 'label': 'User', 'type': 'string', 'example': 'admin'},
            {'id': 'vim_password', 'label': 'Password', 'type': 'password', 'example': ''},
            {'id': 'api_version', 'label': 'API version', 'type': 'string', 'example': 'v3.3'},
            {'id': 'insecure', 'label': 'Allow HTTP', 'type': 'bool'}
        ]
        super().__init__('add_vim_page', self.get_page_layout(), app)

    def get_page_layout(self):
        add_vim_form = dbc.Col(
            [

                Box("Select VIM type", schema_selector('vim_type_dropdown', self.vim_types), width=12).get(),
                Box("Openstack Configuration", config_input_panel(self.data, 'openstack_to_add_data'), width=12,
                    id='content_openstack_form', style={"display": 'none'}).get(),
            ], width=12)

        return add_vim_form

    def get_callbacks(self, app):
        @app.callback(Output('content_openstack_form', 'style'), Input('vim_type_dropdown', 'value'))
        def display_vim_form(value):
            print(value)

            if value == 'openstack':
                print('raised')
                return {'display': 'block'}
            else:
                return {'display': 'none'}

        @app.callback(
            Output('openstack_to_add_data_result', 'children'),
            Input('openstack_to_add_data_submit_button', 'n_clicks'),
            State({'type': 'openstack_to_add_data', 'index': ALL, 'id': ALL}, 'value')
        )
        def update_output(clicks, value):
            print('button clicked')
            if clicks is not None:
                print('@@@@@@@@@@@@@@@@@@@@')
                print(input_data_to_dict(dash.callback_context.states_list))
                print('@@@@@@@@@@@@@@@@@@@@')
