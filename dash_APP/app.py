import dash
import dash_vtk
import vtk

from dash_vtk.utils import to_mesh_state,to_volume_state
from dash import dcc,html
from dash.dependencies import Input, Output, State

import numpy as np
import pyvista as pv
from pyvista import examples

np.random.seed(42)
heart_filename = "ventricle_Tagged.vtk"

"""HeartReader = vtk.vtkXMLUnstructuredGridReader()
HeartReader.SetFileName(heart_filename)
HeartReader.Update()"""

# Get point cloud data from PyVista
dataset = examples.download_lidar()
dataset = pv.read(heart_filename)
mesh_state = to_mesh_state(dataset)
# print(mesh_state.point_data.keys())
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

vtk_view = dash_vtk.View([
    dash_vtk.GeometryRepresentation([
        dash_vtk.Mesh(id='mesh', state=mesh_state),  # replace 'ArrayName' with the name of your scalar array
    ]),
])
vtk_view = dash_vtk.View([
    dash_vtk.VolumeRepresentation([
        # GUI to control Volume Rendering
        # + Setup good default at startup
        dash_vtk.VolumeController(),
        # Actual Imagedata
        dash_vtk.ImageData(
            dimensions=[5, 5, 5],
            origin=[-2, -2, -2],
            spacing=[1, 1, 1],
            children=[
                dash_vtk.PointData([
                    dash_vtk.DataArray(
                        registration="setScalars",
                        values=list(range(5*5*5)),
                    )
                ])
            ],
        ),
    ]),
])


app.layout = html.Div(
    style={"height": "calc(100vh - 16px)"},
    children=[html.Div(vtk_view, style={"height": "100%", "width": "100%"})],
)

if __name__ == "__main__":
    app.run_server(debug=True)
