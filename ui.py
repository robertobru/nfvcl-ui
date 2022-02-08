import json

import dash_admin_components as dac
import dash_bootstrap_components as dbc
from dash import html, dcc, callback_context
from dash.dependencies import Output, Input, State, ALL
from dash_extensions.enrich import DashProxy  # , MultiplexerTransform

from apps.data import delete_blue
from pages.add_blue import AddBluePage
from pages.add_vim import AddVimPage
from pages.blue_detail import BlueDetailPage
from pages.blueprint import BluePage
from pages.editor import Editor
from pages.home import homePage
from pages.topology import TopologyPage


def get_menuitem(icon=None, label=None, href=None):
    return html.Li(dcc.Link(
        [html.I(className="fas {} fa-w-16 nav-icon".format(icon)), html.P("{}".format(label))],
        href=href,
        className='nav-link'), className='nav-item')


# =============================================================================
# Dash App and Flask Server
# =============================================================================
external_stylesheets = ['https://cdnjs.cloudflare.com/ajax/libs/font-awesome/5.15.1/css/all.min.css',
                        'https://cdnjs.cloudflare.com/ajax/libs/vis/4.20.1/vis.min.css',
                        dbc.themes.DARKLY]
app = DashProxy(prevent_initial_callbacks=True,
                # transforms=[MultiplexerTransform()],
                external_stylesheets=external_stylesheets,
                )
server = app.server
app.title = 'NFVCL'

# =============================================================================
# Dash Admin Components
# =============================================================================
# right_ui = dac.NavbarDropdown(
#     badge_label="!",
#     badge_color="danger",
#     # src="https://quantee.ai",
#     header_text="2 Items",
#     children=[dac.NavbarDropdownItem(children="message 1", date="today")]
# )

navbar = dac.Navbar(color="white", children=[])  # right_ui

sidebar = dac.Sidebar(
    dac.SidebarMenu([
        # dac.SidebarHeader(children="Cards"),
        get_menuitem(icon='fa-home', label='Overview', href='/'),
        get_menuitem(icon='fa-project-diagram', label='Topology', href='/topology'),
        get_menuitem(icon='fa-box', label='Blueprints', href='/blueprints'),
        get_menuitem(icon='fa-database', label='Helm Repository', href='/helm'),
        get_menuitem(icon='fa-address-card', label='UEs', href='/blueprints'),
    ]),
    title='NFVCL web UI',
    skin="dark",
    color="primary",
    brand_color="secondary",
    url="/#",
    src=app.get_asset_url('5g_induce.png'),  # 160 x 160?
    elevation=3,
    opacity=0.8
)

# Body
body = dac.Body(dbc.Row(id='page-content', style={'height': '100%', 'width': '100%'}))

# page_objs = [TopologyPage(app), ]
topology_page = TopologyPage(app)
home_page = homePage(app)
blue_page = BluePage(app)
addvim_page = AddVimPage(app)
addblue_page = AddBluePage(app)
blue_detail_page = BlueDetailPage(app)
editor = Editor(app)

# Footer
# footer = dac.Footer(
#     html.A("CNIT S2N National Laboratory",
#            href="https://s2n.cnit.it",
#            target="_blank",
#            ),
#     right_text="2022"
# )

url_location = dcc.Location(id='url', refresh=False)
# =============================================================================
# App Layout
# =============================================================================
app.layout = dac.Page([navbar, url_location,  sidebar, body, ])  # , footer
app.validation_layout = html.Div([
    url_location,
    navbar,
    sidebar,
    body,
    # footer,
    topology_page.get(),
    home_page.get(),
    blue_page.get(),
    addvim_page.get(),
    addblue_page.get(),
    blue_detail_page.get(''),
    editor.get()
])


# =============================================================================
# Callbacks
# =============================================================================
@app.callback(
    Output('page-content', 'children'),
    [
        Input('url', 'pathname'),
        Input('url', 'search'),
        Input({'type': 'tabulator', 'name': ALL}, 'cellClick')
    ],
    State('page-content', 'children')
)
def display_page(pathname, search, cell, previous_content):
    print(callback_context.triggered[0]['prop_id'].split('.')[-1])
    ctx = callback_context.triggered[0]['prop_id'].split('.')[-1]
    if ctx == 'cellClick':
        print(cell)
        cell = json.loads(cell[0])
        print("$$$ {}".format(cell['column']['field']))
        if cell['column']['field'] == 'open':
            print(cell['value']['open'].split('?')[0])
            pathname = cell['value']['open'].split('?')[0]
            search = "?{}".format(cell['value']['open'].split('?')[-1])
        if cell['column']['field'] == 'delete':
            print(cell['value']['delete'].split('?')[0])
            pathname = cell['value']['delete'].split('?')[0]
            search = cell['value']['delete'].split('?')[-1]

    print('received path {} and search {}'.format(pathname, search))

    if pathname == '/':
        return home_page.get()
    if pathname == '/topology':
        return topology_page.get()
    elif pathname == '/blueprints':
        return blue_page.get()
    elif pathname == '/addvim':
        return addvim_page.get()
    elif pathname == '/addblue':
        return addblue_page.get()
    elif pathname == '/delblue':
        if search and search[:3] == 'id=':
            # Fixme: add a notification element?
            delete_blue(search[3:])
            return blue_page.get()  # Fixme: add deletion message

    elif pathname == '/showblue':
        print(search[:4])
        print(search[4:])
        if search and search[:4] == '?id=':
            return blue_detail_page.get(search[4:])
        else:
            return '404'
    elif pathname == '/editor':
        return editor.get()
    else:
        return '404'


topology_page.get_callbacks(app)
addvim_page.get_callbacks(app)
addblue_page.get_callbacks(app)
blue_page.get_callbacks(app)
blue_detail_page.get_callbacks(app)
editor.get_callbacks(app)
home_page.get_callbacks(app)

# =============================================================================
# Run app
# =============================================================================
if __name__ == '__main__':
    # app.run_server(debug=False)
    app.run_server(debug=True)
