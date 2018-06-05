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
import inspect
import subprocess
import xml.etree.ElementTree as ET
import tempfile

from . import util
from . import layers
#from .layers import clean
from . import clean
from . import compute

# Global variables
ML_VERSION = '2016.12'
"""str: MeshLab version to target
"""

THIS_MODULEPATH = os.path.dirname(
    os.path.realpath(
        inspect.getsourcefile(
            lambda: 0)))

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

class FilterScript(object):
    """

    begin - need file names. Need these first to have correct layers; need to know however
    many we're importing!
    layers = list of mesh layers, with name as the entry
    file_in
    mlp_in


    begin code

    filters = actual text of filters. This is a list with each filter in a separate entry
    end code
    use self.meshes.[len(self.meshes)]
    use cur_layer, tot_layer in strings and replace at the end? Sounds way to complicated
    for now; just be sure to provide input files to start!

    add run method?

    """
    def __init__(self, file_in=None, mlp_in=None, file_out=None, ml_version=ML_VERSION):
        self.ml_version = ml_version # MeshLab version
        self.filters = []
        self.layer_stack = [-1] # set current layer to -1
        self.opening = ['<!DOCTYPE FilterScript>\n<FilterScript>\n']
        self.closing = ['</FilterScript>\n']
        self.__stl_layers = []
        self.file_in = file_in
        self.mlp_in = mlp_in
        self.__no_file_in = False
        self.file_out = file_out
        self.geometry = None
        self.topology = None
        self.hausdorff_distance = None
        self.parse_geometry = False
        self.parse_topology = False
        self.parse_hausdorff = False
        # Process input files
        # Process project files first

        # TODO: test to make sure this works with "bunny"; should work fine!
        if self.mlp_in is not None:
            # make a list if it isn't already
            self.mlp_in = util.make_list(self.mlp_in)
            for val in self.mlp_in:
                tree = ET.parse(val)
                #root = tree.getroot()
                for elem in tree.iter(tag='MLMesh'):
                    filename = (elem.attrib['filename'])
                    fext = os.path.splitext(filename)[1][1:].strip().lower()
                    label = (elem.attrib['label'])
                    # add new mesh to the end of the mesh stack
                    self.add_layer(label)
                    #self.layer_stack.insert(self.last_layer() + 1, label)
                    # change current mesh
                    self.set_current_layer(self.last_layer())
                    #self.layer_stack[self.last_layer() + 1] = self.last_layer()
                    # If the mesh file extension is stl, change to that layer and
                    # run clean.merge_vert
                    if fext == 'stl':
                        self.__stl_layers.append(self.current_layer())
        # Process separate input files next
        if self.file_in is not None:
            # make a list if it isn't already
            self.file_in = util.make_list(self.file_in)
            for val in self.file_in:
                fext = os.path.splitext(val)[1][1:].strip().lower()
                label = os.path.splitext(val)[0].strip() # file prefix
                #print('layer_stack = %s' % self.layer_stack)
                #print('last_layer = %s' % self.last_layer())
                #print('current_layer = %s' % self.current_layer())

                # add new mesh to the end of the mesh stack
                self.add_layer(label)
                #self.layer_stack.insert(self.last_layer() + 1, label)
                # change current mesh
                self.set_current_layer(self.last_layer())
                #self.layer_stack[self.last_layer() + 1] = self.last_layer()
                # If the mesh file extension is stl, change to that layer and
                # run clean.merge_vert
                if fext == 'stl':
                    self.__stl_layers.append(self.current_layer())
        # If some input files were stl, we need to change back to the last layer
        # If the mesh file extension is stl, change to that layer and
        # run clean.merge_vert
        if self.__stl_layers:
            for layer in self.__stl_layers:
                if layer != self.current_layer():
                    layers.change(self, layer)
                clean.merge_vert(self)
            layers.change(self, self.last_layer()) # Change back to the last layer
        elif self.last_layer() == -1:
            # If no input files are provided, create a dummy file
            # with a single vertex and delete it first in the script.
            # This works around the fact that meshlabserver will
            # not run without an input file.
            # Layer stack is modified here; temp file
            # is created during run
            self.__no_file_in = True
            self.add_layer('DELETE_ME')
            layers.delete(self)

    def last_layer(self):
        """ Returns the index number of the last layer """
        #print('last layer = %s' % (len(self.layer_stack) - 2))
        return len(self.layer_stack) - 2

    def current_layer(self):
        """ Returns the index number of the current layer """
        return self.layer_stack[len(self.layer_stack) - 1]

    def set_current_layer(self, layer_num):
        """ Set the current layer to layer_num """
        self.layer_stack[len(self.layer_stack) - 1] = layer_num
        return None

    def add_layer(self, label, change_layer=True):
        """ Add new mesh layer to the end of the stack

        Args:
            label (str): new label for the mesh layer
            change_layer (bool): change to the newly created layer
        """
        self.layer_stack.insert(self.last_layer() + 1, label)
        if change_layer:
            self.set_current_layer(self.last_layer())
        return None

    def del_layer(self, layer_num):
        """ Delete mesh layer """
        del self.layer_stack[layer_num]
        # Adjust current layer if needed
        if layer_num < self.current_layer():
            self.set_current_layer(self.current_layer() - 1)
        return None

    def save_to_file(self, script_file):
        """ Save filter script to an mlx file """
        # TODO: rasie exception here instead?
        if not self.filters:
            print('WARNING: no filters to save to file!')
        script_file_descriptor = open(script_file, 'w')
        script_file_descriptor.write(''.join(self.opening + self.filters + self.closing))
        script_file_descriptor.close()

    def run_script(self, log=None, ml_log=None, mlp_out=None, overwrite=False,
                   file_out=None, output_mask=None, script_file=None, print_meshlabserver_output=True):
        """ Run the script
        """

        temp_script = False
        temp_ml_log = False

        if self.__no_file_in:
            # If no input files are provided, create a dummy file
            # with a single vertex and delete it first in the script.
            # This works around the fact that meshlabserver will
            # not run without an input file.
            temp_file_in_file = tempfile.NamedTemporaryFile(delete=False, suffix='.xyz', dir=os.getcwd())
            temp_file_in_file.write(b'0 0 0')
            temp_file_in_file.close()
            self.file_in = [temp_file_in_file.name]

        if not self.filters:
            script_file = None
        elif script_file is None:
            # Create temporary script file
            temp_script = True
            temp_script_file = tempfile.NamedTemporaryFile(delete=False, suffix='.mlx')
            temp_script_file.close()
            self.save_to_file(temp_script_file.name)
            script_file = temp_script_file.name

        if (self.parse_geometry or self.parse_topology or self.parse_hausdorff) and (ml_log is None):
            # create temp ml_log
            temp_ml_log = True
            ml_log_file = tempfile.NamedTemporaryFile(delete=False, suffix='.txt')
            ml_log_file.close()
            ml_log = ml_log_file.name
        if file_out is None:
            file_out = self.file_out

        run(script=script_file, log=log, ml_log=ml_log,
            mlp_in=self.mlp_in, mlp_out=mlp_out, overwrite=overwrite,
            file_in=self.file_in, file_out=file_out, output_mask=output_mask, ml_version=self.ml_version,
            print_meshlabserver_output=print_meshlabserver_output)

        # Parse output
        # TODO: record which layer this is associated with?
        if self.parse_geometry:
            self.geometry = compute.parse_geometry(ml_log, log, print_output=print_meshlabserver_output)
        if self.parse_topology:
            self.topology = compute.parse_topology(ml_log, log, print_output=print_meshlabserver_output)
        if self.parse_hausdorff:
            self.hausdorff_distance = compute.parse_hausdorff(ml_log, log, print_output=print_meshlabserver_output)

        # Delete temp files
        if self.__no_file_in:
            os.remove(temp_file_in_file.name)
        if temp_script:
            os.remove(temp_script_file.name)
        if temp_ml_log:
            os.remove(ml_log_file.name)


