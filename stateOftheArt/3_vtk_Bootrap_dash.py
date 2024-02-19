# <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet" integrity="sha384-T3c6CoIi6uLrA9TneNEoa7RxnatzjcDSCmG1MXxSR1GAsXEV/Dwwykc2MPK8M2HN" crossorigin="anonymous">

import dash
import dash_vtk
from dash import html, dcc,Input, Output, callback
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

app = dash.Dash(__name__,external_stylesheets=[dbc.themes.BOOTSTRAP])

server = app.server

vtk_view = dash_vtk.View(
    [
        dash_vtk.GeometryRepresentation([
            dash_vtk.Mesh(id="my-cone",state=mesh_state)]
        )
        
    ]
)

app.layout = dbc.Container(
    fluid=True,
    style={"height": "100vh"},
    children=[        
        dbc.Row(                
            # dbc.Col(
            #         children=dcc.Slider(
            #             id="scale-factor",
            #             min=3,
            #             max=50,
            #             step=1,
            #             value=6,
            #             marks={3: "3", 25: "25"},
            #         )
            #     ),
            dbc.Col(
                    children=dbc.Input(
                        id="scale-factor",
                        type="range",
                        min=3,
                        max=50,
                        step=1,
                        value=6,
                        
                    )
                )                
                )
                
                ,
            
                html.Div(
                    html.Div(vtk_view, style={"height": "100%", "width": "100%"}),
                    style={"height": "88%"},
                )
            
        

        ]
)

@callback(
    Output("my-cone", 'state'),
    Input("scale-factor", 'value')
)
def update_mesh(scale_factor):

    mesh = pv.Cone(resolution=int(scale_factor))
    grid = mesh.cast_to_unstructured_grid()
    mesh_state = to_mesh_state(grid)
    return mesh_state

if __name__ == "__main__":
    app.run_server(debug=True)