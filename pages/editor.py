import dash_ace
from dash_extensions.enrich import Output, Input, State
from apps.utils import *


class Editor(WebPage):
    def __init__(self, app):
        # self.blue_box = Box("Blueprint Instances", blue_table, width=12)
        super().__init__('Editor', self.get_page_layout(), app)

    def get_page_layout(self, value=[]):
        return dbc.Row([
            getTile(
                dbc.Col([
                    dbc.Row([
                        dcc.Dropdown(
                            options=[
                                {"label": "POST", "value": "POST"},
                                {"label": "GET", "value": "GET"},
                                {"label": "PUT", "value": "PUT"},
                                {"label": "DELETE", "value": "DELETE"}
                            ],
                            id='rest_http_method',
                            style={'width': '30%', 'padding-left': '3px', 'padding-right': '5px'}
                        ),
                        dcc.Input(id='rest_http_path', style={'width': '70%'}, placeholder='URL path')
                    ], style={'padding': '3px'}),
                    html.Div(id='rest_editor_message_bar'),
                    dash_ace.DashAceEditor(
                        id='blue_editor',
                        value='{} \n',
                        theme='github',
                        mode='json',
                        tabSize=2,
                        # enableBasicAutocompletion=True,
                        # enableLiveAutocompletion=True,
                        # autocompleter='/autocompleter?prefix=',
                        placeholder='JSON object ...',
                        width='100%',
                        height='500px',
                        style={'margin-top': '5px', 'margin-bottom': '5px'}
                    ),
                    dbc.Button([html.I(className='fas fa-arrow-circle-right'), "  Submit"], id='rest_submit_button',
                               color="primary", style={'margin-top': '5px', 'margin-bottom': '5px'})
                ]),
                width=6,
                style={'height': "700px", 'margin-left': '10px'},
                color='light',
                title="REST Request"
            ),
            getTile(
                [],
                width=6,
                style={'height': "700px"},
                color='light',
                title="REST Response"
            )
        ])

    def get_callbacks(self, app):
        @app.callback(Output('rest_editor_message_bar', 'children'),
                      Input('rest_submit_button', 'n_clicks'),
                      State('blue_editor', 'value'))
        def rest_submit_button(click, value):
            if click is None:
                return

            print("submit button clicked")
            print(value)
            try:
                body = json.loads(value)
                print(body)
                return "Valid JSON"
            except Exception as e:
                return "Not a valid JSON"


