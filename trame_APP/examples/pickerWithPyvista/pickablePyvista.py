"""
.. _surface_point_picking_example:

Picking a Point on the Surface of a Mesh
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
This example demonstrates how to pick meshes using
:func:`enable_surface_point_picking() <pyvista.Plotter.enable_surface_point_picking>`.

This allows you to pick points on the surface of a mesh.

"""



import pyvista as pv

from pyvista import Sphere, Plotter
from numpy.random import uniform

def callback(sender, event):
    if event == "RightButtonPressEvent":
        print("Right-clicked on:", sender.GetName())

# Create a sphere and add it to the scene with a name
sphere = pv.Sphere()

# Create a plotting window and add the sphere to the plotter
plotter = pv.Plotter()
plotter.add_mesh(sphere,name="sphere")


plotter.enable_block_picking(callback, side="left")

# Show the plotter window
plotter.show()