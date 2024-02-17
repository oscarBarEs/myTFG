import dash
import dash_vtk
from dash import html, dcc
from dash.dependencies import Input, Output, State
from dash_vtk.utils import to_mesh_state
import numpy as np
import pyvista as pv
from pyvista import examples

np.random.seed(42)

# Get point cloud data from PyVista
mesh = pv.Cone()
type(mesh)
grid = mesh.cast_to_unstructured_grid()
type(grid)
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

# Setup VTK rendering of PointCloud
app = dash.Dash(__name__)
server = app.server

vtk_view = dash_vtk.View(
    [
        dash_vtk.GeometryRepresentation([
            dash_vtk.Mesh(state=mesh_state)]
        )
        
    ]
)

app.layout = html.Div(
    style={"height": "calc(100vh - 16px)"},
    children=[
        html.Div(style={"height": "100%", "width": "100%"}
                 ,children=[
                     html.Div(vtk_view,style={"height": "100%", "width": "100%"}),
                        html.Div(
                            dcc.Slider(
                                min=5,
                                max=100,
                                step=0.1,
                                vertical=True
                            ),
                            style={"position": "absolute", "top": "0", "right": "0", "height": "100%", "width": "50px"}
                        )

        ])],
)

if __name__ == "__main__":
    app.run_server(debug=True)