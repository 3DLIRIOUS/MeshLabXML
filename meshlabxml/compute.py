""" MeshLabXML measurement and computation functions """

#from . import mlx.FilterScript
import meshlabxml as mlx
import re
from . import util

def section(script, axis='z', offset=0.0, surface=False, custom_axis=None,
            planeref=2):
    """ Compute the polyline representing a planar section (a slice) of a mesh.

    If the resulting polyline is closed the result can be filled with a
    triangular mesh representing the section.

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.
        axis (str): The slicing plane is perpendicular to this axis. Accepted
            values are 'x', 'y', or 'z'; any other input will be interpreted
            as a custom axis (although using 'custom' is recommended
            for clarity). Upper or lowercase values are accepted.
        offset (float): Specify an offset of the cross-plane. The offset
            corresponds to the distance along 'axis' from the point specified
            in 'planeref'.
        surface (bool): If True, in addition to a layer with the section
            polyline, also a layer with a triangulated version of the section
            polyline will be created. This only works if the section polyline
            is closed.
        custom_axis (3 component list or tuple): Specify a custom axis as
            a 3 component vector (x, y, z); this is ignored unless 'axis' is
            set  to 'custom'.
        planeref (int): Specify the reference from which the planes are
            shifted. Valid values are:
            0 - Bounding box center
            1 - Bounding box min
            2 - Origin (default)

    Layer stack:
        Creates a new layer '{label}_sect_{axis_name}_{offset}', where
            'axis_name' is one of [X, Y, Z, custom] and 'offest' is
            truncated 'offset'
        If surface is True, create a new layer '{label}_sect_{axis}_{offset}_mesh'
        Current layer is changed to the last (newly created) layer

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    # Convert axis name into number
    if axis.lower() == 'x':
        axis_num = 0
        axis_name = 'X'
    elif axis.lower() == 'y':
        axis_num = 1
        axis_name = 'Y'
    elif axis.lower() == 'z':
        axis_num = 2
        axis_name = 'Z'
    else:  # custom axis
        axis_num = 3
        axis_name = 'custom'
        if custom_axis is None:
            print('WARNING: a custom axis was selected, however',
                  '"custom_axis" was not provided. Using default (Z).')
    if custom_axis is None:
        custom_axis = (0.0, 0.0, 1.0)

    filter_xml = ''.join([
        '  <filter name="Compute Planar Section">\n',
        '    <Param name="planeAxis" ',
        'value="{:d}" '.format(axis_num),
        'description="Plane perpendicular to" ',
        'enum_val0="X Axis" ',
        'enum_val1="Y Axis" ',
        'enum_val2="Z Axis" ',
        'enum_val3="Custom Axis" ',
        'enum_cardinality="4" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="customAxis" ',
        'x="{}" y="{}" z="{}" '.format(custom_axis[0], custom_axis[1],
                                       custom_axis[2]),
        'description="Custom axis" ',
        'type="RichPoint3f" ',
        '/>\n',
        '    <Param name="planeOffset" ',
        'value="{}" '.format(offset),
        'description="Cross plane offset" ',
        'type="RichFloat" ',
        '/>\n',
        '    <Param name="relativeTo" ',
        'value="{:d}" '.format(planeref),
        'description="plane reference" ',
        'enum_val0="Bounding box center" ',
        'enum_val1="Bounding box min" ',
        'enum_val2="Origin" ',
        'enum_cardinality="3" ',
        'type="RichEnum" ',
        '/>\n',
        '    <Param name="createSectionSurface" ',
        'value="{}" '.format(str(surface).lower()),
        'description="Create also section surface" ',
        'type="RichBool" ',
        '/>\n',
        '  </filter>\n'])
    util.write_filter(script, filter_xml)
    if isinstance(script, mlx.FilterScript):
        current_layer_label = script.layer_stack[script.current_layer()]
        script.add_layer('{}_sect_{}_{}'.format(current_layer_label, axis_name,
                                                int(offset)))
        if surface:
            script.add_layer('{}_sect_{}_{}_mesh'.format(current_layer_label,
                                                         axis_name, int(offset)))
    return None


def measure_geometry(script):
    """ Compute a set of geometric measures of a mesh/pointcloud.

    Bounding box extents and diagonal, principal axis, thin shell barycenter
    (mesh only), vertex barycenter and quality-weighted barycenter (pointcloud
    only), surface area (mesh only), volume (closed mesh) and Inertia tensor
    Matrix (closed mesh).

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA

    Bugs:
        Bounding box extents not computed correctly for some volumes
    """
    filter_xml = '  <xmlfilter name="Compute Geometric Measures"/>\n'
    util.write_filter(script, filter_xml)
    if isinstance(script, mlx.FilterScript):
        script.parse_geometry = True
    return None


def measure_topology(script):
    """ Compute a set of topological measures over a mesh

    Args:
        script: the mlx.FilterScript object or script filename to write
            the filter to.

    Layer stack:
        No impacts

    MeshLab versions:
        2016.12
        1.3.4BETA
    """
    filter_xml = '  <xmlfilter name="Compute Topological Measures"/>\n'
    util.write_filter(script, filter_xml)
    if isinstance(script, mlx.FilterScript):
        script.parse_topology = True
    return None


def parse_geometry(ml_log, log=None, ml_version='1.3.4BETA', print_output=False):
    """Parse the ml_log file generated by the measure_geometry function.

    Warnings: Not all keys may exist if mesh is not watertight or manifold

    Args:
        ml_log (str): MeshLab log file to parse
        log (str): filename to log output
    """
    # TODO: v2016.12 adds more bounding box measurements (min, max); use these
    # instead of AABB
    geometry = {}
    with open(ml_log) as fread:
        for line in fread:
            if 'Mesh Bounding Box min' in line: #2016.12
                geometry['aabb_min'] = (line.split()[4:7])
                geometry['aabb_min'] = [util.to_float(val) for val in geometry['aabb_min']]
            if 'Mesh Bounding Box max' in line: #2016.12
                geometry['aabb_max'] = (line.split()[4:7])
                geometry['aabb_max'] = [util.to_float(val) for val in geometry['aabb_max']]
            if 'Mesh Bounding Box Size' in line: #2016.12
                geometry['aabb_size'] = (line.split()[4:7])
                geometry['aabb_size'] = [util.to_float(val) for val in geometry['aabb_size']]
            if 'Mesh Bounding Box Diag' in line: #2016.12
                geometry['aabb_diag'] = util.to_float(line.split()[4])
            if 'Mesh Volume' in line:
                geometry['volume_mm3'] = util.to_float(line.split()[3])
                geometry['volume_cm3'] = geometry['volume_mm3'] * 0.001
            if 'Mesh Surface' in line:
                if ml_version == '1.3.4BETA':
                    geometry['area_mm2'] = util.to_float(line.split()[3])
                else:
                    geometry['area_mm2'] = util.to_float(line.split()[4])
                geometry['area_cm2'] = geometry['area_mm2'] * 0.01
            if 'Mesh Total Len of' in line:
                if 'including faux edges' in line:
                    geometry['total_edge_length_incl_faux'] = util.to_float(
                        line.split()[7])
                else:
                    geometry['total_edge_length'] = util.to_float(
                        line.split()[7])
            if 'Thin shell barycenter' in line:
                geometry['barycenter'] = (line.split()[3:6])
                geometry['barycenter'] = [util.to_float(val) for val in geometry['barycenter']]
            if 'Thin shell (faces) barycenter' in line: #2016.12
                geometry['barycenter'] = (line.split()[4:7])
                geometry['barycenter'] = [util.to_float(val) for val in geometry['barycenter']]
            if 'Vertices barycenter' in line: #2016.12
                geometry['vert_barycenter'] = (line.split()[2:5])
                geometry['vert_barycenter'] = [util.to_float(val) for val in geometry['vert_barycenter']]
            if 'Center of Mass' in line:
                geometry['center_of_mass'] = (line.split()[4:7])
                geometry['center_of_mass'] = [util.to_float(val) for val in geometry['center_of_mass']]
            if 'Inertia Tensor' in line:
                geometry['inertia_tensor'] = []
                for val in range(3):
                    row = (next(fread, val).split()[1:4])
                    row = [util.to_float(b) for b in row]
                    geometry['inertia_tensor'].append(row)
            if 'Principal axes' in line:
                geometry['principal_axes'] = []
                for val in range(3):
                    row = (next(fread, val).split()[1:4])
                    row = [util.to_float(b) for b in row]
                    geometry['principal_axes'].append(row)
            if 'axis momenta' in line:
                geometry['axis_momenta'] = (next(fread).split()[1:4])
                geometry['axis_momenta'] = [util.to_float(val) for val in geometry['axis_momenta']]
                break  # stop after we find the first match
    for key, value in geometry.items():
        if log is not None:
            log_file = open(log, 'a')
            log_file.write('{:27} = {}\n'.format(key, value))
            log_file.close()
        elif print_output:
            print('{:27} = {}'.format(key, value))
    return geometry


def parse_topology(ml_log, log=None, ml_version='1.3.4BETA', print_output=False):
    """Parse the ml_log file generated by the measure_topology function.

    Args:
        ml_log (str): MeshLab log file to parse
        log (str): filename to log output

    Returns:
        dict: dictionary with the following keys:
            vert_num (int): number of vertices
            edge_num (int): number of edges
            face_num (int): number of faces
            unref_vert_num (int): number or unreferenced vertices
            boundry_edge_num (int): number of boundary edges
            part_num (int): number of parts (components) in the mesh.
            manifold (bool): True if mesh is two-manifold, otherwise false.
            non_manifold_edge (int): number of non_manifold edges.
            non_manifold_vert (int): number of non-manifold verices
            genus (int or str): genus of the mesh, either a number or
                'undefined' if the mesh is non-manifold.
            holes (int or str): number of holes in the mesh, either a number
                or 'undefined' if the mesh is non-manifold.

    """
    topology = {'manifold': True, 'non_manifold_E': 0, 'non_manifold_V': 0}
    with open(ml_log) as fread:
        for line in fread:
            if 'V:' in line:
                vert_edge_face = line.replace('V:', ' ').replace('E:', ' ').replace('F:', ' ').split()
                topology['vert_num'] = int(vert_edge_face[0])
                topology['edge_num'] = int(vert_edge_face[1])
                topology['face_num'] = int(vert_edge_face[2])
            if 'Unreferenced Vertices' in line:
                topology['unref_vert_num'] = int(line.split()[2])
            if 'Boundary Edges' in line:
                topology['boundry_edge_num'] = int(line.split()[2])
            if 'Mesh is composed by' in line:
                topology['part_num'] = int(line.split()[4])
            if 'non 2-manifold mesh' in line:
                topology['manifold'] = False
            if 'non two manifold edges' in line:
                topology['non_manifold_edge'] = int(line.split()[2])
            if 'non two manifold vertexes' in line:
                topology['non_manifold_vert'] = int(line.split()[2])
            if 'Genus is' in line:  # undefined or int
                topology['genus'] = line.split()[2]
                if topology['genus'] != 'undefined':
                    topology['genus'] = int(topology['genus'])
            if 'holes' in line:
                topology['hole_num'] = line.split()[2]
                if topology['hole_num'] == 'a':
                    topology['hole_num'] = 'undefined'
                else:
                    topology['hole_num'] = int(topology['hole_num'])
    for key, value in topology.items():
        if log is not None:
            log_file = open(log, 'a')
            log_file.write('{:16} = {}\n'.format(key, value))
            log_file.close()
        elif print_output:
            print('{:16} = {}'.format(key, value))

    return topology


def parse_hausdorff(ml_log, log=None, print_output=False):
    """Parse the ml_log file generated by the hausdorff_distance function.

    Args:
        ml_log (str): MeshLab log file to parse
        log (str): filename to log output

    Returns:
        dict: dictionary with the following keys:
            number_points (int): number of points in mesh
            min_distance (float): minimum hausdorff distance
            max_distance (float): maximum hausdorff distance
            mean_distance (float): mean hausdorff distance
            rms_distance (float): root mean square distance

    """
    hausdorff_distance = {"min_distance": 0.0,
                          "max_distance": 0.0,
                          "mean_distance": 0.0,
                          "rms_distance": 0.0,
                          "number_points": 0}
    with open(ml_log) as fread:
        result = fread.readlines()
        data = ""

        for idx, line in enumerate(result):
            m = re.match(r"\s*Sampled (\d+) pts.*", line)
            if m is not None:
                hausdorff_distance["number_points"] = int(m.group(1))
            if 'Hausdorff Distance computed' in line:
                data = result[idx + 2]

        m = re.match(r"\D+(\d+\.*\d*)\D+(\d+\.*\d*)\D+(\d+\.*\d*)\D+(\d+\.*\d*)", data)
        hausdorff_distance["min_distance"] = float(m.group(1))
        hausdorff_distance["max_distance"] = float(m.group(2))
        hausdorff_distance["mean_distance"] = float(m.group(3))
        hausdorff_distance["rms_distance"] = float(m.group(4))
        for key, value in hausdorff_distance.items():
            if log is not None:
                log_file = open(log, 'a')
                log_file.write('{:16} = {}\n'.format(key, value))
                log_file.close()
            elif print_output:
                print('{:16} = {}'.format(key, value))
        return hausdorff_distance
