#!/usr/bin/python3
"""Create and run MeshLab XML scripts

License:
    Copyright (C) 2016 Tim Ayres

    This program is free software; you can redistribute it and/or
    modify it under the terms of the GNU Lesser General Public
    License as published by the Free Software Foundation; either
    version 2.1 of the License, or (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
    Lesser General Public License for more details.

    You should have received a copy of the GNU Lesser General Public
    License along with this program; if not, write to the Free Software
    Foundation, Inc., 51 Franklin Street, Fifth Floor, Boston, MA  02110-1301  USA
"""

import os
import sys
import subprocess
import xml.etree.ElementTree as ET

from . import util
from . import layers
from . import clean

ML_VERSION = '1.3.4Beta'
"""str: MeshLab version to target

Currently only affects output mask flag
"""

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


def run(log=None, ml_log=None,
        mlp_in=None, mlp_out=None, overwrite=False,
        file_in=None, file_out=None, output_mask=None,
        script='TEMP3D_default.mlx', cmd=None):
    """Run meshlabserver in a subprocess.

    Args:
        log (str): filename of the log file for meshlabxml. If not
            None, all meshlabserver stdout and stderr messages
            will be appended to this file.
        ml_log (str): filename of the log file output directly by
            meshlabserver.
        mlp_in (str or list): input meshlab project file. Can be a
            single filename or a list of filenames. Filenames will
            be loaded in the order given. All project files will
            be loaded before individual input files. If you want
            to load project and input files in a different order
            then you should use a custom cmd.
        mlp_out (str): output meshlab project file. Specify a
            single filename (meshlabserver accepts multiple output
            project filenames, however they will all be identical,
            so there is little use). When this option is used all
            layers will be saved as ply files.
        overwrite (bool): when specifying mlp_out, this determines
            whether any existing files will be overwritten (if
            True) or new filenames created (if False). If a new
            project file is created meshes will have '_out' added
            to their name.
        file_in (str or list): input mesh filename. Can be a single
            filename or a list of filenames. Filenames will be
            loaded in the order given. All project files will be
            loaded before individual input files. If you want to
            load project and input files in a different order then
            you should use a custom cmd.
        file_out (str or list): output mesh filename. Can be a
            single filename or a list of filenames. The current
            layer will be saved to this filename or filenames.
            Multiple filenames are useful for saving to multiple
            formats at the same time. Currently there is no way to
            output multiple layers except for saving a mlp project
            file.
        output_mask (str or list): output mask options for the
            output file. Values must include the flag, i.e. -m or
            -output_mask. If this is not provided for an output
            file then function "default_output_mask" is used to
            determine default values.
        script (str): the mlx filter script filename to execute.
        cmd (str): a full meshlabserver command line, such as
            "meshlabserver -input file.stl". If not None, this
            will override all other arguements except for log.

    Returns:
        return code of meshlabserver process; 0 if successful
    """
    if cmd is None:
        cmd = 'meshlabserver '
        if ml_log is not None:
            cmd += ' -l %s' % ml_log
        if mlp_in is not None:
            # make a list if it isn't already
            if not isinstance(mlp_in, list):
                mlp_in = [mlp_in]
            for val in mlp_in:
                cmd += ' -p %s' % val
        if mlp_out is not None:
            cmd += ' -w %s' % mlp_out
            if overwrite:
                cmd += ' -v'
        if (mlp_in is None) and (file_in is None):
            file_in = ['TEMP3D.xyz']
        if file_in is not None:
            # make a list if it isn't already
            if not isinstance(file_in, list):
                file_in = [file_in]
            for val in file_in:
                cmd += ' -i %s' % val
        if file_out is not None:
            # make a list if it isn't already
            if not isinstance(file_out, list):
                file_out = [file_out]
            if output_mask is not None:
                if not isinstance(output_mask, list):
                    output_mask = [output_mask]
            else:
                output_mask = []
            for index, val in enumerate(file_out):
                cmd += ' -o %s' % val
                try:
                    cmd += ' %s' % output_mask[index]
                except IndexError:  # If output_mask can't be found use defaults
                    cmd += default_output_mask(val)
        if script is not None:
            cmd += ' -s %s' % script
    if log is not None:
        log_file = open(log, 'a')
        log_file.write('meshlabserver cmd = %s\n' % cmd)
        log_file.write('***START OF MESHLAB STDOUT & STDERR***\n')
        log_file.close()
        log_file = open(log, 'a')
    else:
        log_file = None
        print('meshlabserver cmd = %s' % cmd)
        print('***START OF MESHLAB STDOUT & STDERR***')
    while True:
        # TODO: test if shell=True is really needed
        return_code = subprocess.call(cmd, shell=True,
                                      stdout=log_file, stderr=log_file,
                                      universal_newlines=True)
        if log is not None:
            log_file.close()

        if return_code == 0:
            break
        else:
            print('Houston, we have a problem.')
            print('MeshLab did not finish sucessfully. Review the log',
                  'file and the input file(s) to see what went wrong.')
            print('MeshLab command: "%s"' % cmd)
            print('log: "%s"' % log)
            print('Where do we go from here?')
            print(' r  - retry running meshlabserver (probably after',
                  'you\'ve fixed any problems with the input files)')
            print(' c  - continue on with the script (probably after',
                  'you\'ve manually re-run and generated the desired',
                  'output file(s)')
            print(' x  - exit, keeping the TEMP3D files and log')
            print(' xd - exit, deleting the TEMP3D files and log')
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
                print('Deleting TEMP3D* and log files and exiting ...')
                util.delete_all('TEMP3D*')
                if log is not None:
                    os.remove(log)
                sys.exit(1)
            elif choice == 'c':
                print('Continuing on ...')
                break
            elif choice == 'r':
                print('Retrying meshlabserver cmd ...')
    if log is not None:
        log_file = open(log, 'a')
        log_file.write('***END OF MESHLAB STDOUT & STDERR***\n')
        log_file.write('meshlabserver return code = %s\n\n' % return_code)
        log_file.close()
    return return_code


