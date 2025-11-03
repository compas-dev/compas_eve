# r: compas_eve>=2.0.0
"""
Create a message.

COMPAS EVE v2.0.0
"""

import System

import Rhino.Geometry as rg
import rhinoscriptsyntax as rs

from compas.geometry import Brep
from compas_eve import Message
from compas_rhino import conversions

component = ghenv.Component  # noqa: F821

local_values = locals()
data = dict()

for input_param in component.Params.Input:
    name = input_param.NickName
    value = local_values[name]
    if isinstance(value, System.Guid):
        try:
            value = rs.coercegeometry(value)
        except:  # noqa: E722
            pass
    if isinstance(value, rg.Point3d):
        value = conversions.point_to_compas(value)
    elif isinstance(value, rg.Box):
        value = conversions.box_to_compas(value)
    elif isinstance(value, rg.Vector3d):
        value = conversions.vector_to_compas(value)
    elif isinstance(value, rg.Arc):
        value = conversions.arc_to_compas(value)
    elif isinstance(value, rg.Circle):
        value = conversions.circle_to_compas(value)
    elif isinstance(value, rg.Curve):
        value = conversions.curve_to_compas(value)
    elif isinstance(value, rg.Cone):
        value = conversions.cone_to_compas(value)
    elif isinstance(value, rg.Cylinder):
        value = conversions.cylinder_to_compas(value)
    elif isinstance(value, rg.Line):
        value = conversions.line_to_compas(value)
    elif isinstance(value, rg.Mesh):
        value = conversions.mesh_to_compas(value)
    elif isinstance(value, rg.Plane):
        value = conversions.plane_to_compas_frame(value)
    elif isinstance(value, rg.Sphere):
        value = conversions.sphere_to_compas(value)
    elif isinstance(value, rg.PolylineCurve):
        value = conversions.polygon_to_compas(value)
    elif isinstance(value, rg.Polyline):
        value = conversions.polyline_to_compas(value)
    elif isinstance(value, rg.Surface):
        value = conversions.surface_to_compas(value)
    elif isinstance(value, rg.Brep):
        value = Brep.from_native(value)

    data[name] = value

message = Message(**data)
