from dash import Dash, html
from dash_vtk.utils import to_mesh_state,presets
import dash_vtk
import vtk
# Get it here: https://github.com/plotly/dash-vtk/blob/master/demos/data/cow-nonormals.obj
vtk_file = "ventricle_Tagged.vtk"

reader = vtk.vtkUnstructuredGridReader()  # Use vtkUnstructuredGridReader for UNSTRUCTURED_GRID
reader.SetFileName(vtk_file)
reader.Update()
unstructuredGrid = reader.GetOutput()
mesh_state = to_mesh_state(unstructuredGrid)

txt_content = None
with open(vtk_file, 'r') as file:
  txt_content = file.read()

content = dash_vtk.View([
    dash_vtk.GeometryRepresentation([
            dash_vtk.Mesh(state=mesh_state)]),
])

# Dash setup
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "400px"},
    children=[content],
)

if __name__ == "__main__":
    app.run(debug=True)