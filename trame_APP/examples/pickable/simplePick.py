"""Basic cone example with cell picking feature. Window scaling issue resolved, missing camera sync."""

from trame.app import get_server

from trame.ui.vuetify import SinglePageLayout
from trame.ui.router import RouterViewLayout
from trame.widgets import vtk, vuetify, trame, html, router

from vtkmodules.vtkFiltersSources import vtkSphereSource, vtkConeSource

from vtkmodules.vtkRenderingCore import (
    vtkActor,
    vtkPolyDataMapper,
    vtkRenderer,
    vtkRenderWindow,
    vtkRenderWindowInteractor,
    vtkCellPicker,
)


# Required for interactor initialization
from vtkmodules.vtkInteractionStyle import vtkInteractorStyleSwitch  # noqa

# Required for rendering initialization, not necessary for
# local rendering, but doesn't hurt to include it
import vtkmodules.vtkRenderingOpenGL2  # noqa


# -----------------------------------------------------------------------------
# Trame setup
# -----------------------------------------------------------------------------

server = get_server()
state, ctrl = server.state, server.controller

# Initial VTK window width and height values
state.vtk_window_width = 300
state.vtk_window_height = 300


# -----------------------------------------------------------------------------
# VTK pipeline
# -----------------------------------------------------------------------------

renderer = vtkRenderer()
renderWindow = vtkRenderWindow()
renderWindow.AddRenderer(renderer)
renderWindow.SetSize(state.vtk_window_width, state.vtk_window_height)

renderWindowInteractor = vtkRenderWindowInteractor()
renderWindowInteractor.SetRenderWindow(renderWindow)
renderWindowInteractor.GetInteractorStyle().SetCurrentStyleToTrackballCamera()

cone_source = vtkConeSource()
mapper = vtkPolyDataMapper()
mapper.SetInputConnection(cone_source.GetOutputPort())
actor = vtkActor()
actor.SetMapper(mapper)

picker = vtkCellPicker()

renderer.AddActor(actor)
renderer.ResetCamera()

# -----------------------------------------------------------------------------
# Functions
# -----------------------------------------------------------------------------


# Life cycle update
ctrl.on_server_ready.add(ctrl.view_update)


def right_button_pressed(event):
    p = event["position"]
    x = p["x"]
    y = p["y"]
    z = p["z"]

    picker.Pick(x, y, z, renderer)
    color = (1, 0, 0) if picker.GetActors().GetNumberOfItems() == 0 else (0, 1, 0)
    create_sphere(picker.GetPickPosition(), color)
    ctrl.view_update()


# -----------------------------------------------------------------------------
# Callbacks
# -----------------------------------------------------------------------------


@state.change("content_size")
def update_content_size(content_size, **kwargs):
    if content_size:
        size = content_size.get("size")

        # Size keys: x, y, top, right, bottom, left
        height = size["bottom"] - size["top"]
        width = size["right"] - size["left"]

        renderWindow.SetSize(width, height)
        root_content()


# -----------------------------------------------------------------------------
# GUI ELEMENTS
# -----------------------------------------------------------------------------


def create_sphere(position, color):
    sphere_source = vtkSphereSource()
    sphere_source.SetCenter(position)
    sphere_source.SetRadius(0.01)

    sphere_mapper = vtkPolyDataMapper()
    sphere_mapper.SetInputConnection(sphere_source.GetOutputPort())

    sphere_actor = vtkActor()
    sphere_actor.SetMapper(sphere_mapper)
    sphere_actor.GetProperty().SetColor(color)

    renderer.AddActor(sphere_actor)


# -----------------------------------------------------------------------------
# GUI
# -----------------------------------------------------------------------------

layout = SinglePageLayout(server)


def root_content():
    with RouterViewLayout(server, "/"):

        if state.content_size:
            size = state.content_size.get("size")
            h = size["bottom"] - size["top"]
            w = size["right"] - size["left"]
        else:
            w = state.vtk_window_width
            h = state.vtk_window_height

        with html.Div() as v_div:

            v_div.style = f"width: {w}px; height: {h}px"

            view = vtk.VtkLocalView(
                view=renderWindow,
                interactor_events=("event_types", ["RightButtonPress"]),
                RightButtonPress=(right_button_pressed, "[utils.vtk.event($event)]"),
            )

            view.update()
            ctrl.view_update.add(view.update)


root_content()


with layout:
    layout.title.set_text("Cell picking example")

    with layout.content:
        # Monitor content window's size
        with trame.SizeObserver("content_size"):
            with vuetify.VContainer(fluid=True, classes="pa-0"):
                router.RouterView()


# -----------------------------------------------------------------------------
# Main
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    server.start()
