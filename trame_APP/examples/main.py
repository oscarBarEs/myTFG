"""
Control Scalar Array
~~~~~~~~~~~~~~~~~~~~

Extending our simple example to have a dropdown menu to control which
scalar array is used to color the mesh.
"""

import pyvista as pv
from pyvista import examples
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify2 import SinglePageWithDrawerLayout
from trame.widgets import vuetify,vega

from components.tableOfSimulation import table_of_simulation, selection_change_tos, chart_onset_pacing
from components.page.header import header

pv.OFF_SCREEN = True
server = get_server(client_type="vue2")
global ctrl
state, ctrl = server.state, server.controller

#mesh = examples.download_antarctica_velocity()
mesh = pv.read("Resources/info/ventricle_Tagged.vtk")

pl = pv.Plotter()

# Agrega la flecha a la escena
actor = None
actor = pl.add_mesh(mesh)
#actor = pl.add_mesh(mesh)

# Obtén el centro de la celda 347
cell_center = mesh.cell_centers().points[0]

# Crea una flecha que apunte al centro de la celda
# arrow = pv.Arrow(start=cell_center, direction=(1.0, 0.0, 0.0), tip_length=0.25, tip_radius=0.1, tip_resolution=20, shaft_radius=0.05, shaft_resolution=20)
#arrow_mesh = pl.add_mesh(arrow, color="red")



pl.view_xy()

is_global = False

@state.change("selection")
def selection_change(selection=[],**kwargs):
    ctrl.fig_update(selection_change_tos(selection, **kwargs))
    # ctrl.fig_update(chart_onset_pacing(selection, **kwargs))


@state.change("scalars")
def set_scalars(scalars=mesh.active_scalars_name, **kwargs):
    global actor
    if actor is not None:
        actor.mapper.array_name = scalars
        actor.mapper.scalar_range = mesh.get_data_range(scalars)
        ctrl.view_update()


@state.change("log_scale")
def set_log_scale(log_scale=False, **kwargs):
    global actor
    if actor is not None:
        actor.mapper.lookup_table.log_scale = log_scale
        ctrl.view_update()

@state.change("show_heart")
def show_heart(show_heart=False, **kwargs):
    global actor
    if show_heart:
        actor = pl.add_mesh(mesh)
    else:
        if actor is not None:
            pl.remove_actor(actor)
    ctrl.view_update()

with SinglePageWithDrawerLayout(server) as layout:
    with layout.toolbar:
        header()


    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):     
            view = plotter_ui(pl)
            ctrl.view_update = view.update


            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard():
                    vuetify.VCheckbox(
                        label="Show Heart",
                        v_model=("show_heart", True),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                    )
                    vuetify.VCheckbox(
                        label="Log Scale",
                        v_model=("log_scale", False),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                    )
                    vuetify.VSelect(
                        label="Scalars",
                        v_model=("scalars", mesh.active_scalars_name),
                        items=("array_list", list(mesh.point_data.keys())),
                        hide_details=True,
                        dense=True,
                        outlined=True,
                        classes="pt-1 ml-2",
                        style="max-width: 250px",
                    )
                    with vuetify.VContainer(classes="justify-left ma-6"):
                        vuetify.VDataTable(**table_of_simulation('output.json'))
                        fig = vega.Figure(classes="ma-2", style="width: 100%;")
                        ctrl.fig_update = fig.update
                            
                    vuetify.VCardText(children=["This is a heart mesh"])

server.start()


