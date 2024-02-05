import vtk
from vtkmodules.vtkCommonDataModel import vtkDataObject

import numpy as np
import math

def readVTKMesh():
    reader = vtk.vtkUnstructuredGridReader()  # Use vtkUnstructuredGridReader for UNSTRUCTURED_GRID
    reader.SetFileName("Resources/info/ventricle_Tagged.vtk")
    reader.Update()

    # Extract Array/Field information
    dataset_arrays = []
    fields = [
        (reader.GetOutput().GetPointData(), vtkDataObject.FIELD_ASSOCIATION_POINTS),
        (reader.GetOutput().GetCellData(), vtkDataObject.FIELD_ASSOCIATION_CELLS),
    ]
    for field in fields:
        field_arrays, association = field
        for i in range(field_arrays.GetNumberOfArrays()):
            array = field_arrays.GetArray(i)
            array_range = array.GetRange()
            dataset_arrays.append(
                {
                    "text": array.GetName(),
                    "value": i,
                    "range": list(array_range),
                    "type": association,
                }
            )
    default_array = dataset_arrays[0]
    default_min, default_max = default_array.get("range")
    # Get the output of the reader
    unstructuredGrid = reader.GetOutput()
    unstructuredGridPort = reader.GetOutputPort()

    # Get point data and store all array names in a list
    pointData = unstructuredGrid.GetPointData()
    arrayNames = [pointData.GetArrayName(i) for i in range(pointData.GetNumberOfArrays())]

    # Create a mapper and set the input to the unstructured grid
    mapper = vtk.vtkDataSetMapper()
    #mapper.SetInputData(unstructuredGrid)
    mapper.SetInputConnection(unstructuredGridPort)
    # Create an actor and set its mapper
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return unstructuredGridPort,actor, arrayNames,dataset_arrays

def color_by_array(actor, array):
    _min, _max = array.get("range")
    mapper = actor.GetMapper()
    mapper.SelectColorArray(array.get("text"))
    mapper.GetLookupTable().SetRange(_min, _max)
    if array.get("type") == vtkDataObject.FIELD_ASSOCIATION_POINTS:
        mesh_mapper.SetScalarModeToUsePointFieldData()
    else:
        mesh_mapper.SetScalarModeToUseCellFieldData()
    mapper.SetScalarVisibility(True)
    mapper.SetUseLookupTableScalarRange(True)



"""def readMesh():
    # Read the mesh from the file
    reader = vtk.vtkSTLReader()
    reader.SetFileName("Resources/Endo.stl")
    reader.Update()

    # Get the output of the reader
    polyData = reader.GetOutput()
    # Calculate the center of the mesh
    center = polyData.GetCenter()
    print("center")
    print(center)
    # Create a scalar array
    scalars = vtk.vtkFloatArray()
    maximunDistance = 0.0
    coorX=0
    coorZ=1
    for i in range(polyData.GetNumberOfCells()):
        cell = polyData.GetCell(i)          
        # Calculate the centroid of the cell
        point_ids = cell.GetPointIds()
        centroid = np.mean([polyData.GetPoint(point_ids.GetId(j)) for j in range(point_ids.GetNumberOfIds())], axis=0)
        
        # Exclude the Y coordinate
        centroid_xz = np.array([centroid[coorX], centroid[1]])
        center_xz = np.array([center[coorX], center[1]])
        
        # Calculate the distance from the centroid to the center  
        distance = np.linalg.norm(centroid_xz - center_xz)
        if(distance>maximunDistance):
            maximunDistance = distance

    # Calculate a scalar value for each cell or point
    for i in range(polyData.GetNumberOfCells()):
        cell = polyData.GetCell(i)          
        # Calculate the centroid of the cell
        point_ids = cell.GetPointIds()
        centroid = np.mean([polyData.GetPoint(point_ids.GetId(j)) for j in range(point_ids.GetNumberOfIds())], axis=0)    
        # Calculate the distance from the centroid to the center  
        distance = np.linalg.norm(centroid - center)
        # Exclude the Y coordinate
        centroid_xz = np.array([centroid[coorX], centroid[coorZ]])
        center_xz = np.array([center[coorX], center[coorZ]])   
        # Calculate the distance from the centroid to the center  
        distance = np.linalg.norm(centroid_xz - center_xz)   
        # Normalize the distance to a range between 0 and 17
        if(distance<=maximunDistance and distance>maximunDistance*3/4):
            division = 0
        if(distance<maximunDistance*3/4 and distance>maximunDistance*2/4):
            division = 0.25
        if(distance<maximunDistance*2/4 and distance>maximunDistance*1/4):
            division = 0.5
        if(distance<maximunDistance*1/4):
            division = 0.75

        angulo = math.atan2(centroid_xz[1]-center_xz[1], centroid_xz[0]-center_xz[0])
        # Asegurarse de que el ángulo esté en el rango [0, 2*pi)
        angulo = (angulo + 2 * math.pi) % (2 * math.pi)

        scalar=division+(angulo/(2*math.pi)/4)
        #scalar = ((distance / maximunDistance) )
        
        scalars.InsertNextValue(scalar)

    # Add the scalar array to the cell data of the polyData
    polyData.GetCellData().SetScalars(scalars)

    # Create a lookup table
    lookupTable = vtk.vtkLookupTable()
    lookupTable.SetRange(0.0, 17.0)  # scalar range
    # for i in range(17):
    #     lookupTable.SetTableValue(i, 1*i/17, 0, (17/(i+1)) ) # red color for the minimum scalar value

    lookupTable.SetTableValue(0, 1, 0, 0)  # 1

    lookupTable.SetTableValue(1, 1, 0.33, 0)  # 2
    lookupTable.SetTableValue(2, 1, 0.66, 0)  # 3
    lookupTable.SetTableValue(3, 1, 1, 0)  # 5

    lookupTable.SetTableValue(4, 0.66, 1, 0)  # 6
    lookupTable.SetTableValue(5, 0.33, 1, 0)  # 7
    lookupTable.SetTableValue(6, 0, 1, 0)  # 9

    lookupTable.SetTableValue(7, 0, 1, 0.33)  # 10
    lookupTable.SetTableValue(8, 0, 1, 0.66)  # 11
    lookupTable.SetTableValue(9, 0, 1, 1)  # 13

    lookupTable.SetTableValue(10, 0, 0.66, 1)  # 14
    lookupTable.SetTableValue(11, 0, 0.33, 1)  # 15
    lookupTable.SetTableValue(12, 0, 0, 1)  # 17

    lookupTable.SetTableValue(13, 0.33, 0, 1)  # 14
    lookupTable.SetTableValue(14, 0.66, 0.33, 1)  # 15
    lookupTable.SetTableValue(15, 1, 0, 1)  # 17

    lookupTable.SetTableValue(16, 1, 0, 0.66)  # 17

    lookupTable.Build()

    # Create a mapper and set its input to the polyData
    mapper = vtk.vtkPolyDataMapper()
    mapper.SetInputData(polyData)
    mapper.SetLookupTable(lookupTable)

    # Create an actor and set its mapper
    actor = vtk.vtkActor()
    actor.SetMapper(mapper)

    return actor"""