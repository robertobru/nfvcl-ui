import dash_ace

from apps.utils import *


class Editor(WebPage):
    def __init__(self, app):
        # self.blue_box = Box("Blueprint Instances", blue_table, width=12)
        super().__init__('Editor', self.get_page_layout(), app)

    def get_page_layout(self, value=[]):
        return dbc.Row([
            dbc.Col(
                [
                    dash_ace.DashAceEditor(
                        id='blue_editor',
                        value='def test(a: int) -> str : \n'
                              '    return f"value is {a}"',
                        theme='github',
                        mode='json',
                        tabSize=2,
                        # enableBasicAutocompletion=True,
                        # enableLiveAutocompletion=True,
                        # autocompleter='/autocompleter?prefix=',
                        placeholder='Python code ...'
                    )
                ],
                width={"size": 12}),

        ])

    def get_callbacks(self, app):
        pass
