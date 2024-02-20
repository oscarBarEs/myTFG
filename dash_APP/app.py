import dash
import dash_vtk
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_vtk.utils import to_mesh_state,presets
import numpy as np
import pyvista as pv
from pyvista import examples
from vtk.util.numpy_support import vtk_to_numpy

try:
    # VTK 9+
    from vtkmodules.vtkImagingCore import vtkRTAnalyticSource
except ImportError:
    # VTK =< 8
    from vtk.vtkImagingCore import vtkRTAnalyticSource

np.random.seed(42)

# Get point cloud data from PyVista
mesh = pv.Cone(height=20.0,radius=30.0,resolution=100)
grid = mesh.cast_to_unstructured_grid()
dataset = grid
mesh_state = to_mesh_state(dataset)
#dataset = examples.download_lidar()
subset = 0.2
selection = np.random.randint(
    low=0, high=dataset.n_points - 1, size=int(dataset.n_points * subset)
)
points = dataset.points[selection]
xyz = points.ravel()
elevation = points[:, -1].ravel()
min_elevation = np.amin(elevation)
max_elevation = np.amax(elevation)
print(f"Number of points: {points.shape}")
print(f"Elevation range: [{min_elevation}, {max_elevation}]")


# Use VTK to get some data
data_source = vtkRTAnalyticSource()
data_source.Update()  # <= Execute source to produce an output
dataset_cube = data_source.GetOutput()
# Use helper to get a mesh structure that can be passed as-is to a Mesh
# RTData is the name of the field
mesh_state_cube = to_mesh_state(dataset_cube)

# Setup VTK rendering of PointCloud
app = dash.Dash(__name__)
server = app.server

vtk_view = dash_vtk.View(
    children=
    [
               
        dash_vtk.GeometryRepresentation([
            dash_vtk.Mesh(state=mesh_state_cube)]
        )
        ,dash_vtk.GeometryRepresentation([
            dash_vtk.Mesh(state=mesh_state)]
        )
        
    ]
)

app.layout = html.Div(
    style={"height": "calc(100vh - 16px)"},
    children=[html.Div(vtk_view, style={"height": "100%", "width": "100%"})],
)

if __name__ == "__main__":
    app.run_server(debug=True)