from dash import Dash, html,dcc,Input, Output, callback,State
import dash_bootstrap_components as dbc

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


heart=None
content = dash_vtk.View([
    dash_vtk.GeometryRepresentation(id="heartViewer",children=[heart]),
])
# Dash setup
app = Dash(__name__)
server = app.server

app.layout = html.Div(
    style={"width": "100%", "height": "400px"},
    children=[
       dcc.Upload(
        id='heartVTK',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ], style={
        'width': '100%',
        'height': '60px',
        'lineHeight': '60px',
        'borderWidth': '1px',
        'borderStyle': 'dashed',
        'borderRadius': '5px',
        'textAlign': 'center'
      })),
       content],
)

@callback(
    Output("heartViewer", 'children'),
    Input("heartVTK", 'contents'),
    State('heartVTK', 'filename')
)
def update_mesh(heartVTK,fileName):
    if(heartVTK is None):
        return
    print("File name: ",fileName)
    vtk_file = fileName
    reader = vtk.vtkUnstructuredGridReader()  # Use vtkUnstructuredGridReader for UNSTRUCTURED_GRID
    reader.SetFileName(vtk_file)
    reader.Update()
    unstructuredGrid = reader.GetOutput()
    mesh_state = to_mesh_state(unstructuredGrid)
    print("Mesh state: ")
    return dash_vtk.Mesh(state=mesh_state)

if __name__ == "__main__":
    app.run(debug=True)