def handle_error(program_name, cmd, log=None):
    """Subprocess program error handling

    Args:
        program_name (str): name of the subprocess program

    Returns:
        break_now (bool): indicate whether calling program should break out of loop

    """
    print('\nHouston, we have a problem.',
          '\n%s did not finish successfully. Review the log' % program_name,
          'file and the input file(s) to see what went wrong.')
    print('%s command: "%s"' % (program_name, cmd))
    if log is not None:
        print('log: "%s"' % log)
    print('Where do we go from here?')
    print(' r  - retry running %s (probably after' % program_name,
          'you\'ve fixed any problems with the input files)')
    print(' c  - continue on with the script (probably after',
          'you\'ve manually re-run and generated the desired',
          'output file(s)')
    print(' x  - exit, keeping the TEMP3D files and log')
    print(' xd - exit, deleting the TEMP3D files and log')
    while True:
        choice = input('Select r, c, x (default), or xd: ')
        if choice not in ('r', 'c', 'x', 'xd'):
            #print('Please enter a valid option.')
            choice = 'x'
        #else:
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
        break_now = True
    elif choice == 'r':
        print('Retrying %s cmd ...' % program_name)
        break_now = False
    return break_now


def run(script='TEMP3D_default.mlx', log=None, ml_log=None,
        mlp_in=None, mlp_out=None, overwrite=False, file_in=None,
        file_out=None, output_mask=None, cmd=None, ml_version=ML_VERSION,
        print_meshlabserver_output=True):
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
        print_meshlabserver_output (bool): Pass meshlabserver's output to stdout; useful for debugging.
                                           Only used if log is None.

    Notes:
        Meshlabserver can't handle spaces in paths or filenames (on Windows at least; haven't tested on other platforms). Enclosing the name in quotes or escaping the space has no effect.

    Returns:
        return code of meshlabserver process; 0 if successful
    """
    if cmd is None:
        cmd = 'meshlabserver'
        if ml_log is not None:
            # Initialize ml_log
            ml_log_file = open(ml_log, 'w')
            ml_log_file.close()
            cmd += ' -l %s' % ml_log
        if mlp_in is not None:
            # make a list if it isn't already
            mlp_in = util.make_list(mlp_in)
            for val in mlp_in:
                cmd += ' -p "%s"' % val
        if mlp_out is not None:
            cmd += ' -w %s' % mlp_out
            if overwrite:
                cmd += ' -v'
        if (mlp_in is None) and (file_in is None):
			# If no input files are provided use the default created by begin().
			# This works around the fact that meshlabserver will
			# not run without an input file.
            file_in = ['TEMP3D.xyz']
        if file_in is not None:
            # make a list if it isn't already
            file_in = util.make_list(file_in)
            for val in file_in:
                if val == 'bunny':
                    cmd += ' -i "%s"' % os.path.join(THIS_MODULEPATH, os.pardir,
                                                     'models', 'bunny_flat(1Z).ply')
                elif val == 'bunny_raw':
                    cmd += ' -i "%s"' % os.path.join(THIS_MODULEPATH, os.pardir,
                                                     'models', 'bunny_raw(-1250Y).ply')
                else:
                    cmd += ' -i "%s"' % val
        if file_out is not None:
            # make a list if it isn't already
            file_out = util.make_list(file_out)
            if output_mask is not None:
                output_mask = util.make_list(output_mask)
            else:
                output_mask = []
            for index, val in enumerate(file_out):
                cmd += ' -o "%s"' % val
                try:
                    cmd += ' %s' % output_mask[index]
                except IndexError:  # If output_mask can't be found use defaults
                    cmd += ' %s' % default_output_mask(val, ml_version=ml_version)
        if script is not None:
            cmd += ' -s "%s"' % script
    if log is not None:
        log_file = open(log, 'a')
        log_file.write('meshlabserver cmd = %s\n' % cmd)
        log_file.write('***START OF MESHLAB STDOUT & STDERR***\n')
        log_file.close()
        log_file = open(log, 'a')
    else:
        if print_meshlabserver_output:
            log_file = None
            print('meshlabserver cmd = %s' % cmd)
            print('***START OF MESHLAB STDOUT & STDERR***')
        else:
            log_file = open(os.devnull, 'w')
    while True:
        # TODO: test if shell=True is really needed
        return_code = subprocess.call(cmd, shell=True,
                                      stdout=log_file, stderr=log_file,
                                      universal_newlines=True)
        if log is not None:
            log_file.close()
        if (return_code == 0) or handle_error(program_name='MeshLab', cmd=cmd, log=log):
            break
    if log is not None:
        log_file = open(log, 'a')
        log_file.write('***END OF MESHLAB STDOUT & STDERR***\n')
        log_file.write('meshlabserver return code = %s\n\n' % return_code)
        log_file.close()
    return return_code


def find_texture_files(fbasename, log=None):
    """Finds the filenames of the referenced texture file(s) (and material
    file for obj) for the mesh.

    Args:
        fbasename (str): input filename. Supported file extensions:
            obj
            ply
            dae
            x3d
            wrl
        log (str): filename to log output

    Returns:
        list: list of all of the texture filenames referenced by the input file.
            May contain duplicates if the texture files are referenced more
            than once. List is empty if no texture files are found.
        list: list of all of the unique texture filenames, also empty if no
            texture files are found.
        str: for obj files only, returns the name of the referenced material file.
            Returns None if no material file is found.

    """
    fext = os.path.splitext(fbasename)[1][1:].strip().lower()
    material_file = None
    texture_files = []
    vert_colors = False
    face_colors = False
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
        face_element = False
        with open(fbasename, 'rb') as fread:
            # read ascii header; works for both ascii & binary files
            while True:
                line = fread.readline().strip().decode('ascii')
                # print(line)
                if 'element face' in line:
                    face_element = True
                if 'red' in line:
                    if face_element:
                        face_colors = True
                    else:
                        vert_colors = True
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
    elif fext != 'stl':  # add other formats that don't support texture, e.g. xyz?
        print('File extension %s is not currently supported' % fext)
        # TODO: raise exception here
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
        log_file.write('vertex colors = %s\n' % vert_colors)
        log_file.write('face colors = %s\n' % face_colors)
        log_file.close()
    colors = {'texture':bool(texture_files), 'vert_colors':vert_colors, 'face_colors':face_colors}
    return texture_files, texture_files_unique, material_file, colors


def default_output_mask(file_out, texture=True, vert_normals=True, vert_colors=False,
                        face_colors=False, ml_version=ML_VERSION):
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
    vn = ''
    wt = ''
    vc = ''
    fc = ''

    if ml_version < '1.3.4':
        om = '-om'
    else:
        om = '-m'

    fext = os.path.splitext(file_out)[1][1:].strip().lower()
    if fext in ['stl', 'dxf', 'xyz']:
        om = ''
        texture = False
        vert_normals = False
        vert_colors = False
        face_colors = False
#    elif fext == 'ply':
#        vert_colors = True

    if vert_normals:
        vn = ' vn'
    if texture:
        wt = ' wt'
    if vert_colors:
        vc = ' vc'
    if face_colors:
        fc = ' fc'
    output_mask = '{}{}{}{}{}'.format(om, vn, wt, vc, fc)
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
        # with a single vertex and delete it first in the script.
        # This works around the fact that meshlabserver will
        # not run without an input file.
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


def create_mlp(file_out, mlp_mesh=None, mlp_raster=None):
    """ Create mlp file
    mlp_mesh (list containing dictionary)
        filename*
        label
        matrix

    mlp_raster
        filename*
        label
        semantic
        camera
            trans_vector*
            rotation_matrix*
            focal_length*
            image_px*
            image_res_mm_per_px*
            lens_distortion
            center_px
    * Required

    http://vcg.isti.cnr.it/~cignoni/newvcglib/html/shot.html
    """
    # Opening lines
    mlp_file = open(file_out, 'w')
    mlp_file.write('\n'.join([
        '<!DOCTYPE MeshLabDocument>',
        '<MeshLabProject>\n']))
    mlp_file.close()

    if mlp_mesh is not None:
        mlp_file = open(file_out, 'a')
        mlp_file.write(' <MeshGroup>\n')
        for i, val in enumerate(mlp_mesh):
            if 'label' not in mlp_mesh[i]:
                mlp_mesh[i]['label'] = mlp_mesh[i]['filename']
            if 'matrix' not in mlp_mesh[i]:
                mlp_mesh[i]['matrix'] = [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]]
            mlp_file.write('  <MLMesh filename="{}" label="{}">\n'.format(mlp_mesh[i]['filename'], mlp_mesh[i]['label']))
            mlp_file.write('\n'.join([
                '   <MLMatrix44>',
                '{m[0]} {m[1]} {m[2]} {m[3]} '.format(m=mlp_mesh[i]['matrix'][0]),
                '{m[0]} {m[1]} {m[2]} {m[3]} '.format(m=mlp_mesh[i]['matrix'][1]),
                '{m[0]} {m[1]} {m[2]} {m[3]} '.format(m=mlp_mesh[i]['matrix'][2]),
                '{m[0]} {m[1]} {m[2]} {m[3]} '.format(m=mlp_mesh[i]['matrix'][3]),
                '</MLMatrix44>',
                '  </MLMesh>\n']))
        mlp_file.write(' </MeshGroup>\n')
        mlp_file.close()
        # print(mlp_mesh)
    else:
        mlp_file = open(file_out, 'a')
        mlp_file.write(' <MeshGroup/>\n')
        mlp_file.close()
    if mlp_raster is not None:
        mlp_file = open(file_out, 'a')
        mlp_file.write(' <RasterGroup>\n')
        for i, val in enumerate(mlp_raster):
            if 'label' not in mlp_raster[i]:
                mlp_raster[i]['label'] = mlp_raster[i]['filename']
            if 'semantic' not in mlp_raster[i]:
                mlp_raster[i]['semantic'] = 1
            if 'lens_distortion' not in mlp_raster[i]['camera']:
                mlp_raster[i]['camera']['lens_distortion'] = [0, 0]
            if 'center_px' not in mlp_raster[i]['camera']:
                mlp_raster[i]['camera']['center_px'] = [int(mlp_raster[i]['camera']['image_px'][0]/2), int(mlp_raster[i]['camera']['image_px'][1]/2)]

            mlp_file.write('  <MLRaster label="{}">\n'.format(mlp_raster[i]['label']))

            mlp_file.write(' '.join([
                '   <VCGCamera',
                'TranslationVector="{m[0]} {m[1]} {m[2]} {m[3]}"'.format(m=mlp_raster[i]['camera']['trans_vector']),
                'RotationMatrix="{m[0][0]} {m[0][1]} {m[0][2]} {m[0][3]} {m[1][0]} {m[1][1]} {m[1][2]} {m[1][3]} {m[2][0]} {m[2][1]} {m[2][2]} {m[2][3]} {m[3][0]} {m[3][1]} {m[3][2]} {m[3][3]} "'.format(m=mlp_raster[i]['camera']['rotation_matrix']),
                'FocalMm="{}"'.format(mlp_raster[i]['camera']['focal_length']),
                'ViewportPx="{m[0]} {m[1]}"'.format(m=mlp_raster[i]['camera']['image_px']),
                'PixelSizeMm="{m[0]} {m[1]}"'.format(m=mlp_raster[i]['camera']['image_res_mm_per_px']),
                'LensDistortion="{m[0]} {m[1]}"'.format(m=mlp_raster[i]['camera']['lens_distortion']),
                'CenterPx="{m[0]} {m[1]}"'.format(m=mlp_raster[i]['camera']['center_px']),
                '/>\n']))
            mlp_file.write('   <Plane semantic="{}" fileName="{}"/>\n'.format(mlp_raster[i]['semantic'], mlp_raster[i]['filename']))
            mlp_file.write(' </MLRaster>\n')
        mlp_file.write(' </RasterGroup>\n')
        mlp_file.close()
        # print(mlp_raster)
    else:
        mlp_file = open(file_out, 'a')
        mlp_file.write(' <RasterGroup/>\n')
        mlp_file.close()

    # Closing lines
    mlp_file = open(file_out, 'a')
    mlp_file.write('</MeshLabProject>\n')
    mlp_file.close()
    return
