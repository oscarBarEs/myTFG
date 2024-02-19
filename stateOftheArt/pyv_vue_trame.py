from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout

import pyvista as pv
from pyvista.trame.ui import plotter_ui

# Always set PyVista to plot off screen with Trame
pv.OFF_SCREEN = True
name=None
server = get_server(name,client_type = "vue2")
state, ctrl = server.state, server.controller

mesh = pv.Sphere()

pl = pv.Plotter()
pl.add_mesh(mesh)

with SinglePageLayout(server) as layout:
    with layout.content:
        # Use PyVista's Trame UI helper method
        #  this will add UI controls
        view = plotter_ui(pl)

server.start()