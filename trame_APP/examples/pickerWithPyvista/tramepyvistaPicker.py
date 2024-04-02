import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import vuetify2 as vuetify,vtk as vtkTrame

pv.OFF_SCREEN = False

server = get_server()
state, ctrl = server.state, server.controller

def callback(point):
    """Create a cube and a label at the click point."""
    print(f"Clicked on point {point}")
    mesh = pv.Cube(center=point, x_length=0.05, y_length=0.05, z_length=0.05)
    pl.add_mesh(mesh, style='wireframe', color='r')
    pl.add_point_labels(point, [f"{point[0]:.2f}, {point[1]:.2f}, {point[2]:.2f}"])

pl = pv.Plotter()
pl.enable_point_picking(callback=callback,left_clicking=True ,show_message='Pick a point')
mesh = pv.Cone()
actor = pl.add_mesh(mesh, name="TheCone",pickable=True)
pl.reset_camera()




with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VProgressLinear(
            indeterminate=True, absolute=True, bottom=True, active=("trame__busy",)
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True, classes="pa-0 fill-height", style="position: relative;"
        ):

            with vtkTrame.VtkLocalView(pl.ren_win)as local:
                def view_update(**kwargs):
                    local.update(**kwargs)                
                ctrl.view_update = view_update            


server.start()