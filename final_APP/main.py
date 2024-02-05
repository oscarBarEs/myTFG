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
from trame.widgets import vuetify

from components.tableOfSimulation import table_of_simulation
from components.page.header import header

pv.OFF_SCREEN = True

server = get_server()
state, ctrl = server.state, server.controller

#mesh = examples.download_antarctica_velocity()
mesh = pv.read("Resources/info/ventricle_Tagged.vtk")

pl = pv.Plotter()
actor = pl.add_mesh(mesh)
pl.view_xy()


@state.change("scalars")
def set_scalars(scalars=mesh.active_scalars_name, **kwargs):
    actor.mapper.array_name = scalars
    actor.mapper.scalar_range = mesh.get_data_range(scalars)
    ctrl.view_update()


@state.change("log_scale")
def set_log_scale(log_scale=False, **kwargs):
    actor.mapper.lookup_table.log_scale = log_scale
    ctrl.view_update()


with SinglePageWithDrawerLayout(server) as layout:
    with layout.toolbar:
        header()


    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # Use PyVista UI template for Plotters
            view = plotter_ui(pl)
            ctrl.view_update = view.update
            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard():
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
                    vuetify.VDataTable(**table_of_simulation('output.json'))
                    vuetify.VCardText(children=["This is a heart mesh"])

server.start()


