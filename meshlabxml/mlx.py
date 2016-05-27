#!/usr/bin/python3
"""Create and run MeshLab XML scripts"""
# meshlabxml.py
# MeshLabXML

import os
import sys
import inspect
import subprocess
#import re
import xml.etree.ElementTree as ET
from glob import glob
import math

ML_VERSION = '1.3.4Beta'

"""
Notes on meshlabserver filters - tested with 1.34Beta:
    Filter parameters may be specified in any order. Arguments within parameters
    may also be specified in any order.
    Required arguments (if applicable):
        value
        name
        type
        enum_cardinality
        min
        max
    Optional arguments (if applicable):
        enum_val#
        description
        tooltip
    Note that while min & max are required, if value is outside of min or max
    the filter will still work (tested with translate, may not work for all)
"""

"""
Abbreviations used in names:
    F = face, faces, facet, facets
    E = edge, edges
    V = vertex, vertexes, vertices
    sel = select, selected
    del = delete, deleted
    L = layer, layers
    N = normal, normals

    under consideration:
    Q = quality
"""

"""
TODO
Keep track of current layer & last layer in every filter
"""

def run(runlogname=None, cmd=None, log=None, p=None, w=None,
         v=False, i=None, o=None, om=None,
         s='MLTEMP_default.mlx'):
    # Can you load multiple project files? Yes!
    # Can you output mulitple project files? Yes, but why? They will be identical
    # order of -i and -p? doesn't matter. Layers will be loaded in the
    # order specified
    # Note: if you provide om it MUST include the flag, e.g. -m or -om.
    # This is to allow for empty entries (e.g. for xyz, etc.)
    # Providing cmd directly overrules all other options except for runlogname
    """
    Usage:
      runlogname: append meshlabserver's stdout and stderr to a log file. This is NOT
           the same as the log file meshlabserver can write directly!
      cmd: your can provide a full commandline, such as 'meshlabserver -i file.stl ...'
           This will overwrite all other options except for 'runlogname'.
      log: log file output by meshlabsever. Specify a single filename as a str
      p: input project file. Can be a single filename str or a list of filenames
      w: output project file. Specify a single filename as a str. All layers
               in the project will be saved as ply files.
      v: overwrite exisitng mesh files (True) or create new ones (False).
                    If a new project file is created meshes will have '_out' added
                    to their name.
      i: input mesh file.  Can be a single filename str or a list of filenames. Order
              is important and determines the order of the layers in the project.
      o: output mesh file. Outputs the current layer at the end of script processing.
              Can be a single filename str or a list of filenames, useful for outputting
              in multiple formats
      om: output mask options for the output file. Can be a single
               filename str or a list of filenames, but should probably be the
               same length as o. If a valid index cannot be found for a
               corresponding o index then the default values in output_mask
               are used. Values MUST include the flag, i.e. -m or -om.
      s: mlx script file to execute
      
      Note that all input files are read after all project files, although meshlabserver
      allows them to be specified in any order. If you want a different order you should
      specify a custom cmd
    """
    """
    if sys.platform == 'win32':
        meshlabserver = 'meshlabserver.exe'
    else:
        meshlabserver = 'meshlabserver'
    """
    if cmd is None:
        cmd = 'meshlabserver '
        if log is not None:
            cmd += ' -l %s' % log
        if p is not None:
            # make a list if it isn't already
            if not isinstance(p, list):
                p = [p]
            for val in p:
                cmd += ' -p %s' % val
        if w is not None:
            cmd += ' -w %s' % w
            if v:
                cmd += ' -v'
        if (p is None) and (i is None):
            i = ['MLTEMP.xyz'] 
        if i is not None:
            # make a list if it isn't already
            if not isinstance(i, list):
                i = [i]
            for val in i:
                cmd += ' -i %s' % val
        if o is not None:
            # make a list if it isn't already
            if not isinstance(o, list):
                o = [o]
            if om is not None:
                if not isinstance(om, list):
                    om = [om]
            else:
                om = []
            for a, val in enumerate(o):
                cmd += ' -o %s' % val
                try:
                    cmd += ' %s' % om[a]
                except IndexError: #If om can't be found use defaults
                    cmd += output_mask(val)
        if s is not None:
            cmd += ' -s %s' % s
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('meshlabserver cmd = %s\n' % cmd)
        RUNLOG.write('***START OF MESHLAB STDOUT & STDERR***\n')
        RUNLOG.close()
        RUNLOG = open(runlogname, 'a')
    else:
        RUNLOG = None
        print('meshlabserver cmd = %s' % cmd)
        print('***START OF MESHLAB STDOUT & STDERR***')
    #subprocess.Popen( meshlabserver,
    #return_code = subprocess.call( [meshlabserver, '-i' + i])
    while True:
        return_code = subprocess.call( cmd, shell=True, stdout=RUNLOG,
                                   stderr=RUNLOG, universal_newlines=True)
        RUNLOG.close()

        if return_code == 0:
            break
        else:
            print('Houston, we have a problem.')
            print('MeshLab did not finish sucessfully. Review the runlog file and the input file(s) to see what went wrong.')
            print('MeshLab command: "%s"' % cmd)
            print('runlog: "%s"' % runlogname)
            print('Where do we go from here?')
            print(' r  - retry running meshlabserver (probably after you\'ve fixed any problems with the input files)')
            print(' c  - continue on with the script (probably after you\'ve manually re-run and generated the deisred output file(s)')
            print(' x  - exit, keeping the MLTEMP file and runlog')
            print(' xd - exit, deleting the MLTEMP files and runlog')
            while True:
                choice = input('Select r, c, x, or xd: ')
                if choice not in ('r', 'c', 'x', 'xd'):
                    print('Please enter a valid option.')
                else:
                    break
            if choice == 'x':
                print('Exiting ...')
                sys.exit(1)
            elif choice == 'xd':
                print('Deleting MLTEMP* and runlog files and exiting ...')
                delete_all('MLTEMP*')
                if runlogname is not None:
                    os.remove(runlogname)
                sys.exit(1)
            elif choice == 'c':
                print('Continuing on ...')
                break
            elif choice == 'r':
                print('Retrying meshlabserver cmd ...')
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***END OF MESHLAB STDOUT & STDERR***\n')
        RUNLOG.write('meshlabserver return code = %s\n\n' % return_code)
        RUNLOG.close()
    return o, return_code

def find_textureFiles(fbasename, runlogname=None):
    """Finds the filenames of the associated texture file(s) (and material
    file for obj) for the mesh."""
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    materialFile = None
    textureFiles = []
    if fext == 'obj':
        # Material Format: mtllib ./model_mesh.obj.mtl
        with open(fbasename, 'r') as f:
            for line in f:
                if 'mtllib' in line:
                    materialFile = os.path.basename(line.split()[1])
                    break
        if materialFile is not None:
            # Texture Format: map_Kd model_texture.jpg
            with open(materialFile, 'r') as f:
                for line in f:
                    if 'map_Kd' in line:
                        textureFiles.append(os.path.basename(line.split()[1]))
    elif fext == 'ply':
        # Texture Format: comment TextureFile model_texture.jpg
        # This works for MeshLab & itSeez3D, but may not work for every ply file. Can't get textured models to work in blender yet.
        # read ascii header; works for both ascii & binary files
        with open(fbasename, 'rb') as f:
            while True:
                line = f.readline().strip().decode('ascii')
                #print(line)
                if 'TextureFile' in line:
                    textureFiles.append(os.path.basename(line.split()[2]))
                if 'end_header' in line:
                    break
    elif fext == 'dae': # COLLADA
    #elif fext == 'mlp':
        # Texture Format:   <image id="texture0" name="texture0">
        #               <init_from>model_texture.jpg</init_from>
        #           </image>
        ns = 'http://www.collada.org/2005/11/COLLADASchema'
        tree = ET.parse(fbasename)
        #root = tree.getroot()
        #print('root = ', root)
        #print('root.tag = ', root.tag, 'root.attrib = ', root.attrib)
        for elem in tree.findall('{%s}library_images/{%s}image/{%s}init_from' % (ns,ns,ns)):
            textureFiles.append(elem.text)
    elif fext == 'x3d':
        # Texture Format: <ImageTexture url="model_texture.jpg"/>
        #ns = 'http://www.w3.org/2001/XMLSchema-instance'
        tree = ET.parse(fbasename)
        #root = tree.getroot()
        #print('root = ', root)
        #print('root.tag = ', root.tag, 'root.attrib = ', root.attrib)
        #for elem in root:
        #for elem in tree.iter(): # iterate through tree; very useful to see possible tags
            #print('elem.tag = ', elem.tag)
            #print('elem.attrib = ', elem.attrib)
        for elem in tree.iter(tag='ImageTexture'):
            #print('elem.attrib = ', elem.attrib)
            textureFiles.append(elem.attrib['url'])
    elif fext == 'wrl':
        # Texture Format: texture ImageTexture { url "model_texture.jpg" }
        with open(fbasename, 'r') as f:
            for line in f:
                if 'ImageTexture' in line:
                    textureFiles.append(os.path.basename(line.split('"')[1]))
                    break
    elif fext != 'stl': # add other format that don't support teture, e.g. xyz?
        print('File extension %s is not currently supported' %fext)
    textureFilesUnique=list(set(textureFiles))
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('Results of find_textureFiles:\n')
        RUNLOG.write('fbasename = %s\n' % fbasename)
        RUNLOG.write('textureFiles = %s\n' % textureFiles)
        RUNLOG.write('textureFilesUnique = %s\n' % textureFilesUnique)
        RUNLOG.write('Number of texture files = %s\n' % len(textureFiles))
        RUNLOG.write('Number of unique texture files = %s\n\n' % len(textureFilesUnique))
        RUNLOG.close()
    return textureFiles, textureFilesUnique, materialFile

def output_mask(o, texture=True):
    """
    Set default output mask options based on file extension
    Note: v1.34BETA changed -om switch to -m
    Possible options (not all options are available for every format):
     vc -> vertex colors
     vf -> vertex flags
     vq -> vertex quality
     vn -> vertex normals
     vt -> vertex texture coords
     fc -> face colors
     ff -> face flags
     fq -> face quality
     fn -> face normals
     wc -> wedge colors
     wn -> wedge normals
     wt -> wedge texture coords
    """
    if ML_VERSION < '1.3.4':
        om_flag=' -om '
    else:
        om_flag=' -m '

    fext = os.path.splitext(o)[1][1:].strip().lower()

    if fext == 'obj':
        if texture:
            om = om_flag + 'vc vn fc wt'
        else:
            om = om_flag + 'vn'
    elif fext == 'ply':
        if texture:
            om = om_flag + 'vc vn wt'
        else:
            om = om_flag + 'vc vn' # with vertex colors
    elif fext == 'stl':
        om = ''
    elif fext == 'dxf':
        om = ''
    elif fext == 'xyz':
        om = ''
    elif fext == 'x3d':
        if texture:
            om = om_flag + 'vc vn wt'
        else:
            om = om_flag + 'vn'
    elif fext == 'dae': # COLLADA
        if texture:
            om = om_flag + 'vc vn wt'
        else:
            om = om_flag + 'vn'
    else:
        print('Default output mask for file extension "%s" is not currently supported' % fext)
    return om

def begin(s='MLTEMP_default.mlx', i=None, p=None):
    sf = open(s,'w')
    sf.write('<!DOCTYPE FilterScript>\n' +
              '<FilterScript>\n')
    sf.close()
    
    LCur = -1
    LLast = -1
    stl = False

    # Process project files first
    if p is not None:
        # make a list if it isn't already
        if not isinstance(p, list):
            p = [ p ]
        for val in p:
            tree = ET.parse(val)
            #root = tree.getroot()
            for elem in tree.iter(tag='MLMesh'):
                f = (elem.attrib['filename'])
                LCur += 1
                LLast += 1
                # If the mesh file extension is stl, change to that layer and
                # run merge_V
                if os.path.splitext(f)[1][1:].strip().lower() == 'stl':
                    change_L(s,LCur)
                    merge_V(s)
                    stl = True

    # Process separate input files next
    if i is not None:
        # make a list if it isn't already
        if not isinstance(i, list):
            i = [ i ]
        for val in i:
            LCur += 1
            LLast += 1
            # If the mesh file extension is stl, change to that layer and
            # run merge_V
            if os.path.splitext(val)[1][1:].strip().lower() == 'stl':
                change_L(s,LCur)
                merge_V(s)
                stl = True

    # If some input files were stl, we need to change back to the last layer
    if stl:
        change_L(s, LLast) # Change back to the last layer
    elif LLast == -1: # If no input files are provided, create a dummy file
        # with a single vertex and delete it first in the script
        i = [ 'MLTEMP.xyz' ]
        MLTEMP_f = open(i[0], 'w')
        MLTEMP_f.write ('0 0 0')
        MLTEMP_f.close ()
        del_L(s)
    return LCur, LLast

def end(s='MLTEMP_default.mlx'):
    sf = open(s,'a')
    sf.write('</FilterScript>')
    sf.close()

### Start measure

