from trame.app import get_server
from trame.ui.vuetify3 import SinglePageLayout
from trame.widgets import vtk as vtkTrame, vuetify3 as vuetify
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
def on_resolution_change( resolution, **kwargs):
    cone_source.SetResolution(int(resolution))
    ctrl.update_vtk()

    print(f">>> ENGINE(a): Slider updating resolution to {resolution}")

with SinglePageLayout(server) as layout:
    layout.title.set_text("Hello trame")
    with layout.toolbar:
        vuetify.VSlider(                    # Add slider
            v_model=("resolution", 10),      # bind variable with an initial value of 6
            min=3, max=60, step=1,          # slider range
            dense=True, hide_details=True,  # presentation setup
        )

    with layout.content:
        with vuetify.VContainer(
            fluid=True,
            classes="pa-0 fill-height",
        ):
            # html_view = vtkTrame.VtkLocalView(renderWindow)
            #       # <--- New line

            with vtkTrame.VtkLocalView(renderWindow) as vtk_view:                # vtk.js view for local rendering
                ctrl.reset_camera = vtk_view.reset_camera  # Bind method to controller
                ctrl.on_server_ready.add(vtk_view.update)
                ctrl.update_vtk = vtk_view.update

# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
