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
global mapper_heart 
global actor 
global ren
mapper_heart = vtkDataSetMapper()
actor = vtkActor()
ren = vtkRenderer()

"""def change_Data_Array_Representation(i):
    default_array = dataset_arrays[i]
    # Mesh: Color by default array
    mapper_heart.SelectColorArray(default_array.get("text"))
    print(default_array.get("text"))
    mapper_heart.GetLookupTable().SetRange(default_min, default_max)
    if default_array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mapper_heart.SetScalarModeToUsePointFieldData()
    else:
        mapper_heart.SetScalarModeToUseCellFieldData()"""
"""
unstructuredGridPort,ventricle_Tagged, arrayNames,dataset_arrays = readVTKMesh() # en meshReader.py
default_array = dataset_arrays[10]
default_min, default_max = default_array.get("range")

mapper_heart.SetInputConnection(unstructuredGridPort)

actor.SetMapper(mapper_heart)

# Create a rendering window and renderer

renWin = vtkRenderWindow()
renWin.AddRenderer(ren)
renWin.SetWindowName('ReadSTL')

# Assign actor to the renderer
ren.AddActor(actor)"""
pyvista_actor = pv.read("Resources/info/ventricle_Tagged.vtk")
pl.add_mesh(pyvista_actor)
# Mesh: Setup default representation to surface
"""actor.GetProperty().SetRepresentationToSurface()
actor.GetProperty().SetPointSize(1)
actor.GetProperty().EdgeVisibilityOff()
# Mesh: Apply rainbow color map
mesh_lut = mapper_heart.GetLookupTable()
mesh_lut.SetHueRange(0.666, 0.0)
mesh_lut.SetSaturationRange(1.0, 1.0)
mesh_lut.SetValueRange(1.0, 1.0)
mesh_lut.Build()

change_Data_Array_Representation(10)

mapper_heart.SetScalarVisibility(True)
mapper_heart.SetUseLookupTableScalarRange(True)

colors = vtkNamedColors()
ren.SetBackground(colors.GetColor3d('DarkOliveGreen'))

renWin.Render()"""

# -----------------------------------------------------------------------------
# functions
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# Trame
# -----------------------------------------------------------------------------

      
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
                        plotly_graph_vuetify()
                        #view = vtk.VtkLocalView(renWin)
                        view = plotter_ui(pl)
                #self.ctrl.view_update = view.update                
                #self.ctrl.on_server_ready.add(view.update)


            with layout.toolbar:
                header()
                    
            with layout.drawer as drawer:
                drawer.width = "40%"
                vuetify.VDivider(classes="mb-2")
                with vuetify.VCard():
                    vuetify.VSelect(multiple=False,items=("representations",list(pyvista_actor.point_data.keys())),
                    value=dataset_arrays[2].get("text") )
                    vuetify.VDataTable(**table_of_simulation('output.json'))
                    vuetify.VCardText(children=["This is a heart mesh"])

        return layout

"""    def update_mesh_representation(value):
        change_Data_Array_Representation(value)
        self.ctrl.view_update()"""
# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------
def main():
    app = App_Hearth_Helper()
    app.server.start()

if __name__ == "__main__":
    # server.start()
    main()
