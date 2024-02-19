import dash
import dash_vtk
from dash import html, dcc
import dash_bootstrap_components as dbc

from dash.dependencies import Input, Output, State
from dash_vtk.utils import to_mesh_state
import numpy as np
import pyvista as pv
from pyvista import examples

np.random.seed(42)

# Get point cloud data from PyVista
mesh = pv.Cone()
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

app.layout = dbc.Container(
    fluid=True,
    style={"height": "100vh"},
    children=[        
        dbc.Row(                
            dbc.Col(
                    children=dcc.Slider(
                        id="scale-factor",
                        min=4,
                        max=25,
                        step=1,
                        value=1,
                        marks={4: "4", 25: "25"},
                    )
                )),
            
                html.Div(
                    html.Div(vtk_view, style={"height": "100%", "width": "100%"}),
                    style={"height": "88%"},
                )
            
        

        ]
)

if __name__ == "__main__":
    app.run_server(debug=True)