def measure_geometry(s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <xmlfilter name="Compute Geometric Measures"/>\n')
    sf.close ()
    return LCur, LLast

def measure_topology(s="MLTEMP_default.mlx", LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <xmlfilter name="Compute Topological Measures"/>\n')
    sf.close ()
    return LCur, LLast

def parse_geometry(log, runlogname=None):
    """Parse the log file generated by the measure_geometry function.
    
    Warnings: Not all keys may exist if mesh is not watertight or manifold"""
    geometry = {}
    with open(log) as f:
        for line in f:
            if 'Mesh Volume' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                geometry['volume_mm3'] = to_float(line.split()[3])
                geometry['volume_cm3'] = geometry['volume_mm3'] * 0.001
            if 'Mesh Surface' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                geometry['area_mm2'] = to_float(line.split()[3])
                geometry['area_cm2'] = geometry['area_mm2'] * 0.01
            if 'Mesh Total Len of' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                #print(line.split(' '))
                if 'including faux edges' in line:
                    geometry['total_E_length_incl_fauxE'] = to_float(line.split()[7])
                else:
                    geometry['total_E_length'] = to_float(line.split()[7])
            if 'Thin shell barycenter' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                geometry['barycenter'] = (line.split()[3:6])
                geometry['barycenter'] = [to_float(a) for a in geometry['barycenter']]
            if 'Center of Mass' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                geometry['center_of_mass'] = (line.split()[4:7])
                geometry['center_of_mass'] = [to_float(a) for a in geometry['center_of_mass']]
            if 'Inertia Tensor' in line:
                geometry['inertia_tensor'] = []
                for a in range(3):
                    row = ' '.join(next(f, a).split()) # remove extra whitespace
                    row = (row.split(' ')[1:4])
                    row = [to_float(b) for b in row]
                    geometry['inertia_tensor'].append(row)
            if 'Principal axes' in line:
                geometry['principal_axes'] = []
                for a in range(3):
                    row = ' '.join(next(f, a).split()) # remove extra whitespace
                    row = (row.split(' ')[1:4])
                    row = [to_float(b) for b in row]
                    geometry['principal_axes'].append(row)
            if 'axis momenta' in line:
                line = ' '.join(next(f).split()) # remove extra whitespace
                geometry['axis_momenta'] = (line.split(' ')[1:4])
                geometry['axis_momenta'] = [to_float(a) for a in geometry['axis_momenta']]
                break # stop after we find the first match
    if runlogname is None:
        print ('volume_mm3 =', geometry['volume_mm3'], 'volume_cm3 =', geometry['volume_cm3'])
        print ('area_mm2 =', geometry['area_mm2'], 'area_cm2 =', geometry['area_cm2'])
        print('barycenter =', geometry['barycenter'])
        print('center_of_mass =', geometry['center_of_mass'])
        print('inertia_tensor =', geometry['inertia_tensor'])
        print('principal_axes =',  geometry['principal_axes'])
        print('axis_momenta =', geometry['axis_momenta'])
        print('total_E_length_incl_fauxE =', geometry['total_E_length_incl_fauxE'])
        print('total_E_length =', geometry['total_E_length'])
    else:
        RUNLOG = open(runlogname, 'a')
        if 'volume_mm3' in geometry:
            RUNLOG.write('volume_mm3 = %s, volume_cm3 = %s\n'
                      % (geometry['volume_mm3'], geometry['volume_cm3']))
        if 'area_mm2' in geometry:
            RUNLOG.write('area_mm2 = %s, area_cm2 = %s\n'
                  % (geometry['area_mm2'], geometry['area_cm2']) +
                  'total_E_length = %s\n' % geometry['total_E_length'] +
                  'total_E_length_incl_fauxE = %s\n' % geometry['total_E_length_incl_fauxE'])
        if 'barycenter' in geometry:
            RUNLOG.write('barycenter = %s\n' % geometry['barycenter'])
        if 'center_of_mass' in geometry:
            RUNLOG.write('center_of_mass = %s\n' % geometry['center_of_mass'])
        if 'inertia_tensor' in geometry:
            RUNLOG.write('inertia_tensor =\n' +
                      '  %s\n' % geometry['inertia_tensor'][0] +
                      '  %s\n' % geometry['inertia_tensor'][1] +
                      '  %s\n' % geometry['inertia_tensor'][2])
        if 'principal_axes' in geometry:
            RUNLOG.write('principal_axes = \n' +
                      '  %s\n' % geometry['principal_axes'][0] +
                      '  %s\n' % geometry['principal_axes'][1] +
                      '  %s\n' % geometry['principal_axes'][2])
        if 'axis_momenta' in geometry:
            RUNLOG.write('axis_momenta = %s\n' % geometry['axis_momenta'])
        if 'total_E_length_incl_fauxE' in geometry:
            RUNLOG.write('total_E_length_incl_fauxE = %s\n' % geometry['total_E_length_incl_fauxE'])
        if 'total_E_length' in geometry:
            RUNLOG.write('total_E_length = %s\n\n' % geometry['total_E_length'])
        RUNLOG.close()
    return geometry
    
def parse_topology(log, runlogname=None):
    """Parse the log file generated by the measure_topology function.
    
    Warnings: Not all keys may exist"""
    topology = {'manifold': True, 'non_manifold_E': 0, 'non_manifold_V': 0}
    with open(log) as f:
        for line in f:
            if 'V:' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['V_num'] = int(line.split()[1])
                topology['E_num'] = int(line.split()[3])
                topology['F_num'] = int(line.split()[5])
            if 'Unreferenced Vertices' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['unref_V_num'] = int(line.split()[2])
            if 'Boundary Edges' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['boundry_E_num'] = int(line.split()[2])
            if 'Mesh is composed by' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['part_num'] = int(line.split()[4])
            if 'non 2-manifold mesh' in line:
                topology['manifold'] = False
            if 'non two manifold edges' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['non_manifold_E'] = int(line.split()[2])
            if 'non two manifold vertexes' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['non_manifold_V'] = int(line.split()[2])
            if 'Genus is' in line: #undefined or int
                line = ' '.join(line.split()) # remove extra whitespace
                topology['genus'] = line.split()[2]
                if topology['genus'] != 'undefined':
                    topology['genus'] = int(topology['genus'])
            if 'holes' in line:
                line = ' '.join(line.split()) # remove extra whitespace
                topology['hole_num'] = line.split()[2]
                if topology['hole_num'] == 'a':
                    topology['hole_num'] = 'undefined'
                else:
                    topology['hole_num'] = int(topology['hole_num'])
    if runlogname is None:
        print('\nV_num = %d, ' % topology['V_num'], 'E_num = %d, ' % topology['E_num'],
            'F_num = %d' % topology['F_num'])
        print('part_num = %d\n' % topology['part_num'])
        print('manifold (two-manifold) = %s\n' % topology['manifold'])
        print('hole_num = %d\n' % topology['hole_num'])
        print('boundry_E_num = %d\n' % topology['boundry_E_num'])
        print('unref_V_num = %d\n' % topology['unref_V_num'])
        print('non_manifold_V = %d\n' % topology['non_manifold_V'])
        print('non_manifold_E = %d\n' % topology['non_manifold_E'])
        print('genus = %d\n' % topology['genus'])
    else:
        RUNLOG = open(runlogname, 'a')
        if 'V_num' in topology:
            RUNLOG.write('V_num = %d\n' % topology['V_num'])
            RUNLOG.write('E_num = %d\n' % topology['E_num'])
            RUNLOG.write('F_num = %d\n' % topology['F_num'])
        if 'part_num' in topology:
            RUNLOG.write('part_num = %d\n' % topology['part_num'])
        if 'manifold' in topology:
            RUNLOG.write('manifold (two-manifold) = %s\n' % topology['manifold'])
        if 'hole_num' in topology:
            RUNLOG.write('hole_num = %d\n' % topology['hole_num'])
        if 'boundry_E_num' in topology:
            RUNLOG.write('boundry_E_num = %d\n' % topology['boundry_E_num'])
        if 'unref_V_num' in topology:
            RUNLOG.write('unref_V_num = %d\n' % topology['unref_V_num'])
        if 'non_manifold_V' in topology:
            RUNLOG.write('non_manifold_V = %d\n' % topology['non_manifold_V'])
        if 'non_manifold_E' in topology:
            RUNLOG.write('non_manifold_E = %d\n' % topology['non_manifold_E'])
        if 'genus' in topology:
            RUNLOG.write('genus = %d\n' % topology['genus'])
    return topology
        
# TIP: surfaces can also be simplified after generation
# Recommended output formats:
# surface: stl, obj
# line: dxf, obj (need to process obj) - note: creates a 1D outline composed
#of line segments (not a continuous polyline but individual segments)
# points: xyz (for measuring size)
def section(s='MLTEMP_default.mlx', axis='z', offset=0.0, surface=False,
            custom_axis=[0,0,1], planeref=2, LCur=None, LLast=None):
    # Convert axis name into number
    if axis.lower()=='x':
        axis_num=0
    elif axis.lower()=='y':
        axis_num=1
    elif axis.lower()=='z':
        axis_num=2
    else: # custom axis
        axis_num=3
        if custom_axis == [0,0,1]:
            print('WARNING: a custom axis was selected, however' +
                  ' "custom_axis" was not provided. Using default (Z).')
    sf = open(s,'a')
    sf.write ('  <filter name="Compute Planar Section">\n' +

              '    <Param name="planeAxis" ' +
              'value="%d" ' % axis_num +
              'description="Plane perpendicular to" ' +
              'enum_val0="X Axis" ' +
              'enum_val1="Y Axis" ' +
              'enum_val2="Z Axis" ' +
              'enum_val3="Custom Axis" ' +
              'enum_cardinality="4" ' +
              'type="RichEnum" ' +
              'tooltip="The Slicing plane will be done perpendicular to the' +
              ' axis"/>\n' +

              '    <Param name="customAxis" ' +
              'x="%s" y="%s" z="%s" ' % (custom_axis[0],custom_axis[1],
                                         custom_axis[2]) +
              'description="Custom axis" ' +
              'type="RichPoint3f" ' +
              'tooltip="Specify a custom axis, this is only valid if the' +
              ' above parameter is set to Custom"/>\n' +

              '    <Param name="planeOffset" ' +
              'value="%s" ' % offset +
              'description="Cross plane offset" ' +
              'type="RichFloat" ' +
              'tooltip="Specify an offset of the cross-plane. The offset' +
              ' corresponds to the distance from the point specified in the' +
              ' plane reference parameter."/>\n' +

              '    <Param name="relativeTo" ' +
              'value="%s" ' % planeref +
              'description="plane reference" ' +
              'enum_val0="Bounding box center" ' +
              'enum_val1="Bounding box min" ' +
              'enum_val2="Origin" '+
              'enum_cardinality="3" ' +
              'type="RichEnum" ' +
              'tooltip="Specify the reference from which the planes are' +
              ' shifted"/>\n' +

              '    <Param name="createSectionSurface" ' +
              'value="%s" ' % str(surface).lower() +
              'description="Create also section surface" ' +
              'type="RichBool" ' +
              'tooltip="If selected, in addition to a layer with the section' +
              ' polyline, it will be created also a layer with a' +
              ' triangulated version of the section polyline. This only' +
              ' works if the section polyline is closed"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

### End measure

### Begin Cleaning & Repair ###
# (Also see Selection & Deletion section for lots of cleaning functions)

def merge_V(s='MLTEMP_default.mlx', threshold=0, LCur=None, LLast=None):
    # This filter only works on the current layer
    sf = open(s,'a')
    sf.write ('  <filter name="Merge Close Vertices">\n' +

              '    <Param name="Threshold" ' +
              'value="%s" ' % threshold +
              'description="Merging distance" ' +
              'min="0" ' +
              'max="1" ' +
              'type="RichAbsPerc" ' +
              'tooltip="All the vertices that closer than this threshold' +
              ' are merged together. Use very small values, default value' +
              ' is 1/10000 of bounding box diagonal."/>\n' +
              '  </filter>\n')
    sf.close ()
    return LCur, LLast

# TIP: run subdivide on the slected faces next if the hole is large
# TODO: automatically subdivide based on how many edges are in hole. 
# Need to experiment to find good numbers.
# Run filter with progressivley larger hole sizes, subdiving by increasing
#amounts as hole gets bigger
def close_holes(s='MLTEMP_default.mlx', hole_E_max=30, selected=False,
                sel_new_F=True, self_intersection=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Close Holes">\n' +

              '    <Param name="maxholesize" ' +
              'value="%d" ' % hole_E_max +
              'description="Max size to be closed" ' +
              'type="RichInt" ' +
              'tooltip="The size is expressed as number of edges composing' +
              ' the hole boundary."/>\n' +

              '    <Param name="Selected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Close holes with selected faces" ' +
              'type="RichBool" ' +
              'tooltip="Only the holes with at least one of the boundary' +
              ' faces selected are closed."/>\n' +

              '    <Param name="NewFaceSelected" ' +
              'value="%s" ' % str(sel_new_F).lower() +
              'description="Select the newly created faces" ' +
              'type="RichBool" ' +
              'tooltip="After closing a hole the faces that have been' +
              ' created are left selected. Any previous selection is lost.' +
              ' Useful for example for smoothing or subdividing the newly' +
              ' created holes."/>\n' +

              '    <Param name="SelfIntersection" ' +
              'value="%s" ' % str(self_intersection).lower() +
              'description="Prevent creation of selfIntersecting faces" ' +
              'type="RichBool" ' +
              'tooltip="When closing an holes it tries to prevent the' +
              ' creation of faces that intersect faces adjacent to the' +
              ' boundary of the hole. It is an heuristic, non intersecting' +
              ' hole filling can be NP-complete."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def reorient_N(s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Re-Orient all faces coherentely"/>\n')
    sf.close ()
    return LCur, LLast

def flip_N(s='MLTEMP_default.mlx', force_flip=False, selected=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Invert Faces Orientation">\n' +

              '    <Param name="forceFlip" ' +
              'value="%s" ' % str(force_flip).lower() +
              'description="Force Flip" ' +
              'type="RichBool" ' +
              'tooltip="If selected, the normals will always be flipped;' +
              ' otherwise, the filter tries to set them outside."/>\n' +

              '    <Param name="onlySelected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Flip only selected faces" ' +
              'type="RichBool" ' +
              'tooltip="If selected, only selected faces will be' +
              ' affected."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

# Will reorient normals & then make sure they are oriented outside
def fix_N(s='MLTEMP_default.mlx', LCur=None, LLast=None):
    reorient_N (s)
    flip_N (s)
    return LCur, LLast

def split_V_on_nonmanifold_F(s='MLTEMP_default.mlx', V_disp_ratio=0.0, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Split Vertexes Incident on' +
              ' Non Manifold Faces">\n' +

              '    <Param name="VertDispRatio" ' +
              'value="%d" ' % V_disp_ratio +
              'description="Vertex Displacement Ratio" ' +
              'type="RichFloat" ' +
              'tooltip="When a vertex is split it is moved along the average' +
              ' vector going from its position to the baricyenter of the' +
              ' FF connected faces sharing it."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

# TODO: need to test
def fix_folded_F(s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Isolated Folded Faces by Edge Flip"/>\n')
    sf.close ()
    return LCur, LLast

def snap_mismatched_borders(s='MLTEMP_default.mlx', E_dist_ratio=0.01,
                            unify_V=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Snap Mismatched Borders">\n' +

              '    <Param name="EdgeDistRatio" ' +
              'value="%s" ' % E_dist_ratio +
              'description="Edge Distance Ratio" ' +
              'type="RichFloat" ' +
              'tooltip="Collapse edge when the edge / distance ratio is' +
              ' greater than this value. E.g. for default value 1000 two' +
              ' straight border edges are collapsed if the central vertex' +
              ' dist from the straight line composed by the two edges less' +
              ' than a 1/1000 of the sum of the edges length. Larger values' +
              ' enforce that only vertexes very close to the line are' +
              ' removed."/>\n' +

              '    <Param name="UnifyVertices" ' +
              'value="%s" ' % str(unify_V).lower() +
              'description="UnifyVertices" ' +
              'type="RichBool" ' +
              'tooltip="If true the snap vertices are weld together."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast
    
### End Cleaning & Repair ###


### Begin Selection & Deletion ###

def sel_none(s='MLTEMP_default.mlx', all_F=True, all_V=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select None">\n' +

              '    <Param name="allFaces" ' +
              'value="%s" ' % str(all_F).lower() +
              'description="De-select all Faces" ' +
              'type="RichBool" ' +
              'tooltip="If true the filter will de-select all the' +
              ' faces."/>\n' +

              '    <Param name="allVerts" ' +
              'value="%s" ' % str(all_V).lower() +
              'description="De-select all Vertices" ' +
              'type="RichBool" ' +
              'tooltip="If true the filter will de-select all the' +
              ' vertices."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def invert_sel(s='MLTEMP_default.mlx', inv_F=True, inv_V=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Invert Selection">\n' +

              '    <Param name="InvFaces" ' +
              'value="%s" ' % str(inv_F).lower() +
              'description="Invert Faces" ' +
              'type="RichBool" ' +
              'tooltip="If true  the filter will invert the selected' +
              ' faces."/>\n' +

              '    <Param name="InvVerts" ' +
              'value="%s" ' % str(inv_V).lower() +
              'description="Invert Vertices" ' +
              'type="RichBool" ' +
              'tooltip="If true the filter will invert the selected' +
              ' vertices."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def sel_border(s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select Border"/>\n')
    sf.close ()
    return LCur, LLast

def grow_sel(s='MLTEMP_default.mlx',iterations=1, LCur=None, LLast=None):
    sf = open(s,'a')
    i=0
    while i < iterations:
        sf.write ('  <filter name="Dilate Selection"/>\n')
        i += 1
    sf.close ()
    return LCur, LLast

def shrink_sel(s='MLTEMP_default.mlx',iterations=1, LCur=None, LLast=None):
    sf = open(s,'a')
    i=0
    while i < iterations:
        sf.write ('  <filter name="Erode Selection"/>\n')
        i += 1
    sf.close ()
    return LCur, LLast

def sel_self_intersecting_F (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select Self Intersecting Faces"/>\n')
    sf.close ()
    return LCur, LLast

def sel_nonmanifold_V (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select non Manifold Vertices"/>\n')
    sf.close ()
    return LCur, LLast

def del_nonmanifold_V (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sel_nonmanifold_V (s)
    del_sel_V (s)
    #del_unreferenced_V (s)
    return LCur, LLast

def sel_nonmanifold_E (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select non Manifold Edges"/>\n')
    sf.close ()
    return LCur, LLast

def del_nonmanifold_E (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sel_nonmanifold_E (s)
    del_sel_V (s)
    #del_unreferenced_V (s)
    return LCur, LLast

def sel_small_parts (s='MLTEMP_default.mlx', ratio=0.2,
                     non_closed_only=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Small component selection">\n' +

              '    <Param name="NbFaceRatio" ' +
              'value="%s" ' % ratio +
              'description="Small component ratio" ' +
              'type="RichFloat" ' +
              'tooltip="This ratio (between 0 and 1) defines the meaning of' +
              ' _small_as the threshold ratio between the number of faces of' +
              ' the largest component and the other ones. A larger value' +
              ' will select more components."/>\n' +

              '    <Param name="NonClosedOnly" ' +
              'value="%s" ' % str(non_closed_only).lower() +
              'description="Select only non closed components" ' +
              'type="RichBool" ' +
              'tooltip="Select only non-closed components."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def del_small_parts (s='MLTEMP_default.mlx', ratio=0.2,
                     non_closed_only=False, LCur=None, LLast=None):
    sel_small_parts (s,ratio,non_closed_only)
    del_sel_V_F (s)
    return LCur, LLast

def del_sel_V (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Delete Selected Vertices"/>\n')
    sf.close ()
    return LCur, LLast

def del_sel_F (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Delete Selected Faces"/>\n')
    sf.close ()
    return LCur, LLast

def del_sel_V_F (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Delete Selected Faces and Vertices"/>\n')
    sf.close ()
    return LCur, LLast

def del_F_from_nonmanifold_E (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Faces from Non Manifold Edges"/>\n')
    sf.close ()
    del_unreferenced_V (s)
    return LCur, LLast

def del_unreferenced_V (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Unreferenced Vertex"/>\n')
    sf.close ()
    return LCur, LLast

def del_duplicate_F (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Duplicate Faces"/>\n')
    sf.close ()
    return LCur, LLast

def del_duplicate_V (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Duplicated Vertex"/>\n')
    sf.close ()
    return LCur, LLast

def del_zero_area_F (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Remove Zero Area Faces"/>\n')
    sf.close ()
    return LCur, LLast

# TODO: set min & max better
def sel_V_quality (s='MLTEMP_default.mlx', min_Q=0, max_Q=0.05,
                   inclusive=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Select by Vertex Quality">\n' +

              '    <Param name="minQ" ' +
              'value="%s" ' % min_Q +
              'description="Min Quality" ' +
              'min="0" ' +
              'max="0.1" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Minimum acceptable quality value."/>\n' +

              '    <Param name="maxQ" ' +
              'value="%s" ' % max_Q +
              'description="Max Quality" ' +
              'min="0" ' +
              'max="0.1" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Maximum acceptable quality value."/>\n' +

              '    <Param name="Inclusive" ' +
              'value="%s" ' % str(inclusive).lower() +
              'description="Inclusive Sel." ' +
              'type="RichBool" ' +
              'tooltip="If true only the faces with _all_ the vertices' +
              ' within the specified range are selected. Otherwise any face' +
              ' with at least one vertex within the range is selected."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

### End Selection & Deletion ###


### Begin Transformations ###

def translate2 (s='MLTEMP_default.mlx', amount=[0,0,0], center=False,
               freeze=True, all_L=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Transform: Move, Translate, Center">\n' +

              '    <Param name="axisX" ' +
              'value="%s" ' % amount[0] +
              'description="X Axis" ' +
              'min="-500" ' +
              'max="500" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Absolute translation amount along the X axis."/>\n' +

              '    <Param name="axisY" ' +
              'value="%s" ' % amount[1] +
              'description="Y Axis" ' +
              'min="-500" ' +
              'max="500" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Absolute translation amount along the Y axis."/>\n' +

              '    <Param name="axisZ" ' +
              'value="%s" ' % amount[2] +
              'description="Z Axis" ' +
              'min="-500" ' +
              'max="500" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Absolute translation amount along the Z axis."/>\n' +

              '    <Param name="centerFlag" ' +
              'value="%s" ' % str(center).lower() +
              'description="Translate center of bbox to the origin." ' +
              'type="RichBool" ' +
              'tooltip="Translate center of bbox to the origin."/>\n' +

              '    <Param name="Freeze" ' +
              'value="%s" ' % str(freeze).lower() +
              'description="Freeze Matrix." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied and the' +
              ' vertex coords are actually changed."/>\n' +

              '    <Param name="ToAll" ' +
              'value="%s" ' % str(all_L).lower() +
              'description="Apply to all layers." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied to all the' +
              ' mesh and raster layers in the project."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def translate(s='MLTEMP_default.mlx', amount=[0,0,0], LCur=None, LLast=None):
    """An alternative translate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    deform_func(s, x='x+%s' % amount[0],
                   y='y+%s' % amount[1],
                   z='z+%s' % amount[2])
    return LCur, LLast

def rotate2 (s='MLTEMP_default.mlx', axis='z', angle=0,
            custom_axis=[0,0,1], center_pt='origin', custom_center_pt=[0,0,0],
            freeze=True, all_L=False, LCur=None, LLast=None):
    # Convert axis name into number
    if axis.lower()=='x':
        axis_num=0
    elif axis.lower()=='y':
        axis_num=1
    elif axis.lower()=='z':
        axis_num=2
    else: # custom axis
        axis_num=3
        if custom_axis == [0,0,1]:
            print('WARNING: a custom axis was selected, however' +
                  ' "custom_axis" was not provided. Using default (Z).')
    # Convert center point name into number
    if center_pt.lower()=='origin':
        center_pt_num=0
    elif center_pt.lower()=='barycenter':
        center_pt_num=1
    else: # custom axis
        center_pt_num=2
        if custom_center_pt == [0,0,0]:
            print('WARNING: a custom center point was selected, however' +
                  ' "custom_center_pt" was not provided. Using default' +
                  ' (origin).')
    sf = open(s,'a')
    sf.write ('  <filter name="Transform: Rotate">\n' +

              '    <Param name="rotAxis" ' +
              'value="%d" ' % axis_num +
              'description="Rotation on:" ' +
              'enum_val0="X axis" ' +
              'enum_val1="Y axis" ' +
              'enum_val2="Z axis" ' +
              'enum_val3="custom axis" ' +
              'enum_cardinality="4" ' +
              'type="RichEnum" ' +
              'tooltip="Choose a method."/>\n' +

              '    <Param name="rotCenter" ' +
              'value="%d" ' % center_pt_num +
              'description="Center of rotation:" ' +
              'enum_val0="origin" ' +
              'enum_val1="barycenter" ' +
              'enum_val2="custom point" ' +
              'enum_cardinality="3" ' +
              'type="RichEnum" ' +
              'tooltip="Choose a method."/>\n' +

              '    <Param name="angle" ' +
              'value="%s" ' % angle +
              'description="Rotation Angle" ' +
              'min="-360" ' +
              'max="360" ' +
              'type="RichDynamicFloat" ' +
              'tooltip="Angle of rotation (in degrees). If snapping is' +
              ' enabled this value is rounded according to the snap' +
              ' value."/>\n' +

              '    <Param name="snapFlag" ' +
              'value="false" ' +
              'description="Snap angle" ' +
              'type="RichBool" ' +
              'tooltip="If selected, before starting the filter will remove' +
              ' any unreferenced vertex (for which curvature values are not' +
              ' defined)."/>\n' +

              '    <Param name="customAxis" ' +
              'x="%s" ' % custom_axis[0] +
              'y="%s" ' % custom_axis[1] +
              'z="%s" ' % custom_axis[2] +
              'description="Custom axis" ' +
              'type="RichPoint3f" ' +
              'tooltip="This rotation axis is used only if the' +
              ' _custom axis_ option is chosen."/>\n' +

              '    <Param name="customCenter" ' +
              'x="%s" ' % custom_center_pt[0] +
              'y="%s" ' % custom_center_pt[1] +
              'z="%s" ' % custom_center_pt[2] +
              'description="Custom center" ' +
              'type="RichPoint3f" ' +
              'tooltip="This rotation center is used only if the' +
              ' _custom point_ option is chosen."/>\n' +

              '    <Param name="snapAngle" ' +
              'value="30" ' +
              'description="Snapping Value" ' +
              'type="RichFloat" ' +
              'tooltip="This value is used to snap the rotation angle."/>\n' +

              '    <Param name="Freeze" ' +
              'value="%s" ' % str(freeze).lower() +
              'description="Freeze Matrix." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied and the' +
              ' vertex coords are actually changed."/>\n' +

              '    <Param name="ToAll" ' +
              'value="%s" ' % str(all_L).lower() +
              'description="Apply to all layers." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied to all the' +
              ' mesh and raster layers in the project."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def rotate(s='MLTEMP_default.mlx', axis='z', angle=0, LCur=None, LLast=None):
    """An alternative rotate implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    angle = math.radians(angle)
    if axis.lower()=='x':
        deform_func(s, x='x',
                       y='y*cos(%s)-z*sin(%s)' % (angle, angle),
                       z='y*sin(%s)+z*cos(%s)' % (angle, angle))
    elif axis.lower()=='y':
        deform_func(s, x='z*sin(%s)+x*cos(%s)' % (angle, angle),
                       y='y',
                       z='z*cos(%s)-x*sin(%s)' % (angle, angle))
    elif axis.lower()=='z':
        deform_func(s, x='x*cos(%s)-y*sin(%s)' % (angle, angle),
                       y='x*sin(%s)+y*cos(%s)' % (angle, angle),
                       z='z')
    else:
        print('Axis name is not valid; exiting ...')
        sys.exit(1)
    return LCur, LLast

def scale2 (s='MLTEMP_default.mlx', amount=[1.0,1.0,1.0], uniform=True,
           center_pt='origin', custom_center_pt=[0,0,0], unit=False,
           freeze=True, all_L=False, LCur=None, LLast=None):
    # Convert center point name into number
    if center_pt.lower()=='origin':
        center_pt_num=0
    elif center_pt.lower()=='barycenter':
        center_pt_num=1
    else: # custom axis
        center_pt_num=2
        if custom_center_pt == [0,0,0]:
            print('WARNING: a custom center point was selected, however' +
                  ' "custom_center_pt" was not provided. Using default' +
                  ' (origin).')
    sf = open(s,'a')
    sf.write ('  <filter name="Transform: Scale">\n' +

              '    <Param name="axisX" ' +
              'value="%s" ' % amount[0] +
              'description="X Axis" ' +
              'type="RichFloat" ' +
              'tooltip="Scaling along the X axis."/>\n' +

              '    <Param name="axisY" ' +
              'value="%s" ' % amount[1] +
              'description="Y Axis" ' +
              'type="RichFloat" ' +
              'tooltip="Scaling along the Y axis."/>\n' +

              '    <Param name="axisZ" ' +
              'value="%s" ' % amount[2] +
              'description="Z Axis" ' +
              'type="RichFloat" ' +
              'tooltip="Scaling along the Z axis."/>\n' +

              '    <Param name="uniformFlag" ' +
              'value="%s" ' % str(uniform).lower() +
              'description="Uniform Scaling" ' +
              'type="RichBool" ' +
              'tooltip="If selected an uniform scaling (the same for all the' +
              ' three axis) is applied (the X axis value is used)."/>\n' +

              '    <Param name="scaleCenter" ' +
              'value="%d" ' % center_pt_num +
              'description="Center of scaling:" ' +
              'enum_val0="origin" ' +
              'enum_val1="barycenter" ' +
              'enum_val2="custom point" ' +
              'enum_cardinality="3" ' +
              'type="RichEnum" ' +
              'tooltip="Choose a method."/>\n' +

              '    <Param name="customCenter" ' +
              'x="%s" ' % custom_center_pt[0] +
              'y="%s" ' % custom_center_pt[1] +
              'z="%s" ' % custom_center_pt[2] +
              'description="Custom center" ' +
              'type="RichPoint3f" ' +
              'tooltip="This scaling center is used only if the' +
              ' _custom point_ option is chosen."/>\n' +

              '    <Param name="unitFlag" ' +
              'value="%s" ' % str(unit).lower() +
              'description="Scale to Unit bbox" ' +
              'type="RichBool" ' +
              'tooltip="If selected, the object is scaled to a box whose' +
              ' sides are at most 1 unit length."/>\n' +

              '    <Param name="Freeze" ' +
              'value="%s" ' % str(freeze).lower() +
              'description="Freeze Matrix." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied and the' +
              ' vertex coords are actually changed."/>\n' +

              '    <Param name="ToAll" ' +
              'value="%s" ' % str(all_L).lower() +
              'description="Apply to all layers." ' +
              'type="RichBool" ' +
              'tooltip="The transformation is explicitly applied to all the' +
              ' mesh and raster layers in the project."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def scale(s='MLTEMP_default.mlx', amount=[1.0,1.0,1.0], LCur=None, LLast=None):
    """An alternative scale implementation that uses a geometric function.
    This is more accurate than the built-in version."""
    amount = check_list(amount,3)
    deform_func(s, x='x*%s' % amount[0],
                   y='y*%s' % amount[1],
                   z='z*%s' % amount[2])
    return LCur, LLast

def freeze_matrix (s='MLTEMP_default.mlx', all_L=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Freeze Current Matrix">\n' +

              '    <Param name="allLayers" ' +
              'value="%s" ' % str(all_L).lower() +
              'description="Apply to all visible Layers" ' +
              'type="RichBool" ' +
              'tooltip="If selected the filter will be applied to all' +
              ' visible layers."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

### End Transformations ###


### Begin Remeshing ###

# TIP: measure topology fist to find number of faces and area
def simplify (s='MLTEMP_default.mlx', texture=True, faces=25000,
              target_perc=0.0, quality_thr=0.3, preserve_boundary=False,
              boundary_weight=1.0, preserve_N=False, optimal_placement=True,
              planar_quadric=False, selected=False, extra_tex_coord_weight=1.0,
              preserve_topology=True, quality_weight=False, autoclean=True, LCur=None, LLast=None):
    sf = open(s,'a')

    if texture:
        sf.write ('  <filter name="Quadric Edge Collapse Decimation ' +
                  '(with texture)">\n')
    else:
        sf.write ('  <filter name="Quadric Edge Collapse Decimation">\n')      

    # Parameters common to both 'with' and 'without texture'
    sf.write ('    <Param name="TargetFaceNum" ' +
              'value="%d" ' % faces +
              'description="Target number of faces" ' +
              'type="RichInt" ' +
              'tooltip="The desired final number of faces"/>\n' +

              '    <Param name="TargetPerc" ' +
              'value="%s" ' % target_perc +
              'description="Percentage reduction (0..1)" ' +
              'type="RichFloat" ' +
              'tooltip="If non zero, this parameter specifies the desired' +
              ' final size of the mesh as a percentage of the initial' +
              ' mesh size."/>\n' +

              '    <Param name="QualityThr" ' +
              'value="%s" ' % quality_thr +
              'description="Quality threshold" ' +
              'type="RichFloat" ' +
              'tooltip="Quality threshold for penalizing bad shaped faces.' +
              ' The value is in the range [0..1]' +
              ' 0 accept any kind of face (no penalties),' +
              ' 0.5 penalize faces with quality less than 0.5,' +
              ' proportionally to their shape."/>\n' +

              '    <Param name="PreserveBoundary" ' +
              'value="%s" ' % str(preserve_boundary).lower() +
              'description="Preserve Boundary of the mesh" ' +
              'type="RichBool" ' +
              'tooltip="The simplification process tries not to affect mesh' +
              ' boundaries"/>\n' +

              '    <Param name="BoundaryWeight" ' +
              'value="%s" ' % boundary_weight +
              'description="Boundary Preserving Weight" ' +
              'type="RichFloat" ' +
              'tooltip="The importance of the boundary during simplification.' +
              ' Default (1.0) means that the boundary has the same importance' +
              ' of the rest. Values greater than 1.0 raise boundary importance' +
              ' and has the effect of removing less vertices on the border.' +
              ' Admitted range of values (0,+inf)."/>\n' +

              '    <Param name="OptimalPlacement" ' +
              'value="%s" ' % str(optimal_placement).lower() +
              'description="Optimal position of simplified vertices" ' +
              'type="RichBool" ' +
              'tooltip="Each collapsed vertex is placed in the position' +
              ' minimizing the quadric error. It can fail (creating bad' +
              ' spikes) in case of very flat areas. If disabled edges' +
              ' are collapsed onto one of the two original vertices and' +
              ' the final mesh is composed by a subset of the original' +
              ' vertices."/>\n' +

              '    <Param name="PreserveNormal" ' +
              'value="%s" ' % str(preserve_N).lower() +
              'description="Preserve Normal" ' +
              'type="RichBool" ' +
              'tooltip="Try to avoid face flipping effects and try to' +
              ' preserve the original orientation of the surface"/>\n' +

              '    <Param name="PlanarQuadric" ' +
              'value="%s" ' % str(planar_quadric).lower() +
              'description="Planar Simplification" ' +
              'type="RichBool" ' +
              'tooltip="Add additional simplification constraints that' +
              ' improves the quality of the simplification of the planar' +
              ' portion of the mesh."/>\n' +

              '    <Param name="Selected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Simplify only selected faces" ' +
              'type="RichBool" ' +
              'tooltip="The simplification is applied only to the selected' +
              ' set of faces. Take care of the target number of faces!"/>\n')

    if texture: # Parameters unique to 'with texture'
        sf.write ('    <Param name="Extratcoordw" ' +
                  'value="%s" ' % extra_tex_coord_weight +
                  'description="Texture Weight" ' +
                  'type="RichFloat" ' +
                  'tooltip="Additional weight for each extra Texture' +
                  ' Coordinates for every (selected) vertex"/>\n')

    else: # Parameters unique to 'without texture'
        sf.write ('    <Param name="PreserveTopology" ' +
                  'value="%s" ' % str(preserve_topology).lower() +
                  'description="Preserve Topology" ' +
                  'type="RichBool" ' +
                  'tooltip="Avoid all the collapses that should cause a' +
                  ' topology change in the mesh (like closing holes,' +
                  ' squeezing handles, etc). If checked the genus of the' +
                  ' mesh should stay unchanged."/>\n' +

                  '    <Param name="QualityWeight" ' +
                  'value="%s" ' % str(quality_weight).lower() +
                  'description="Weighted Simplification" ' +
                  'type="RichBool" ' +
                  'tooltip="Use the Per-Vertex quality as a weighting factor' +
                  ' for the simplification. The weight is used as a error' +
                  ' amplification value, so a vertex with a high quality' +
                  ' value will not be simplified and a portion of the mesh' +
                  ' with low quality values will be aggressively' +
                  ' simplified."/>\n' +

                  '    <Param name="AutoClean" ' +
                  'value="%s" ' % str(autoclean).lower() +
                  'description="Post-simplification cleaning" ' +
                  'type="RichBool" ' +
                  'tooltip="After the simplification an additional set of' +
                  ' steps is performed to clean the mesh (unreferenced' +
                  ' vertices, bad faces, etc)/>\n')

    sf.write ('  </filter>\n')
    sf.close ()
    return LCur, LLast

# If you prefer to use a precision (as a percentage of AABB[diag])
#instead of the voxel cell size include the following code in the parent
# and pass voxel:
#   precision=1 # 1% of AABB[diag]
#   voxel=$(bc <<< "(${AABB[diag]} * 0.01 * $precision)")
def offset(s='MLTEMP_default.mlx', voxel=1, delta=0, merge_V=True,
           discretize=False, multisample=False, thicken=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Uniform Mesh Resampling">\n' +

              '    <Param name="CellSize" ' +
              'value="%s" ' % voxel +
              'description="Precision" ' +
              'min="0" ' +
              'max="100" ' +
              'type="RichAbsPerc" ' +
              'tooltip="Voxel (cell) size for resampling. Smaller cells give' +
              ' better precision at a higher computational cost. Remember' +
              ' that halving the cell size means that you build a volume 8' +
              ' times larger."/>\n' +

              '    <Param name="Offset" ' +
              'value="%s" ' % delta +
              'description="Offset" ' +
              'min="-100" ' +
              'max="100" ' +
              'type="RichAbsPerc" ' +
              'tooltip=" Offset amount of the created surface (i.e. distance' +
              ' of the created surface from the original one). If offset is' +
              ' zero, the created surface passes on the original mesh' +
              ' itself. Values greater than zero mean an external surface' +
              ' (offset), and lower than zero mean an internal surface' +
              ' (inset). In practice this value is the threshold passed to' +
              ' the Marching Cube algorithm to extract the isosurface from' +
              ' the distance field representation."/>\n' +

              '    <Param name="mergeCloseVert" ' +
              'value="%s" ' % str(merge_V).lower() +
              'description="Clean Vertices" ' +
              'type="RichBool" ' +
              'tooltip="If true the mesh generated by MC will be cleaned by' +
              ' unifying vertices that are almost coincident"/>\n' +

              '    <Param name="discretize" ' +
              'value="%s" ' % str(discretize).lower() +
              'description="Discretize" ' +
              'type="RichBool" ' +
              'tooltip="If true the position of the intersected edge of the' +
              ' marching cube grid is not computed by linear interpolation,' +
              ' but it is placed in fixed middle position. As a consequence' +
              ' the resampled object will look severely aliased by a' +
              ' stairstep appearance. Useful only for simulating the output' +
              ' of 3D printing devices."/>\n' +

              '    <Param name="multisample" ' +
              'value="%s" ' % str(multisample).lower() +
              'description="Multisample" ' +
              'type="RichBool" ' +
              'tooltip="If true the distance field is more accurately' +
              ' compute by multisampling the volume (7 sample for each' +
              ' voxel). Much slower but less artifacts."/>\n' +

              '    <Param name="absDist" ' +
              'value="%s" ' % str(thicken).lower() +
              'description="Absolute Distance" ' +
              'type="RichBool" ' +
              'tooltip="If true, you have to choose a not zero Offset and a' +
              ' double surface is built around the original surface, inside' +
              ' and outside. Is useful to convert thin floating surfaces' +
              ' into solid, thick meshes."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def subdivide_loop(s='MLTEMP_default.mlx', iterations=1, loop_weight=0,
               E_threshold=0, selected=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Subdivision Surfaces: Loop">\n' +

              '    <Param name="LoopWeight" ' +
              'value="%d" ' % loop_weight +
              'description="Weighting scheme" ' +
              'enum_val0="Loop" ' +
              'enum_val1="Enhance regularity" ' +
              'enum_val2="Enhance continuity" ' +
              'enum_cardinality="3" ' +
              'type="RichEnum" ' +
              'tooltip="Change the weights used. Allow to optimize some' +
              ' behaviours in spite of others."/>\n' +

              '    <Param name="Iterations" ' +
              'value="%d" ' % iterations +
              'description="Iterations" ' +
              'type="RichInt" ' +
              'tooltip="Number of times the model is subdivided"/>\n' +

              '    <Param name="Threshold" ' +
              'value="%s" ' % E_threshold +
              'description="Edge Threshold" ' +
              'min="0" ' +
              'max="100" ' +
              'type="RichAbsPerc" ' +
              'tooltip="All the edges longer than this threshold will be' +
              ' refined. Setting this value to zero will force an uniform' +
              ' refinement."/>\n' +

              '    <Param name="Selected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Affect only selected faces" ' +
              'type="RichBool" ' +
              'tooltip="If selected the filter is performed only on the' +
              ' selected faces"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast


# def subdivide_butterfly:
# def subdivide_CC:
# def subdivide_LS3loop:
def subdivide_midpoint(s='MLTEMP_default.mlx', iterations=1, E_threshold=0,
                selected=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Subdivision Surfaces: Midpoint">\n' +

              '    <Param name="Iterations" ' +
              'value="%d" ' % iterations +
              'description="Iterations" ' +
              'type="RichInt" ' +
              'tooltip="Number of times the model is subdivided"/>\n' +

              '    <Param name="Threshold" ' +
              'value="%s" ' % E_threshold +
              'description="Edge Threshold" ' +
              'min="0" ' +
              'max="100" ' +
              'type="RichAbsPerc" ' +
              'tooltip="All the edges longer than this threshold will be' +
              ' refined. Setting this value to zero will force an uniform' +
              ' refinement."/>\n' +

              '    <Param name="Selected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Affect only selected faces" ' +
              'type="RichBool" ' +
              'tooltip="If selected the filter is performed only on the' +
              ' selected faces"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def deform_func(s='MLTEMP_default.mlx', x='x', y='y', z='z',
                LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Geometric Function">\n' +

              '    <Param name="x" ' +
              'value="%s" ' % x.replace('<','&lt;') +
              'description="func x = " ' +
              'type="RichString" ' +
              'tooltip="insert function to generate new coord for x"/>\n' +

              '    <Param name="y" ' +
              'value="%s" ' % y.replace('<','&lt;') +
              'description="func y = " ' +
              'type="RichString" ' +
              'tooltip="insert function to generate new coord for y"/>\n' +

              '    <Param name="z" ' +
              'value="%s" ' % z.replace('<','&lt;') +
              'description="func z = " ' +
              'type="RichString" ' +
              'tooltip="insert function to generate new coord for z"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def deform2cylinder(s='MLTEMP_default.mlx', r=1, pitch=0, LCur=None, LLast=None):
    """Deform mesh around cylinder of radius r and axis z
    
    y = 0 will be on the surface of radius r
    pitch != 0 will create a helix, with distance "pitch" traveled in z for each rotation
    
    """
    """deform_func(s=s, x='(%s+y)*sin(x/(%s+y))' % (r, r),
                     y='(%s+y)*cos(x/(%s+y))' % (r, r),
                     z='z-%s*x/(2*%s*(%s+y))' % (pitch, pi, r))"""
    deform_func(s=s, x='(%s+y)*sin(x/%s)' % (r, r),
                     y='(%s+y)*cos(x/%s)' % (r, r),
                     z='z-%s*x/(2*%s*%s)' % (pitch, math.pi, r))
    return LCur, LLast

def deform_bend(s='MLTEMP_default.mlx', r=1,  pitch=0, angle=0, straightEnds=False, LCur=None, LLast=None):
    """Bends mesh around cylinder of radius r and axis z to a certain angle
    
    straightEnds: Only apply twist (pitch) over the area that is bent
    """
    angle = math.radians(angle/2)
    segment = r*angle
    """deform_func(s=s, x='if(x<%s and x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(%s/%s)+(x-%s)*cos(%s/%s))'
                        % (segment, segment,  r, r,  r, segment, r, segment, segment, r),
                     y='if(x<%s*%s/2 and x>-%s*%s/2, (%s+y)*cos(x/%s), (%s+y)*cos(%s)-(x-%s*%s)*sin(%s))'
                        % (r, angle, r, angle, r, r, r, angle/2, r, angle/2, angle/2),"""
    xfunc = 'if(x<%s, if(x>-%s, (%s+y)*sin(x/%s), (%s+y)*sin(-%s)+(x+%s)*cos(-%s)), (%s+y)*sin(%s)+(x-%s)*cos(%s))' % (segment, segment,  r, r,  r, angle, segment, angle,   r, angle, segment, angle)
    yfunc = 'if(x<%s, if(x>-%s, (%s+y)*cos(x/%s), (%s+y)*cos(-%s)-(x+%s)*sin(-%s)), (%s+y)*cos(%s)-(x-%s)*sin(%s))' % (segment, segment,  r, r,  r, angle, segment, angle,   r, angle, segment, angle)
    if straightEnds:
        zfunc = z='if(x<%s, if(x>-%s, z-%s*x/(2*%s*%s), z+%s*%s/(2*%s)), z-%s*%s/(2*%s))' % (segment, segment, pitch, math.pi, r, pitch, angle, math.pi, pitch, angle, math.pi)
    else:
        zfunc = 'z-%s*x/(2*%s*%s)' % (pitch, math.pi, r)
    deform_func(s=s, x=xfunc, y=yfunc, z=zfunc)
    return LCur, LLast

# TODO: add function to round mesh to desired tolerance
# use muparser rint (round to nearest integer)
    
def smooth_laplacian(s='MLTEMP_default.mlx', iterations=1, boundary=True,
           cotangent_weight=True, selected=False, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Laplacian Smooth">\n' +

              '    <Param name="stepSmoothNum" ' +
              'value="%d" ' % iterations +
              'description="Smoothing steps" ' +
              'type="RichInt" ' +
              'tooltip="The number of times that the whole algorithm' +
              ' (normal smoothing + vertex fitting) is iterated."/>\n' +

              '    <Param name="Boundary" ' +
              'value="%s" ' % str(boundary).lower() +
              'description="1D Boundary Smoothing" ' +
              'type="RichBool" ' +
              'tooltip="If true the boundary edges are smoothed only by' +
              ' themselves (e.g. the polyline forming the boundary of the' +
              ' mesh is independently smoothed). Can reduce the shrinking' +
              ' on the border but can have strange effects on very small' +
              ' boundaries."/>\n' +

              '    <Param name="cotangentWeight" ' +
              'value="%s" ' % str(cotangent_weight).lower() +
              'description="Cotangent weighting" ' +
              'type="RichBool" ' +
              'tooltip="If true the cotangent weighting scheme is computed' +
              ' for the averaging of the position. Otherwise (false) the' +
              ' simpler umbrella scheme (1 if the edge is present) is' +
              ' used."/>\n' +

              '    <Param name="Selected" ' +
              'value="%s" ' % str(selected).lower() +
              'description="Affect only selected faces" ' +
              'type="RichBool" ' +
              'tooltip="If selected the filter is performed only on the' +
              ' selected faces"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def hull (s='MLTEMP_default.mlx', reorient_N=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Convex Hull">\n' +

              '    <Param name="reorient" ' +
              'value="%s" ' % str(reorient_N).lower() +
              'description="Re-orient all faces coherentely" ' +
              'type="RichBool" ' +
              'tooltip="Re-orient all faces coherentely after hull' +
              ' operation."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def reconstruct_surface_poisson (s='MLTEMP_default.mlx', octree_depth=10,
                         solver_divide=8, samples_per_node=1.0, offset=1.0, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Surface Reconstruction: Poisson">\n' +

              '    <Param name="OctDepth" ' +
              'value="%d" ' % octree_depth +
              'description="Octree Depth" ' +
              'type="RichInt" ' +
              'tooltip="Set the depth of the Octree used for extracting the' +
              ' final surface. Suggested range 5..10. Higher numbers mean' +
              ' higher precision in the reconstruction but also higher' +
              ' processing times. Be patient."/>\n' +

              '    <Param name="SolverDivide" ' +
              'value="%d" ' % solver_divide +
              'description="Solver Divide" ' +
              'type="RichInt" ' +
              'tooltip="This integer argument specifies the depth at which' +
              ' a block Gauss-Seidel solver is used to solve the Laplacian' +
              ' equation. Using this parameter helps reduce the memory' +
              ' overhead at the cost of a small increase in reconstruction' +
              ' time. In practice, the authors have found that for' +
              ' reconstructions of depth 9 or higher a subdivide depth of 7' +
              ' or 8 can reduce the memory usage. The default value is' +
              ' 8."/>\n' +

              '    <Param name="SamplesPerNode" ' +
              'value="%s" ' % samples_per_node +
              'description="Samples per Node" ' +
              'type="RichFloat" ' +
              'tooltip="This floating point value specifies the minimum' +
              ' number of sample points that should fall within an octree' +
              ' node as the octree&#xa;construction is adapted to sampling' +
              ' density. For noise-free samples, small values in the range' +
              ' [1.0 - 5.0] can be used. For more noisy samples, larger' +
              ' values in the range [15.0 - 20.0] may be needed to provide' +
              ' a smoother, noise-reduced, reconstruction. The default' +
              ' value is 1.0."/>\n' +

              '    <Param name="Offset" ' +
              'value="%s" ' % offset +
              'description="Surface offsetting" ' +
              'type="RichFloat" ' +
              'tooltip="This floating point value specifies a correction' +
              ' value for the isosurface threshold that is chosen. Values' +
              ' less than 1 mean internal offsetting, greater than 1 mean' +
              ' external offsetting. Good values are in the range 0.5 .. 2.' +
              ' The default value is 1.0 (no offsetting)."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

### End Remeshing ###


### Begin Mesh Layers ###
    
# NOTE: filter will discard textures, creates a new layer "Merged Mesh"
# merge_V looks to be a key one; experiment with this
def join_L (s='MLTEMP_default.mlx', merge_visible=True, merge_V=False,
               del_L=True, keep_unreferenced_V=False, LCur=None, LLast=None):
    if  LCur is not None:
        if del_L:
            LCur = 0
            LLast = 0
        else:
            LCur += 1
            LLast += 1
    sf = open(s,'a')
    sf.write ('  <filter name="Flatten Visible Layers">\n' +

              '    <Param name="MergeVisible" ' +
              'value="%s" ' % str(merge_visible).lower() +
              'description="Merge Only Visible Layers" ' +
              'type="RichBool" ' +
              'tooltip="Merge only visible layers"/>\n' +

              '    <Param name="MergeVertices" ' +
              'value="%s" ' % str(merge_V).lower() +
              'description="Merge duplicate vertices" ' +
              'type="RichBool" ' +
              'tooltip="Merge the vertices that are duplicated among' +
              ' different layers. Very useful when the layers are spliced' +
              ' portions of a single big mesh."/>\n' +

              '    <Param name="DeleteLayer" ' +
              'value="%s" ' % str(del_L).lower() +
              'description="Delete Layers" ' +
              'type="RichBool" ' +
              'tooltip="Delete all the merged layers. If all layers are' +
              ' visible only a single layer will remain after the' +
              ' invocation of this filter."/>\n' +

              '    <Param name="AlsoUnreferenced" ' +
              'value="%s" ' % str(keep_unreferenced_V).lower() +
              'description="Keep unreferenced vertices" ' +
              'type="RichBool" ' +
              'tooltip="Do not discard unreferenced vertices from source' +
              ' layers. Necessary for point-only layers"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def del_L (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    """Delete current layer"""
    if  LCur is not None:
        LCur -= 1
        LLast -= 1
    sf = open(s,'a')
    sf.write ('  <filter name="Delete Current Mesh"/>\n')
    sf.close ()
    return LCur, LLast

def rename_L (s='MLTEMP_default.mlx', label='blank', LCur=None, LLast=None):
    """Renames current layer label. Not currently very useful for non-interctive use."""
    sf = open(s,'a')
    sf.write ('  <filter name="Rename Current Mesh">\n' +

              '    <Param name="newName" ' +
              'value="%s" ' % label +
              'description="New Label" ' +
              'type="RichString" ' +
              'tooltip="New Label for the mesh"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def change_L (s='MLTEMP_default.mlx', LNum=0, LCur=None, LLast=None):
    """change the current layer by specifying the new layer number.
    BROKEN: this filter crashes meshlabserver but runs fine in the gui. A MeshLab bug is suspected.
    TODO: do some more troubleshooting before filing a bug report.
      Find the minimum case that will cause this to occur, i.e. open cube, duplicate, change_L
      test on different computers
      does initial delete filter have anything to do with it?
      
    """
    if  LCur is not None:
        LCur = LNum
    sf = open(s,'a')
    sf.write ('  <filter name="Change the current layer">\n' +

              '    <Param name="mesh" ' +
              'value="%d" ' % LNum +
              'description="Mesh" ' +
              'type="RichMesh" ' +
              'tooltip="The number of the layer to change to"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def duplicate_L (s='MLTEMP_default.mlx', LCur=None, LLast=None):
    """Duplicate the current layer. New layer label is '*_copy'."""
    if  LCur is not None:
        LCur += 1
        LLast += 1
    sf = open(s,'a')
    sf.write ('  <filter name="Duplicate Current layer"/>\n')
    sf.close ()
    return LCur, LLast

def split_parts(s='MLTEMP_default.mlx', partNum=None, LCur=None, LLast=None):
    """Splits mesh into separate parts (components). Creates layers named
    'CC 0', 'CC 1', etc.
    
    Warnings: does not preserve textures."""
    if  LCur is not None:
        if partNum is not None:
            LCur += partNum
            LLast += partNum
        else:
            print('Warning: the number of parts was not provided and cannot be determined automatically. Cannot set correct current layer LCur and last layer LLast values.')
    sf = open(s,'a')
    sf.write ('  <filter name="Split in Connected Components"/>\n')
    sf.close ()
    return LCur, LLast

### End Mesh Layers ###


### Begin Create ###

def cube (s='MLTEMP_default.mlx', size=1.0, center=False, color=None, LCur=None, LLast=None):
    """Create a cube primitive"""
    if  LCur is not None:
        LCur += 1
        LLast += 1
    if not isinstance(size, list):
        size = [size, size, size]
    sf = open(s,'a')
    sf.write ('  <filter name="Box">\n' +

              '    <Param name="size" ' +
              'value="1.0" ' +
              'description="Scale factor" ' +
              'type="RichFloat" ' +
              'tooltip="Scales the new mesh"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    scale (s, amount=size)
    # Box is centered on origin at creation
    if not center:
        translate (s, amount=[size[0]/2, size[1]/2, size[2]/2] )
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast


# Usage: height=(1) (radius=(1)|(radius1=(1) radius2=(1)))|(diameter=(2)|(diameter1=(2) diameter2=(2))) center=(false)
# Note: need to know m_up in order to orient cylinder correctly!
# OpenSCAD cylinder:
#    h This is the height of the cylinder. Default value is 1.
#    r The radius of both top and bottom ends of the cylinder. Use this parameter if you want plain cylinder. Default value is 1.
#    r1 This is the radius of the cone on bottom end. Default value is 1.
#    r2 This is the radius of the cone on top end. Default value is 1.
#    d The diameter of both top and bottom ends of the cylinder. Use this parameter if you want plain cylinder. Default value is 1.
#    d1 This is the diameter of the cone on bottom end. Default value is 1.
#    d2 This is the diameter of the cone on top end. Default value is 1.
#    center If true will center the height of the cone/cylinder around the origin. Default is false, placing the base of the cylinder or r1 radius of cone at the origin.
def cylinder (s='MLTEMP_default.mlx', up='z', h=1.0, r=None, r1=None,
              r2=None, d=None, d1=None, d2=None, 
              center=False, segmentsC=32, color=None, LCur=None, LLast=None):
    """Create a cylinder or cone primitive. Usage is based on OpenSCAD.
    # h = height of the cylinder
    # r1 = radius of the cone on bottom end
    # r2 = radius of the cone on top end
    # center = If true will center the height of the cone/cylinder around
    # the origin. Default is false, placing the base of the cylinder or r1
    # radius of cone at the origin.
    # color = specify a color name to apply vertex colors to the newly
    # created mesh
    """
    if  LCur is not None:
        LCur += 1
        LLast += 1
    if r is not None and d is None:
        if r1 is None and d1 is None:
            r1 = r
        if r2 is None and d2 is None:
            r2 = r
    if d is not None:
        if r1 is None and d1 is None:
            r1 = d/2
        if r2 is None and d2 is None:
            r2 = d/2
    if d1 is not None:
        r1 = d1/2
    if d2 is not None:
        r2 = d2/2
    if r1 is None:
        r1 = 1.0
    if r2 is None:
        r2 = r1

    # Cylinder is created centered with Y up
    sf = open(s,'a')
    sf.write ('  <filter name="Cone">\n' +

              '    <Param name="h" ' +
              'value="%s" ' % h +
              'description="Height" ' +
              'type="RichFloat" ' +
              'tooltip="Height of the Cone"/>\n' +

              '    <Param name="r0" ' +
              'value="%s" ' % r1 +
              'description="Radius 1" ' +
              'type="RichFloat" ' +
              'tooltip="Radius of the bottom circumference"/>\n' +

              '    <Param name="r1" ' +
              'value="%s" ' % r2 +
              'description="Radius 2" ' +
              'type="RichFloat" ' +
              'tooltip="Radius of the top circumference"/>\n' +

              '    <Param name="subdiv" ' +
              'value="%d" ' % segmentsC +
              'description="Side" ' +
              'type="RichInt" ' +
              'tooltip="Number of sides of the polygonal approximation of' +
              ' the cone"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    if not center:
        translate (s, [0, h/2, 0])
    if up.lower() == 'z':
        rotate (s, axis='x', angle=90) # rotate to Z up
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def sphere (s='MLTEMP_default.mlx', radius=1.0, diameter=None,
            subdiv=3, color=None, LCur=None, LLast=None):
    """# subdiv = Subdivision level; Number of the recursive subdivision of the
    # surface. Default is 3 (a sphere approximation composed by 1280 faces).
    # Admitted values are in the range 0 (an icosahedron) to 8 (a 1.3 MegaTris
    # approximation of a sphere). Formula for number of faces: F=20*4^subdiv
    # color = specify a color name to apply vertex colors to the newly
    # created mesh"""
    if  LCur is not None:
        LCur += 1
        LLast += 1
    if diameter is not None:
        radius = diameter/2
    
    sf = open(s,'a')
    sf.write ('  <filter name="Sphere">\n' +

              '    <Param name="radius" ' +
              'value="%s" ' % radius +
              'description="Radius" ' +
              'type="RichFloat" ' +
              'tooltip="Radius of the sphere"/>\n' +

              '    <Param name="subdiv" ' +
              'value="%d" ' % subdiv +
              'description="Subdiv. Level" ' +
              'type="RichInt" ' +
              'tooltip="Number of the recursive subdivision of the surface.' +
              ' Default is 3 (a sphere approximation composed by 1280' +
              ' faces). Admitted values are in the range 0 (an icosahedron)' +
              ' to 8 (a 1.3 MegaTris approximation of a sphere)."/>\n' +
              
              '  </filter>\n')
    sf.close ()
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def sphere_cap (s='MLTEMP_default.mlx', angle=1.0,
            subdiv=3, color=None, LCur=None, LLast=None):
    """# angle = Angle of the cone subtending the cap. It must be <180
    # subdiv = Subdivision level; Number of the recursive subdivision of the
    # surface. Default is 3 (a sphere approximation composed by 1280 faces).
    # Admitted values are in the range 0 (an icosahedron) to 8 (a 1.3 MegaTris
    # approximation of a sphere). Formula for number of faces: F=20*4^subdiv
    # color = specify a color name to apply vertex colors to the newly
    # created mesh"""
    if  LCur is not None:
        LCur += 1
        LLast += 1
    sf = open(s,'a')
    sf.write ('  <filter name="Sphere Cap">\n' +

              '    <Param name="angle" ' +
              'value="%s" ' % angle +
              'description="Angle" ' +
              'type="RichFloat" ' +
              'tooltip="Angle of the cone subtending the cap. It must be' +
              ' less than 180"/>\n' +

              '    <Param name="subdiv" ' +
              'value="%d" ' % subdiv +
              'description="Subdiv. Level" ' +
              'type="RichInt" ' +
              'tooltip="Number of the recursive subdivision of the surface.' +
              ' Default is 3 (a sphere approximation composed by 1280' +
              ' faces). Admitted values are in the range 0 (an icosahedron)' +
              ' to 8 (a 1.3 MegaTris approximation of a sphere)."/>\n' +
              
              '  </filter>\n')
    sf.close ()
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def torus (s='MLTEMP_default.mlx', up='z', rH=3.0, rV=1.0,
              ID=None, OD=None, segmentsHC=24, segmentsVC=12, color=None, LCur=None, LLast=None):
    """
    rH=3 # Radius of the whole horizontal ring of the torus
    rV=1 # Radius of the vertical section of the ring
    ID # Alt; inner diameter of torus, ID=2*(rH-rV)
    OD # Alt; outer diameter of torus, OD=2*(rH+rV)
    fn_h=24 # Subdivision step of the ring
    fn_v=12 # Number of sides of the polygonal approximation of the torus section
    color="" # specify a color name to apply vertex colors to the newly created mesh
    """
    if  LCur is not None:
        LCur += 1
        LLast += 1
    # TODO: add support for up direction
    if ID is not None and OD is not None:
        rH = (ID + OD)/4
        rV = rH - ID/2

    sf = open(s,'a')
    sf.write ('  <filter name="Torus">\n' +

              '    <Param name="hRadius" ' +
              'value="%s" ' % rH +
              'description="Horizontal Radius" ' +
              'type="RichFloat" ' +
              'tooltip="Radius of the whole horizontal ring of the torus"/>\n' +

              '    <Param name="vRadius" ' +
              'value="%s" ' % rV +
              'description="Vertical Radius" ' +
              'type="RichFloat" ' +
              'tooltip="Radius of the vertical section of the ring"/>\n' +

              '    <Param name="hSubdiv" ' +
              'value="%d" ' % segmentsHC +
              'description="Horizontal Subdivision" ' +
              'type="RichInt" ' +
              'tooltip="Subdivision step of the ring"/>\n' +

              '    <Param name="vSubdiv" ' +
              'value="%d" ' % segmentsVC +
              'description="Vertical Subdivision" ' +
              'type="RichInt" ' +
              'tooltip="Number of sides of the polygonal approximation of' +
              ' the torus section"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def plane (s='MLTEMP_default.mlx', size=1.0, segmentsX=1, segmentsY=1,
            center=False, color=None, LCur=None, LLast=None):
    """2D square/plane/grid created on XY plane
    num_V_X=2 # Number of vertices in the X direction. Must be at least 2
    (start and end vertices); setting this to a higher value will create an
    evenly spaced grid.
    num_V_Y=2 # Number of vertices in the Y direction. Must be at least 2
    (start and end vertices); setting this to a higher value will create an
    evenly spaced grid.
    center="false" # If true square will be centered on origin;
    otherwise it is place in the positive XY quadrant. Note that the
    "center" parameter in the mlx script does not actually center the square,
    not sure what it is doing. Instead this is set to false, which places
    the plane in the -X,+Y quadrant, and it is translated to the
    appropriate position after creation.
    """
    if  LCur is not None:
        LCur += 1
        LLast += 1
    if not isinstance(size, list):
        size = [size, size]
    # TODO: check that only 1 or 2 parameters were passed. Print a warning if not.

    sf = open(s,'a')
    sf.write ('  <filter name="Grid Generator">\n' +

              '    <Param name="absScaleX" ' +
              'value="%s" ' % size[0] +
              'description="x scale" ' +
              'type="RichFloat" ' +
              'tooltip="absolute scale on x (float)"/>\n' +

              '    <Param name="absScaleY" ' +
              'value="%s" ' % size[1] +
              'description="y scale" ' +
              'type="RichFloat" ' +
              'tooltip="absolute scale on y (float)"/>\n' +

              '    <Param name="numVertX" ' +
              'value="%d" ' % (segmentsX + 1) +
              'description="num vertices on x" ' +
              'type="RichInt" ' +
              'tooltip="number of vertices on x. it must be positive"/>\n' +

              '    <Param name="numVertY" ' +
              'value="%d" ' % (segmentsY + 1) +
              'description="num vertices on y" ' +
              'type="RichInt" ' +
              'tooltip="number of vertices on y. it must be positive"/>\n' +

              '    <Param name="center" ' +
              'value="false" ' +
              'description="centered on origin" ' +
              'type="RichBool" ' +
              'tooltip="center grid generated by filter on origin.' +
              ' Grid is first generated and than moved into origin (using' +
              ' muparser lib to perform fast calc on every vertex)"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    deform_func(s, z='rint(z)')
    """This is to work around a bug in MeshLab whereby the Grid Generator does not 
    create zero values for z. Ref bug #458: https://sourceforge.net/p/meshlab/bugs/458/"""
    if center:
        translate(s, amount=[size[0]/2, -size[1]/2, 0] )
    else:
        translate(s, amount=[size[0], 0, 0] )
    if color is not None:
        color_V(s, color=color)
    return LCur, LLast

def annulus(s='MLTEMP_default.mlx', r=None, r1=None, r2=None, d=None,
            d1=None, d2=None, segmentsC=32, color=None, LCur=None, LLast=None):
    """Create a 2D (surface) circle or annulus
    r1=1 # Outer radius of the circle
    r2=0 # Inner radius of the circle (if non-zero it creates an annulus)
    color="" # specify a color name to apply vertex colors to the newly created mesh
    
    OpenSCAD: parameters: d overrides r, r1 & r2 override r
    """
    if  LCur is not None:
        LCur += 1
        LLast += 1
    if r is not None and d is None:
        if r1 is None and d1 is None:
            r1 = r
        if r2 is None and d2 is None:
            r2 = 0
    if d is not None:
        if r1 is None and d1 is None:
            r1 = d/2
        if r2 is None and d2 is None:
            r2 = 0
    if d1 is not None:
        r1 = d1/2
    if d2 is not None:
        r2 = d2/2
    if r1 is None:
        r1 = 1
    if r2 is None:
        r2 = 0

    # Circle is created centered on the XY plane
    sf = open(s,'a')
    sf.write('  <filter name="Annulus">\n' +

             '    <Param name="externalRadius" ' +
             'value="%s" ' % r1 +
             'description="External Radius" ' +
             'type="RichFloat" ' +
             'tooltip="External Radius of the annulus"/>\n' +

             '    <Param name="internalRadius" ' +
             'value="%s" ' % r2 +
             'description="Internal Radius" ' +
             'type="RichFloat" ' +
             'tooltip="Internal Radius of the annulus"/>\n' +

             '    <Param name="sides" ' +
             'value="%d" ' % segmentsC +
             'description="Sides" ' +
             'type="RichInt" ' +
             'tooltip="Number of sides of the polygonal approximation of' +
             ' the annulus"/>\n' +

             '  </filter>\n')
    sf.close()
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def cube_hires(s='MLTEMP_default.mlx', size=1.0, segmentsX=1, segmentsY=1, segmentsZ=1, simpleBottom=True, topZ=True, centerXY=False, center=False, color=None, LCur=None, LLast=None):
    """Create a box with user defined number of segments in each direction.
    
    Grid spacing is the same as its dimensions (spacing = 1) and its
    thickness is one. Intended to be used for e.g. deforming using functions
    or a height map (lithopanes) and can be resized after creation.
    
    Warnings: function uses join_L
    
    """
    if not isinstance(size, list):
        size = [size, size, size]
    # TODO: check that size has the correct number of arguments
    
    # Top
    LCur, LLast = plane(s, size, segmentsX, segmentsY, LCur=LCur, LLast=LLast)
    
    # Bottom
    if simpleBottom:
        LCur, LLast = plane(s, size=[size[0]+size[1]-1, 1], segmentsX=(size[0]+size[1]-1), segmentsY=1, LCur=LCur, LLast=LLast)
        # Deform left side
        deform_func(s, x='if((y>0) and (x<%s),0,x)' % (size[1]),
                    y='if((y>0) and (x<%s),x+1,y)' % (size[1]))
        # Deform top
        deform_func(s, x='if((y>0) and (x>=%s),x-%s+1,x)' % (size[1], size[1]),
                    y='if((y>0) and (x>=%s),%s,y)' % (size[1], size[1]))
        # Deform right side
        deform_func(s, x='if((y<1) and (x>=%s),%s,x)' % (size[0], size[0]),
                    y='if((y<1) and (x>=%s),x-%s,y)' % (size[0], size[0]))
    else:
        LCur, LLast = duplicate_L(s, LCur=LCur, LLast=LLast)
    translate(s, [0,0,-size[2]])
	
    # X sides
    LCur, LLast = plane(s, [size[0], size[2]], segmentsX=segmentsX, segmentsY=segmentsZ, LCur=LCur, LLast=LLast)
    rotate(s, 'x', 90)
    translate(s, [0,0,-size[2]])
    LCur, LLast = duplicate_L(s, LCur=LCur, LLast=LLast)
    translate(s, [0,size[1],0])
    
    # Y sides
    LCur, LLast = plane(s, [size[1], size[2]], segmentsX=segmentsY, segmentsY=segmentsZ, LCur=LCur, LLast=LLast)
    rotate(s, 'x', 90)
    rotate(s, 'z', 90)
    translate(s, [0,0,-size[2]])
    LCur, LLast = duplicate_L(s, LCur=LCur, LLast=LLast)
    translate(s, [size[0],0,0])
    
    LCur, LLast = join_L(s, LCur=LCur, LLast=LLast)
    merge_V(s, threshold=0.0001)
    fix_N(s)
    
    if not topZ:
        translate(s, [0,0,size[2]])
    if centerXY:
        translate(s, [-size[0]/2,-size[1]/2,0])
    elif center:
        translate(s, [-size[0]/2,-size[1]/2,size[2]/2])
    if color is not None:
        color_V(s, color=color)
    return LCur, LLast

def annulus_hires(s='MLTEMP_default.mlx', r=None, r1=None, r2=None, d=None,
            d1=None, d2=None, segmentsC=32, segmentsR=1, color=None, LCur=None, LLast=None):
    """Create a cylinder with user defined number of segments
    
    """
    if r is not None and d is None:
        if r1 is None and d1 is None:
            r1 = r
        if r2 is None and d2 is None:
            r2 = 0
    if d is not None:
        if r1 is None and d1 is None:
            r1 = d/2
        if r2 is None and d2 is None:
            r2 = 0
    if d1 is not None:
        r1 = d1/2
    if d2 is not None:
        r2 = d2/2
    if r1 is None:
        r1 = 1
    if r2 is None:
        r2 = 0
    ring = (r1 - r2)/segmentsR

    for i in range(0,segmentsR):
        LCur, LLast = annulus(s, r1=r1-i*ring, r2=r1-(i+1)*ring, segmentsC=segmentsC, LCur=LCur, LLast=LLast)
    LCur, LLast = join_L(s, merge_V=True, LCur=LCur, LLast=LLast)
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

def tube_hires(s='MLTEMP_default.mlx', h=1.0, r=None, r1=None, r2=None, d=None,
            d1=None, d2=None, segmentsC=32, segmentsR=1, segmentsH=1, center=False,
            simpleBottom=True, topZ=True,color=None, LCur=None, LLast=None):
    """Create a cylinder with user defined number of segments
    
    """

    # TODO: add option to round the top of the cylinder, i.e. deform spherically
    # TODO: add warnings if values are ignored
    if r is not None and d is None:
        if r1 is None and d1 is None:
            r1 = r
        if r2 is None and d2 is None:
            r2 = 0
    if d is not None:
        if r1 is None and d1 is None:
            r1 = d/2
        if r2 is None and d2 is None:
            r2 = 0
    if d1 is not None:
        r1 = d1/2
    if d2 is not None:
        r2 = d2/2
    if r1 is None:
        r1 = 1
    if r2 is None:
        r2 = 0
    
    LCur, LLast = annulus_hires(s, r1=r1, r2=r2, segmentsC=segmentsC, segmentsR=segmentsR, LCur=LCur, LLast=LLast)
    if simpleBottom:
        LCur, LLast = annulus(s, r1=r1, r2=r2, segmentsC=segmentsC, LCur=LCur, LLast=LLast)
    else:
        LCur, LLast = duplicate_L(s, LCur=LCur, LLast=LLast)
    translate(s, [0,0,-h])

    LCur, LLast = plane(s, [2*math.pi*r1, h], segmentsX=segmentsC, segmentsY=segmentsH, LCur=LCur, LLast=LLast)
    rotate(s, 'x', 90)
    translate(s, [math.pi*r1/2,0,-h])
    deform2cylinder(s, r1)
    if r2 != 0:
        LCur, LLast = plane(s, [2*math.pi*r2, h], segmentsX=segmentsC, segmentsY=segmentsH, LCur=LCur, LLast=LLast)
        rotate(s, 'x', 90)
        translate(s, [math.pi*r2/2,0,-h])
        deform2cylinder(s, r2)
    LCur, LLast = join_L(s, LCur=LCur, LLast=LLast)
    merge_V(s, threshold=0.0001)
    fix_N(s)
    if not topZ:
        translate(s, [0,0,h])
    if center:
        translate (s, [0, 0, h/2])
    if color is not None:
        color_V (s, color=color)
    return LCur, LLast

# TODO: create doublehelix function, takes spacing between helixes and rungs, rung diameter

### End Create ###


### Begin Sampling ###

def hausdorff_distance (s='MLTEMP_default.mlx', sampled_L=1, target_L=0,
                        save_sample=False, sample_V=True, sample_E=True,
                        sample_faux_E=False, sample_F=True, sample_num=1000,
                        maxdist=10, maxdist_max=100, LCur=None, LLast=None):
    """
    sampledLayer=1 # The mesh whose surface is sampled.
    For each sample we search the closest point on the Target Mesh.
    targetLayer=0 # The mesh that is sampled for the comparison.
    saveSample="false" # Save the position and distance of all the used
    samples on both the two surfaces, creating two new layers with two
    point clouds representing the used samples.
    sample_V="true" # For the search of maxima it is useful to sample
    vertices and edges of the mesh with a greater care. It is quite
    probable that the farthest points falls along edges or on mesh
    vertexes, and with uniform montecarlo sampling approaches the
    probability of taking a sample over a vertex or an edge is
    theoretically null. On the other hand this kind of sampling
    could make the overall sampling distribution slightly biased
    and slightly affects the cumulative results.
    sample_E="true" # See the above comment.
    sample_fauxE="false" # See the above comment.
    sample_F="true" # See the above comment.
    sample_num=1000 # The desired number of samples. It can be smaller or
    larger than the mesh size, and according to the chosen sampling strategy
    it will try to adapt. ML default: number of vertices in sampled mesh
    maxdist=10 # Sample points for which we do not find anything within
    this distance are rejected and not considered neither for averaging
    nor for max. ML default: 5% AABB[diag] of sampled mesh,
    max 100% AABB[diag] of sampled mesh
    """

    """
    Defaults:
      sample_num=num_V
      maxdist=0.05 * AABB['diag'] #5% of AABB[diag]
      maxdistmax=AABB['diag']
    """
    
    sf = open(s,'a')
    sf.write ('  <filter name="Hausdorff Distance">\n' +

              '    <Param name="SampledMesh" ' +
              'value="%d" ' % sampled_L +
              'description="Sampled Mesh" ' +
              'type="RichMesh" ' +
              'tooltip="The mesh whose surface is sampled. For each sample' +
              ' we search the closest point on the Target Mesh."/>\n' +

              '    <Param name="TargetMesh" ' +
              'value="%d" ' % target_L +
              'description="Target Mesh" ' +
              'type="RichMesh" ' +
              'tooltip="The mesh that is sampled for the comparison."/>\n' +

              '    <Param name="SaveSample" ' +
              'value="%s" ' % str(save_sample).lower() +
              'description="Save Samples" ' +
              'type="RichBool" ' +
              'tooltip="Save the position and distance of all the used' +
              ' samples on both the two surfaces, creating two new layers' +
              ' with two point clouds representing the used samples."/>\n' +

              '    <Param name="SampleVert" ' +
              'value="%s" ' % str(sample_V).lower() +
              'description="Sample Vertexes" ' +
              'type="RichBool" ' +
              'tooltip="For the search of maxima it is useful to sample' +
              ' vertices and edges of the mesh with a greater care. It is' +
              ' quite probably the the farthest points falls along edges' +
              ' or on mesh vertexes, and with uniform montecarlo sampling' +
              ' approachesthe probability of taking a sample over a vertex' +
              ' or an edge is theoretically null. On the other hand this' +
              ' kind of sampling could make the overall sampling' +
              ' distribution slightly biased and slightly affects the' +
              ' cumulative results."/>\n' +

              '    <Param name="SampleEdge" ' +
              'value="%s" ' % str(sample_E).lower() +
              'description="Sample Edges" ' +
              'type="RichBool" ' +
              'tooltip="See the above comment"/>\n' +

              '    <Param name="SampleFauxEdge" ' +
              'value="%s" ' % str(sample_faux_E).lower() +
              'description="Sample FauxEdge" ' +
              'type="RichBool" ' +
              'tooltip="See the above comment"/>\n' +

              '    <Param name="SampleFace" ' +
              'value="%s" ' % str(sample_F).lower() +
              'description="Sample Faces" ' +
              'type="RichBool" ' +
              'tooltip="See the above comment"/>\n' +

              '    <Param name="SampleNum" ' +
              'value="%d" ' % sample_num +
              'description="Number of samples" ' +
              'type="RichInt" ' +
              'tooltip="The desired number of samples. It can be smaller or' +
              ' larger than the mesh size, and according to the choosed' +
              ' sampling strategy it will try to adapt."/>\n' +

              '    <Param name="MaxDist" ' +
              'value="%s" ' % maxdist +
              'description="Max Distance" ' +
              'min="0" ' +
              'max="%s" ' % maxdist_max +
              'type="RichAbsPerc" ' +
              'tooltip="Sample points for which we do not find anything' +
              ' whithin this distance are rejected and not considered' +
              ' neither for averaging nor for max."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def sampling_poisson_disk (s='MLTEMP_default.mlx', sample_num=1000, radius=0,
              montecarlo_rate=20, save_montecarlo=False,
              approx_geodesic_dist=False, subsample=False, refine=False,
              refine_L=0, best_sample=True, best_sample_pool=10,
              exact_num=False, radius_variance=1, LCur=None, LLast=None):
    # NOTE: Poisson-disk sampling does not switch to the new sampling layer
    # after creation! Haven't tested other sampling filters yet
    sf = open(s,'a')
    sf.write ('  <filter name="Poisson-disk Sampling">\n' +

              '    <Param name="SampleNum" ' +
              'value="%d" ' % sample_num +
              'description="Number of samples" ' +
              'type="RichInt" ' +
              'tooltip="The desired number of samples. The ray of the disk' +
              ' is calculated according to the sampling density."/>\n' +

              '    <Param name="Radius" ' +
              'value="%s" ' % radius +
              'description="Explicit Radius" ' +
              'min="0" ' +
              'max="100" ' +
              'type="RichAbsPerc" ' +
              'tooltip="If not zero this parameter override the previous' +
              ' parameter to allow exact radius specification"/>\n' +

              '    <Param name="MontecarloRate" ' +
              'value="%d" ' % montecarlo_rate +
              'description="MonterCarlo OverSampling" ' +
              'type="RichInt" ' +
              'tooltip="The over-sampling rate that is used to generate' +
              ' the intial Montecarlo samples (e.g. if this parameter is' +
              ' _K_ means that _K_ x _poisson sample_ points will be' +
              ' used). The generated Poisson-disk samples are a subset of' +
              ' these initial Montecarlo samples. Larger this number slows' +
              ' the process but make it a bit more accurate."/>\n' +

              '    <Param name="SaveMontecarlo" ' +
              'value="%s" ' % str(save_montecarlo).lower() +
              'description="Save Montecarlo" ' +
              'type="RichBool" ' +
              'tooltip="If true, it will generate an additional Layer with' +
              ' the montecarlo sampling that was pruned to build the' +
              ' poisson distribution."/>\n' +

              '    <Param name="ApproximateGeodesicDistance" ' +
              'value="%s" ' % str(approx_geodesic_dist).lower() +
              'description="Approximate Geodesic Distance" ' +
              'type="RichBool" ' +
              'tooltip="If true Poisson Disc distances are computed using' +
              ' an approximate geodesic distance, e.g. an euclidean' +
              ' distance weighted by a function of the difference between' +
              ' the normals of the two points."/>\n' +

              '    <Param name="Subsample" ' +
              'value="%s" ' % str(subsample).lower() +
              'description="Base Mesh Subsampling" ' +
              'type="RichBool" ' +
              'tooltip="If true the original vertices of the base mesh are' +
              ' used as base set of points. In this case the SampleNum' +
              ' should be obviously much smaller than the original vertex' +
              ' number. Note that this option is very useful in the case' +
              ' you want to subsample a dense point cloud."/>\n' +

              '    <Param name="RefineFlag" ' +
              'value="%s" ' % str(refine).lower() +
              'description="Refine Existing Samples" ' +
              'type="RichBool" ' +
              'tooltip="If true the vertices of the below mesh are used as' +
              ' starting vertices, and they will utterly refined by adding' +
              ' more and more points until possible."/>\n' +

              '    <Param name="RefineMesh" ' +
              'value="%d" ' % refine_L +
              'description="Samples to be refined" ' +
              'type="RichMesh" ' +
              'tooltip="Used only if the above option is checked."/>\n' +

              '    <Param name="BestSampleFlag" ' +
              'value="%s" ' % str(best_sample).lower() +
              'description="Best Sample Heuristic" ' +
              'type="RichBool" ' +
              'tooltip="If true it will use a simple heuristic for choosing' +
              ' the samples. At a small cost (it can slow a bit the' +
              ' process) it usually improve the maximality of the generated' +
              ' sampling."/>\n' +

              '    <Param name="BestSamplePool" ' +
              'value="%d" ' % best_sample_pool +
              'description="Best Sample Pool Size" ' +
              'type="RichInt" ' +
              'tooltip="Used only if the Best Sample Flag is true. It' +
              ' controls the number of atMLTEMPts that it makes to get the' +
              ' best sample. It is reasonable that it is smaller than the' +
              ' Montecarlo oversampling factor."/>\n' +

              '    <Param name="ExactNumFlag" ' +
              'value="%s" ' % str(exact_num).lower() +
              'description="Exact number of samples" ' +
              'type="RichBool" ' +
              'tooltip="If requested it will try to do a dicotomic search' +
              ' for the best poisson disk radius that will generate the' +
              ' requested number of samples with a tolerance of the 0.5%.' +
              ' Obviously it takes much longer."/>\n' +

              '    <Param name="RadiusVariance" ' +
              'value="%s" ' % radius_variance +
              'description="Radius Variance" ' +
              'type="RichFloat" ' +
              'tooltip="The radius of the disk is allowed to vary between' +
              ' r and r*var. If this parameter is 1 the sampling is the' +
              ' same of the Poisson Disk Sampling"/>\n' +
              
              '  </filter>\n')
    sf.close ()
    return LCur, LLast

### End Sampling ###


### Begin Color ###

# TODO: test out using a function
def color_V (s='MLTEMP_default.mlx', r=255, g=255, b=255, a=255,
             color=None, LCur=None, LLast=None):
    """
    Color function using muparser lib to generate new RGBA color for every
    vertex. Red, Green, Blue and Alpha channels may be defined specifying
    a function in their respective fields.
    It's possible to use the following per-vertex variables in the
    expression:
      x,y,z (position),
      nx,ny,nz (normal),
      r,g,b,a (color),
      q (quality),
      rad (radius),
      vi (vertex index),
      vtu,vtv,ti (texture coords and texture index),
      vsel (is the vertex selected? 1 yes, 0 no)
      and all custom vertex attributes already defined by user.
    Function should produce values in the range 0-255
    """

    if color is not None:
        r, g, b = color_values(color)
    
    sf = open(s,'a')
    sf.write ('  <filter name="Per Vertex Color Function">\n' +

              '    <Param name="x" ' +
              'value="%s" ' % str(r).replace('<','&lt;') +
              'description="func r = " ' +
              'type="RichString" ' +
              'tooltip="Function to generate Red component. Expected Range' +
              ' 0-255"/>\n' +

              '    <Param name="y" ' +
              'value="%s" ' % str(g).replace('<','&lt;') +
              'description="func g = " ' +
              'type="RichString" ' +
              'tooltip="Function to generate Green component. Expected Range' +
              ' 0-255"/>\n' +

              '    <Param name="z" ' +
              'value="%s" ' % str(b).replace('<','&lt;') +
              'description="func b = " ' +
              'type="RichString" ' +
              'tooltip="Function to generate Blue component. Expected Range' +
              ' 0-255"/>\n' +

              '    <Param name="a" ' +
              'value="%s" ' % str(a).replace('<','&lt;') +
              'description="func alpha = " ' +
              'type="RichString" ' +
              'tooltip="Function to generate Alpha component. Expected Range' +
              ' 0-255"/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast


def color_V_voronoi(s='MLTEMP_default.mlx', target_L=0, source_L=1,
                     backward=True, LCur=None, LLast=None):
    sf = open(s,'a')
    sf.write ('  <filter name="Voronoi Vertex Coloring">\n' +

              '    <Param name="ColoredMesh" ' +
              'value="%d" ' % target_L +
              'description="To be Colored Mesh" ' +
              'type="RichMesh" ' +
              'tooltip="The mesh whose surface is colored. For each vertex' +
              ' of this mesh we decide the color according the below' +
              ' parameters."/>\n' +

              '    <Param name="VertexMesh" ' +
              'value="%d" ' % source_L +
              'description="Vertex Mesh" ' +
              'type="RichMesh" ' +
              'tooltip="The mesh whose vertexes are used as seed points for' +
              ' the color computation. These seeds point are projected onto' +
              ' the above mesh."/>\n' +

              '    <Param name="backward" ' +
              'value="%s" ' % str(backward).lower() +
              'description="BackDistance" ' +
              'type="RichBool" ' +
              'tooltip="If true the mesh is colored according the distance' +
              ' from the frontier of the voronoi diagram induced by the' +
              ' VertexMesh seeds."/>\n' +

              '  </filter>\n')
    sf.close ()
    return LCur, LLast

def color_V_cyclic_rainbow(s='MLTEMP_default.mlx', direction='sphere', center=[0,0,0], a=255/2, c=255/2, f=0.8, p=[0,2*math.pi/3,4*math.pi/3,0], alpha=False, LCur=None, LLast=None):
    """Color your mesh vertices in a repeating rainbow pattern
    direction = sphere, x, y, z, function
    center = center point of color function. For a sphere this is the center of the sphere.
    a = amplitude, between 0-255
    c = center, between 0-255
    f = frequency
    p = phase
    """
    center = check_list(center,3)
    a = check_list(a,4)
    c = check_list(c,4)
    f = check_list(f,4)
    p = check_list(p,4)

    if direction.lower() == 'sphere':
        increment = 'sqrt((x-%s)^2+(y-%s)^2+(z-%s)^2)' % (center[0], center[1], center[2])
    elif direction.lower() == 'x':
        increment = 'x - %s' % center[0]
    elif direction.lower() == 'y':
        increment = 'y - %s' % center[1]
    elif direction.lower() == 'z':
        increment = 'z - %s' % center[2]
    else:
        increment = direction
    
    funcRed = 'sin(%s*%s + %s)*%s + %s' % (f[0], increment, p[0], a[0], c[0])
    funcGreen = 'sin(%s*%s + %s)*%s + %s' % (f[1], increment, p[1], a[1], c[1])
    funcBlue = 'sin(%s*%s + %s)*%s + %s' % (f[2], increment, p[2], a[2], c[2])
    if alpha:
        funcAlpha = 'sin(%s*%s + %s)*%s + %s' % (f[3], increment, p[3], a[3], c[3])
    else:
        funcAlpha = 255
    
    color_V(s=s, r=funcRed, g=funcGreen, b=funcBlue, a=funcAlpha)
    return LCur, LLast

### End Color ###

""" Measurement functions """

def file_measure_AABB(fbasename=None, runlogname=None):
    """Measure the Axis Aligned Bounding Box of a mesh"""
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    if fext != 'xyz':
        fin, rc = run(o='MLTEMP_AABB.xyz', i=fbasename, runlogname=runlogname, s=None)
        fin = fin[0]
    else:
        fin = fbasename
    fread = open(fin, 'r')
    first = True
    for line in fread:
        x, y, z =  line.split()
        x = to_float(x)
        y = to_float(y)
        z = to_float(z)
        if first:
            AABB = {'min': [x, y, z], 'max': [x, y, z]}
            first = False
        if x < AABB['min'][0]: AABB['min'][0] = x
        if y < AABB['min'][1]: AABB['min'][1] = y
        if z < AABB['min'][2]: AABB['min'][2] = z
        if x > AABB['max'][0]: AABB['max'][0] = x
        if y > AABB['max'][1]: AABB['max'][1] = y
        if z > AABB['max'][2]: AABB['max'][2] = z
    fread.close()
    try:
        AABB['center'] = [(AABB['max'][0] + AABB['min'][0])/2, (AABB['max'][1] + AABB['min'][1])/2,
                    (AABB['max'][2] + AABB['min'][2])/2]
        AABB['size'] = [AABB['max'][0] - AABB['min'][0], AABB['max'][1] - AABB['min'][1],
                    AABB['max'][2] - AABB['min'][2]]
        AABB['diagonal'] = math.sqrt(AABB['size'][0]**2 + AABB['size'][1]**2 + AABB['size'][2]**2)
    except UnboundLocalError:
        print('Error: AABB input file does not contain valid data. Exiting ...')
        sys.exit(1)
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        #RUNLOG.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        RUNLOG.write('min = %s\n' % AABB['min'])
        RUNLOG.write('max = %s\n' % AABB['max'])
        RUNLOG.write('center = %s\n' % AABB['center'])
        RUNLOG.write('size = %s\n' % AABB['size'])
        RUNLOG.write('diagonal = %s\n' % AABB['diagonal'])
        RUNLOG.close()
    #print(AABB)
    return AABB

def file_polylinesort(fbasename=None, runlogname=None):
    """Sort separate line segments in obj format into a continous polyline or polylines.
    
    Also measures the length of each polyline
    
    Return polyline and polylineMeta (lengths)
    """
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    if fext != 'obj':
        print('Input file must be obj. Exiting ...')
        sys.exit(1)
    fread = open(fbasename, 'r')
    first = True
    polyline_vertices = []
    line_segments = []
    for line in fread:
        type, x, y, z =  line.split()
        if type == 'v':
            polyline_vertices.append([to_float(x), to_float(y), to_float(z)])
        elif type == 'l':
            line_segments.append([int(x), int(y)])  # x and y are really p1 and p2
        
        if first:
            AABB = {'min': [x, y, z], 'max': [x, y, z]}
            first = False
        if x < AABB['min'][0]: AABB['min'][0] = x
        if y < AABB['min'][1]: AABB['min'][1] = y
        if z < AABB['min'][2]: AABB['min'][2] = z
        if x > AABB['max'][0]: AABB['max'][0] = x
        if y > AABB['max'][1]: AABB['max'][1] = y
        if z > AABB['max'][2]: AABB['max'][2] = z
    fread.close()
    try:
        AABB['center'] = [(AABB['max'][0] + AABB['min'][0])/2, (AABB['max'][1] + AABB['min'][1])/2,
                    (AABB['max'][2] + AABB['min'][2])/2]
        AABB['size'] = [AABB['max'][0] - AABB['min'][0], AABB['max'][1] - AABB['min'][1],
                    AABB['max'][2] - AABB['min'][2]]
        AABB['diagonal'] = math.sqrt(AABB['size'][0]**2 + AABB['size'][1]**2 + AABB['size'][2]**2)
    except UnboundLocalError:
        print('Error: AABB input file does not contain valid data. Exiting ...')
        sys.exit(1)
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        #RUNLOG.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        RUNLOG.write('min = %s\n' % AABB['min'])
        RUNLOG.write('max = %s\n' % AABB['max'])
        RUNLOG.write('center = %s\n' % AABB['center'])
        RUNLOG.write('size = %s\n' % AABB['size'])
        RUNLOG.write('diagonal = %s\n' % AABB['diagonal'])
        RUNLOG.close()
    #print(AABB)
    return AABB

def file_measure_geometry(fbasename=None, runlogname=None):
    """Measures mesh geometry. Also runs measure_AABB"""
    s = 'MLTEMP_measure_geometry.mlx'
    log = 'MLTEMP_measure_geometry_log.txt'
    i = fbasename
    o = 'MLTEMP_AABB.xyz'

    begin(s, i)
    measure_geometry(s)
    end(s)
    run(runlogname, log=log, i=i, o=o, s=s)

    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        RUNLOG.close()
    AABB = measure_AABB(o, runlogname)

    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***Parsed Geometry Values for file "%s":\n' % fbasename)
        RUNLOG.close()
    geometry = parse_geometry(log, runlogname)
    return AABB, geometry
    
def file_measure_gAndT(fbasename=None, runlogname=None):
    """Measures mesh geometry, AABB and topology."""
    s = 'MLTEMP_measure_gAndT.mlx'
    log = 'MLTEMP_measure_gAndT_log.txt'
    i = fbasename
    o = 'MLTEMP_AABB.xyz'
    begin(s, i)
    measure_geometry(s)
    measure_topology(s)
    end(s)
    run(runlogname, log=log, i=i, o=o, s=s)
    
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***Axis Aligned Bounding Results for file "%s":\n' % fbasename)
        RUNLOG.close()
    AABB = measure_AABB(o, runlogname)
    
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***Parsed Geometry Values for file "%s":\n' % fbasename)
        RUNLOG.close()
    geometry = parse_geometry(log, runlogname)
    
    if runlogname is not None:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('***Parsed Topology Values for file "%s":\n' % fbasename)
        RUNLOG.close()
    topology = parse_topology(log, runlogname)
    return AABB, geometry, topology

def file_measure_dimension(fbasename=None, runlogname=None, axis1=None, offset1=0, 
                    axis2=None, offset2=0):
    """Measure a dimension of a mesh"""
    axis1 = axis1.lower()
    axis2 = axis2.lower()
    s = 'MLTEMP_measure_dimension.mlx'
    o = 'MLTEMP_measure_dimension.xyz'
    begin(s, fbasename)
    section(s, axis1, offset1, surface=True)
    section(s, axis2, offset2, surface=False)
    end(s)
    run(runlogname, i=fbasename, o=o, s=s)
    
    for a in ('x', 'y', 'z'):
        if a not in (axis1, axis2):
            axis = a
    axisNum = ord(axis) - ord('x')
    AABB = file_measure_AABB(o, runlogname)
    dimension = {'min': AABB['min'][axisNum], 'max': AABB['max'][axisNum],
        'length': AABB['size'][axisNum], 'axis': axis}
    if runlogname is None:
        print('\nFor file "%s"' % fbasename)
        print('Dimension parallel to %s with %s=%s & %s=%s:' % (axis, axis1, offset1,
        axis2, offset2))
        print('  Min = %s, Max = %s, Total length = %s' % (dimension['min'],
            dimension['max'], dimension['length']))
    else:
        RUNLOG = open(runlogname, 'a')
        RUNLOG.write('\nFor file "%s"\n' % fbasename)
        RUNLOG.write('Dimension parallel to %s with %s=%s & %s=%s:\n' % (axis, axis1, offset1,
        axis2, offset2))
        RUNLOG.write('min = %s\n' % dimension['min'])
        RUNLOG.write('max = %s\n' % dimension['max'])
        RUNLOG.write('Total length = %s\n' % dimension['length'])
        RUNLOG.close()
    return dimension

### Utility Functions ###
def is_number(n):
    try:
        float(n)
        return True
    except:
        return False

def to_float(n):
    try:
        float(n)
        return float(n)
    except ValueError:
        return float('NaN')

def delete_all (filename):
    """delete files in the current directory that match a pattern. Intended for temp files, e.g. mlx.delete('MLTEMP*')"""
    for f in glob(filename):
        os.remove(f)

def color_values (color):
    """Read color_names.txt and find the r, g ,b values for a named color."""
    # Get the directory where this script file is located:
    thisDir = os.path.dirname(os.path.realpath(inspect.getsourcefile(lambda:0)))
    colorNameFile = thisDir + os.sep + 'color_names.txt'
    found = False
    for line in open(colorNameFile, 'r'):
        line = line.rstrip()
        if color.lower() == line.split()[0]:
            hex = line.split()[1]
            r = line.split()[2]
            g = line.split()[3]
            b = line.split()[4]
            found = True
            break
    if not found:
        print('Color name "' + color + '" not found, using default (white)')
        r = 255
        g = 255
        b = 255
    return r, g, b

def check_list(var, terms):
    """Check if a variable is a list and is the correct length. If variable is not a list it will make it a list of the correct length with all terms identical."""
    if not isinstance(var, list):
        var = [var]
        for a in range(1,terms):
            var.append(var[0])
    if len(var) != terms:
        print('"%s" has the wrong number of terms; it needs %s. Exiting ...' % (var, terms))
        sys.exit(1)
    return var