def find_texture_files(fbasename, log=None):
    """Finds the filenames of the associated texture file(s) (and material
    file for obj) for the mesh."""
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    material_file = None
    texture_files = []
    if fext == 'obj':
        # Material Format: mtllib ./model_mesh.obj.mtl
        with open(fbasename, 'r') as fread:
            for line in fread:
                if 'mtllib' in line:
                    material_file = os.path.basename(line.split()[1])
                    break
        if material_file is not None:
            # Texture Format: map_Kd model_texture.jpg
            with open(material_file, 'r') as fread:
                for line in fread:
                    if 'map_Kd' in line:
                        texture_files.append(os.path.basename(line.split()[1]))
    elif fext == 'ply':
        # Texture Format: comment TextureFile model_texture.jpg
        # This works for MeshLab & itSeez3D, but may not work for
        # every ply file.
        with open(fbasename, 'rb') as fread:
            # read ascii header; works for both ascii & binary files
            while True:
                line = fread.readline().strip().decode('ascii')
                # print(line)
                if 'TextureFile' in line:
                    texture_files.append(os.path.basename(line.split()[2]))
                if 'end_header' in line:
                    break
    elif fext == 'dae':  # COLLADA
        # elif fext == 'mlp':
        # Texture Format:   <image id="texture0" name="texture0">
        #               <init_from>model_texture.jpg</init_from>
        #           </image>
        namespace = 'http://www.collada.org/2005/11/COLLADASchema'
        tree = ET.parse(fbasename)
        #root = tree.getroot()
        #print('root = ', root)
        #print('root.tag = ', root.tag, 'root.attrib = ', root.attrib)
        for elem in tree.findall(
                '{%s}library_images/{%s}image/{%s}init_from' % (namespace, namespace, namespace)):
            texture_files.append(elem.text)
    elif fext == 'x3d':
        # Texture Format: <ImageTexture url="model_texture.jpg"/>
        #ns = 'http://www.w3.org/2001/XMLSchema-instance'
        tree = ET.parse(fbasename)
        #root = tree.getroot()
        #print('root = ', root)
        #print('root.tag = ', root.tag, 'root.attrib = ', root.attrib)
        # for elem in root:
        # for elem in tree.iter(): # iterate through tree; very useful to see possible tags
        #print('elem.tag = ', elem.tag)
        #print('elem.attrib = ', elem.attrib)
        for elem in tree.iter(tag='ImageTexture'):
            #print('elem.attrib = ', elem.attrib)
            texture_files.append(elem.attrib['url'])
    elif fext == 'wrl':
        # Texture Format: texture ImageTexture { url "model_texture.jpg" }
        with open(fbasename, 'r') as fread:
            for line in fread:
                if 'ImageTexture' in line:
                    texture_files.append(os.path.basename(line.split('"')[1]))
                    break
    elif fext != 'stl':  # add other formats that don't support teture, e.g. xyz?
        print('File extension %s is not currently supported' % fext)
    texture_files_unique = list(set(texture_files))
    if log is not None:
        log_file = open(log, 'a')
        log_file.write('Results of find_texture_files:\n')
        log_file.write('fbasename = %s\n' % fbasename)
        log_file.write('texture_files = %s\n' % texture_files)
        log_file.write('texture_files_unique = %s\n' % texture_files_unique)
        log_file.write('Number of texture files = %s\n' % len(texture_files))
        log_file.write(
            'Number of unique texture files = %s\n\n' %
            len(texture_files_unique))
        log_file.close()
    return texture_files, texture_files_unique, material_file


