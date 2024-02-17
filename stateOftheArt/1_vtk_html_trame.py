from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.ui.html import DivLayout
from trame.widgets import vtk as vtkTrame, vuetify3 as vuetify,html
import vtk
from vtkmodules.vtkFiltersSources import vtkConeSource


# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa


# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtk.vtkRenderer()
renderWindow = vtk.vtkRenderWindow()
renderWindow.AddRenderer(renderer)

renderWindowInteractor = vtk.vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtk.vtkConeSource()
cone_source.SetResolution(5)
mapper = vtk.vtkPolyDataMapper()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor = vtk.vtkActor()
actor.GetProperty().SetRepresentationToWireframe()

actor.SetMapper(mapper)

renderer.AddActor(actor)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Trame
# -----------------------------------------------------------------------------

server = get_server()
server.client_type = "vue3"
ctrl = server.controller
state = server.state


@state.change("resolution")
def on_resolution_change( resolution):
    print(f">>> ENGINE(a): Slider updating resolution to {resolution}")
    cone_source.SetResolution(int(resolution))
    #ctrl.update_vtk()

    print(f">>> ENGINE(a): Slider updating resolution to {resolution}")

with DivLayout(server) as layout:

    with html.Div():
        html.H1("Hello trame")
        html.Input(type="range", min="3", max="20", value="5", step="1")# 
        #Documentatios say that VModel works on gtml.Input 
        # Its a lie
        # Same with vtkTrame.VtkLocalView(renderWindow)
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            with vtkTrame.VtkLocalView(renderWindow) as vtk_view:                # vtk.js view for local rendering
                ctrl.reset_camera = vtk_view.reset_camera  # Bind method to controller
                ctrl.on_server_ready.add(vtk_view.update)
                ctrl.update_vtk = vtk_view.update

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
