from trame.app import get_server
from trame.ui.vuetify2 import SinglePageWithDrawerLayout
from trame.widgets import html
from trame.widgets import vuetify2 as vuetify
from trame.widgets import vtk,  plotly
from trame.decorators import TrameApp, change, life_cycle

import pyvista as pv
from pyvista.trame.ui import plotter_ui


# noinspection PyUnresolvedReferences
from vtkmodules.vtkCommonColor import vtkNamedColors
from vtkmodules.vtkCommonDataModel import vtkDataObject

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkDataSetMapper,
    vtkPolyDataMapper,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkRenderer
)
#Parts of the APP
from components.page.header import header
#Table
from components.fromJsonToTable import fetch_data
from components.tableOfSimulation import table_of_simulation

from components.graphs import plotly_graph_vuetify
#Read Mesh
from components.meshReader import readVTKMesh


# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
# -----------------------------------------------------------------------------
# Globals
# -----------------------------------------------------------------------------

DEFAULT_RESOLUTION = 6
pv.OFF_SCREEN = True
pl = pv.Plotter()
# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------
#actor = readMesh() # en meshReader.py

mesh = pv.read("Resources/info/ventricle_Tagged.vtk")
actor = pl.add_mesh(mesh)
pl.view_xy()

# Mesh: Setup default representation to surface
"""    @change("scalars")
    def set_scalars(scalars=mesh.active_scalars_name, **kwargs):
        actor.mapper.array_name = scalars
        actor.mapper.scalar_range = mesh.get_data_range(scalars)
        ctrl.view_update()"""     
# -----------------------------------------------------------------------------
# Main Page
# -----------------------------------------------------------------------------
@TrameApp()
class App_Hearth_Helper:

    def __init__(self, server=None,ctrl=None, table_size=10):
        self.server = get_server(server, client_type="vue2")
        self.ctrl = self.server.controller
        self.state = self.server.state
        self.ui = self._build_ui()

    @life_cycle.server_reload
    @life_cycle.server_ready
    def reload_ui(self, *args, **kwargs):
        self.ui = self._build_ui()
    @change("scalars")
    def set_scalars(scalars=mesh.active_scalars_name, **kwargs):
        actor.mapper.array_name = scalars
        actor.mapper.scalar_range = mesh.get_data_range(scalars)
        ctrl.view_update()


    def _build_ui(self):
        with SinglePageWithDrawerLayout(self.server) as layout:
            layout.title.set_text("Heart Helper")

            with layout.content:
                with vuetify.VContainer(
                    fluid=True,
                    classes="pa-0 fill-height",
                    
                ):
                    with vuetify.VContainer(
                        fluid=True,
                        classes="pa-0 fill-height",
                        height="100%",
                    ):
                        #plotly_graph_vuetify()
                        view = plotter_ui(pl)
                        self.ctrl.view_update = view.update                
                #self.ctrl.on_server_ready.add(view.update)


            with layout.toolbar:
                header()
                    
            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard():
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

        return layout

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    app = App_Hearth_Helper()
    app.server.start()

if __name__ == "__main__":
    # server.start()
    main()
