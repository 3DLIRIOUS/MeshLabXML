""" MeshLabXML utility functions """

import os
import sys
import inspect
from glob import glob


def is_number(num):
    try:
        float(num)
        return True
    except:
        return False


def to_float(num):
    try:
        float(num)
        return float(num)
    except ValueError:
        return float('NaN')


def delete_all(filename):
    """delete files in the current directory that match a pattern.
    
    Intended for temp files, e.g. mlx.delete('TEMP3D*').
    
    """
    for fread in glob(filename):
        os.remove(fread)


def color_values(color):
    """Read color_names.txt and find the red, green, and blue values
    for a named color."""
    # Get the directory where this script file is located:
    this_dir = os.path.dirname(
        os.path.realpath(
            inspect.getsourcefile(
                lambda: 0)))
    color_name_file = os.path.join(this_dir, 'color_names.txt')
    found = False
    for line in open(color_name_file, 'r'):
        line = line.rstrip()
        if color.lower() == line.split()[0]:
            #hex_color = line.split()[1]
            red = line.split()[2]
            green = line.split()[3]
            blue = line.split()[4]
            found = True
            break
    if not found:
        print('Color name "%s" not found, using default (white)' % color)
        red = 255
        green = 255
        blue = 255
    return red, green, blue


def check_list(var, num_terms):
    """Check if a variable is a list and is the correct length. If variable is not a list it will make it a list of the correct length with all terms identical."""
    if not isinstance(var, list):
        if isinstance(var, tuple):
            var = list(var)
        else:
            var = [var]
        for _ in range(1, num_terms):
            var.append(var[0])
    if len(var) != num_terms:
        print(
            '"%s" has the wrong number of terms; it needs %s. Exiting ...' %
            (var, num_terms))
        sys.exit(1)
    return var


def make_list(var, num_terms):
    """Check if a variable is a list and is the correct length. If variable is not a list it will make it a list of the correct length with all terms identical."""
    if not isinstance(var, list):
        if isinstance(var, tuple):
            var = list(var)
        else:
            var = [var]
    if len(var) == 1:
        for _ in range(1, num_terms):
            var.append(var[0])
    return var