def default_output_mask(file_out, texture=True):
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
        om_flag = '-om'
    else:
        om_flag = '-m'

    fext = os.path.splitext(file_out)[1][1:].strip().lower()

    if fext == 'obj':
        if texture:
            output_mask = ' %s vc vn fc wt' % om_flag
        else:
            output_mask = ' %s vn' % om_flag
    elif fext == 'ply':
        if texture:
            output_mask = ' %s vc vn wt' % om_flag
        else:
            output_mask = ' %s vc vn' % om_flag  # with vertex colors
    elif fext == 'stl':
        output_mask = ''
    elif fext == 'dxf':
        output_mask = ''
    elif fext == 'xyz':
        output_mask = ''
    elif fext == 'x3d':
        if texture:
            output_mask = ' %s vc vn wt' % om_flag
        else:
            output_mask = ' %s vn' % om_flag
    elif fext == 'dae':  # COLLADA
        if texture:
            output_mask = ' %s vc vn wt' % om_flag
        else:
            output_mask = ' %s vn' % om_flag
    else:
        print('Default output mask for file extension "%s"' % fext,
              'is not currently supported')
    return output_mask


def begin(script='TEMP3D_default.mlx', file_in=None, mlp_in=None):
    """Create new mlx script and write opening tags.

    Performs special processing on stl files.

    If no input files are provided this will create a dummy
    file and delete it as the first filter. This works around
    the meshlab limitation that it must be provided an input
    file, even if you will be creating a mesh as the first
    filter.

    """
    script_file = open(script, 'w')
    script_file.write(''.join(['<!DOCTYPE FilterScript>\n',
                      '<FilterScript>\n']))
    script_file.close()

    current_layer = -1
    last_layer = -1
    stl = False

    # Process project files first
    if mlp_in is not None:
        # make a list if it isn't already
        if not isinstance(mlp_in, list):
            mlp_in = [mlp_in]
        for val in mlp_in:
            tree = ET.parse(val)
            #root = tree.getroot()
            for elem in tree.iter(tag='MLMesh'):
                filename = (elem.attrib['filename'])
                current_layer += 1
                last_layer += 1
                # If the mesh file extension is stl, change to that layer and
                # run clean.merge_vert
                if os.path.splitext(filename)[1][1:].strip().lower() == 'stl':
                    layers.change(script, current_layer)
                    clean.merge_vert(script)
                    stl = True

    # Process separate input files next
    if file_in is not None:
        # make a list if it isn't already
        if not isinstance(file_in, list):
            file_in = [file_in]
        for val in file_in:
            current_layer += 1
            last_layer += 1
            # If the mesh file extension is stl, change to that layer and
            # run clean.merge_vert
            if os.path.splitext(val)[1][1:].strip().lower() == 'stl':
                layers.change(script, current_layer)
                clean.merge_vert(script)
                stl = True

    # If some input files were stl, we need to change back to the last layer
    if stl:
        layers.change(script, last_layer)  # Change back to the last layer
    elif last_layer == -1:
        # If no input files are provided, create a dummy file
        # with a single vertex and delete it first in the script
        file_in = ['TEMP3D.xyz']
        file_in_descriptor = open(file_in[0], 'w')
        file_in_descriptor.write('0 0 0')
        file_in_descriptor.close()
        layers.delete(script)
    return current_layer, last_layer


def end(script='TEMP3D_default.mlx'):
    """Write the closing tag to mlx script."""
    script_file = open(script, 'a')
    script_file.write('</FilterScript>')
    script_file.close()
