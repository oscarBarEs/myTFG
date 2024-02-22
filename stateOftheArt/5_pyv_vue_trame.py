from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import vtk as vtkTrame, vuetify2 as vuetify

import pyvista as pv
from pyvista.trame.ui import plotter_ui

# Always set PyVista to plot off screen with Trame
pv.OFF_SCREEN = True
name=None
server = get_server(name,client_type = "vue2")
state, ctrl = server.state, server.controller

mesh = pv.Cone()
pl = pv.Plotter()
actor = pl.add_mesh(mesh,name="cone")

@state.change("resolution")
def on_resolution_change( resolution, **kwargs):
    global mesh

    pl.remove_actor(actor)
    mesh = pv.Cone(resolution=int(resolution))
    actor = pl.add_mesh(mesh,name="cone")
    ctrl.reset_camera()

    print(f">>> ENGINE(a): Slider updating resolution to {resolution}")

with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSlider(                    # Add slider
            v_model=("resolution",4),            # link to state
            min=3, max=60, step=1,          # slider range
            dense=True, hide_details=True,  # presentation setup
        )
    with layout.content:
        # Use PyVista's Trame UI helper method
        #  this will add UI controls
        view = plotter_ui(pl)
        ctrl.reset_camera = view.reset_camera

server.start()