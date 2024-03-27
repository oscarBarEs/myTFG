import pyvista as pv
from pyvista.trame.ui import plotter_ui
from trame.app import get_server
from trame.ui.vuetify2 import SinglePageLayout
from trame.widgets import vuetify2 as vuetify,vtk as vtkTrame

pv.OFF_SCREEN = True

server = get_server()
state, ctrl = server.state, server.controller

pl = pv.Plotter()
mesh = pv.read("ventricle_Tagged.vtk")
actor = pl.add_mesh(mesh, name="ventricle_Tagged.vtk")
pl.reset_camera()


@state.change("scalars")
def set_scalars(scalars, **kwargs):
    actor.mapper.array_name = scalars
    actor.mapper.scalar_range = mesh.get_data_range(scalars)
    ctrl.view_update()

with SinglePageLayout(server) as layout:
    with layout.toolbar:
        vuetify.VSpacer()
        vuetify.VSelect(
            label="Mapper",
            v_model=("scalars", mesh.active_scalars_name),
            items=("array_mappes", list(mesh.point_data.keys())),
            hide_details=True,
            dense=True,
            outlined=True,
            classes="pt-1 ml-2",
            style="max-width: 250px",
        )
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