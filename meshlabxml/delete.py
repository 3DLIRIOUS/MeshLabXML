""" MeshLabXML deletion functions"""

# Sub-modules
from . import select


def nonmanifold_vert(script='TEMP3D_default.mlx',
                     current_layer=None, last_layer=None):
    select.nonmanifold_vert(script)
    selected(script, face=False)
    # unreferenced_V(s)
    return current_layer, last_layer


def nonmanifold_edge(script='TEMP3D_default.mlx',
                     current_layer=None, last_layer=None):
    select.nonmanifold_edge(script)
    selected(script, face=False)
    # unreferenced_V(s)
    return current_layer, last_layer


def small_parts(script='TEMP3D_default.mlx', ratio=0.2,
                non_closed_only=False,
                current_layer=None, last_layer=None):
    select.small_parts(script, ratio, non_closed_only)
    selected(script)
    return current_layer, last_layer


def selected(script='TEMP3D_default.mlx', face=True,
             vert=True, current_layer=None, last_layer=None):
    """ Delete selected vertices and/or faces"""
    script_file = open(script, 'a')
    if face and vert:
        script_file.write(
            '  <filter name="Delete Selected Faces and Vertices"/>\n')
    elif face and not vert:
        script_file.write('  <filter name="Delete Selected Faces"/>\n')
    elif not face and vert:
        script_file.write('  <filter name="Delete Selected Vertices"/>\n')
    script_file.close()
    return current_layer, last_layer


def faces_from_nonmanifold_edges(
        script='TEMP3D_default.mlx', current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write(
        '  <filter name="Remove Faces from Non Manifold Edges"/>\n')
    script_file.close()
    unreferenced_vert(script)
    return current_layer, last_layer


def unreferenced_vert(script='TEMP3D_default.mlx',
                      current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Remove Unreferenced Vertex"/>\n')
    script_file.close()
    return current_layer, last_layer


def duplicate_faces(script='TEMP3D_default.mlx',
                    current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Remove Duplicate Faces"/>\n')
    script_file.close()
    return current_layer, last_layer


def duplicate_verts(script='TEMP3D_default.mlx',
                    current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Remove Duplicated Vertex"/>\n')
    script_file.close()
    return current_layer, last_layer


def zero_area_face(script='TEMP3D_default.mlx',
                   current_layer=None, last_layer=None):
    script_file = open(script, 'a')
    script_file.write('  <filter name="Remove Zero Area Faces"/>\n')
    script_file.close()
    return current_layer, last_layer
