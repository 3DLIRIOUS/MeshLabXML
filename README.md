![mlx_logo](https://user-images.githubusercontent.com/15272764/30234183-88b1588e-94c0-11e7-9cce-6252e3c39237.png)


MLX, or **M**esh**L**ab**X**ML, is a Python (2.7 or 3) scripting interface to [MeshLab](http://www.meshlab.net/), the open source system for processing and editing 3D triangular meshes. 

Under the hood, MLX generates XML filter scripts that can then be executed headless with the meshlabserver executable or run in the MeshLab GUI. It can also parse some of MeshLab's output, such as the results of the measure_geometry and measure_topology functions.

MLX is named after the .mlx file extension for MeshLab script files, however the name was already taken on PyPi (for an unrelated machine learning library), so it is formally registered under the longer name of MeshLabXML.

## Installation

MLX can be installed via [PyPI](https://pypi.org/project/MeshLabXML/) and pip:

    pip install meshlabxml

The released PyPI version may lag behind this git repository somewhat, so install from git if you want the latest and greatest. MLX may also be installed and run in other Python environments, such as [Blender](https://www.blender.org/). Note that Blender does not come with pip by default, however it can be easily installed using [get-pip](https://bootstrap.pypa.io/get-pip.py).

##  Platforms & Versions

*Platforms:* MLX should work anywhere that MeshLab will run, including Windows, Mac & Linux, although it is only routinely tested on 64 bit Windows.

*Python:* MLX should work under Python 2.7 and 3.x, although it is only routinely tested on 64 bit >=3.5

*MeshLab:* MLX is known to work on MeshLab versions 1.34BETA (64 bit Windows only) and 2016.12. As of the time of this writing, not all functions have been tested with 2016.12 yet, so please open an issue if you find a bug.

*MLX version numbers:* PyPI releases are numbered by the year and month of release, e.g. 2017.9. A letter may be added on the end ("a", "b", "c", etc) if there is more than one release in a month.

## Filters & Functions

MLX contains a fairly large subset of the filters available in MeshLab. Additional filters will be added over time, generally on an "as I need them" basis. If you need a filter that is not yet incorporated, please open an issue.

Many of the functions below are a direct implementation of a MeshLab filter. Others are created from a combination of other functions, or implement new functionality using the [muparser](http://beltoforion.de/article.php?a=muparser) function filters.

Documentation for most filters is available by using "help" within a Python shell, although there are many that still need to be documented. In addition, in many cases the documentation is taken directly from the MeshLab filter, which is not always sufficient to understand the function if you are not already familiar with how it works.

*mlx* - functions to create and run scripts, determine inputs & outputs, etc.
 * FilterScript - Main class to create scripts
 * create_mlp
 * find_texture_files
 * default_output_mask
 * run

*mlx.create* - functions that create a new mesh
 * grid
 * cube
 * cube_hires
 * cube_open_hires
 * cylinder
 * cylinder_open_hires
 * tube_hires
 * icosphere
 * half_sphere_hires
 * sphere_cap
 * plane_hires_edges
 * annulus
 * annulus_hires
 * torus

*mlx.transform* - functions that transform, deform or morph mesh geometry
 * translate
 * translate2
 * rotate
 * rotate2
 * scale
 * scale2
 * freeze_matrix
 * function
 * function_cyl_co
 * wrap2cylinder
 * wrap2sphere
 * emboss_sphere
 * bend
 * deform2curve

*mlx.select* - functions that work with selections
 * all
 * none
 * invert
 * border
 * grow
 * shrink
 * self_intersecting_face
 * nonmanifold_vert
 * nonmanifold_edge
 * small_parts
 * vert_quality
 * face_function
 * vert_function
 * cylindrical_vert
 * spherical_vert

*mlx.delete* - functions that delete faces and/or vertices
 * nonmanifold_vert
 * nonmanifold_edge
 * small_parts
 * selected
 * faces_from_nonmanifold_edges
 * unreferenced_vert
 * duplicate_faces
 * duplicate_verts
 * zero_area_face

*mlx.clean* - functions to clean and repair a mesh
 * merge_vert
 * close_holes
 * split_vert_on_nonmanifold_face
 * fix_folded_face
 * snap_mismatched_borders

*mlx.layers* - functions that work with mesh layers
 * join
 * delete
 * rename
 * change
 * duplicate
 * split_parts

*mlx.normals* - functions that work with normals
 * reorient
 * flip
 * fix
 * point_sets

*mlx.remesh* - remeshing functions
 * simplify
 * uniform_resampling
 * hull
 * surface_poisson
 * surface_poisson_screened
 * curvature_flipping
 * voronoi

*mlx.sampling* - sampling functions
 * hausdorff_distance
 * poisson_disk
 * mesh_element
 * clustered_vert

*mlx.smooth* - smoothing functions
 * laplacian
 * hc_laplacian
 * taubin
 * twostep
 * depth

*mlx.subdivide* - subdivision functions
 * loop
 * ls3loop
 * midpoint
 * butterfly
 * catmull_clark

*mlx.texture* - functions that work with textures and UV mapping (parameterization)
 * flat_plane
 * per_triangle
 * voronoi
 * isometric
 * isometric_build_atlased_mesh
 * isometric_save
 * isometric_load
 * isometric_transfer
 * isometric_remesh
 * set_texture
 * project_rasters
 * param_texture_from_rasters
 * param_from_rasters

*mlx.transfer* - functions to transfer attributes
 * tex2vc
 * vc2tex
 * fc2vc
 * vc2fc
 * mesh2fc
 * vert_attr_2_meshes
 * vert_attr2tex_2_meshes
 * tex2vc_2_meshes

*mlx.compute* - functions that measure or perform a computation
 * section
 * measure_geometry
 * measure_topology
 * parse_geometry
 * parse_topology

*mlx.vert_color* - functions that work with vertex colors
 * function
 * voronoi
 * cyclic_rainbow

*mlx.mp_func* - functions to work with muparser filter functions, this is mostly a vector math library
 * muparser_ref
 * v_cross
 * v_dot
 * v_add
 * v_subtract
 * v_multiply
 * v_length
 * v_normalize
 * torus_knot
 * torus_knot_bbox
 * vert_attr
 * face_attr
 * vq_function
 * fq_function

*mlx.files* - functions that operate directly on files, usually to measure them
 * measure_aabb
 * measure_section
 * measure_geometry
 * measure_topology
 * measure_all
 * measure_dimension


## Possible Workflow

For production MLX can run completely headless, however while developing new scripts some visual feedback can be helpful.

MLX does not have an integrated GUI like OpenSCAD or Blender, however you can simulate one by arranging several programs into a useful layout, such as shown below. This can be accomplished pretty easily in modern versions of Windows using the Windows key and the arrow keys.

Generally you will want a text editor, a console and of course MeshLab itself. The general script development workflow may consist of the following steps
 1. Write & edit script in text editor
 2. Run script in console and view meshlabserver output
 3. Load output in MeshLab. Use the "reload" button to reload the mesh after any changes are made.
 4. Repeat ad nauseam

![workflow_2016 12](https://user-images.githubusercontent.com/15272764/30234194-9dd84f10-94c0-11e7-89a3-cd5d0acb598f.png)

## Examples

Some simple examples are shown below. These assume that the meshlabserver executable is in your path. If it is not already in your path, you can add it to your path in your script using something similar to the following:

    import os

    meshlabserver_path = 'C:\\Program Files\\VCG\\MeshLab'
    os.environ['PATH'] = meshlabserver_path + os.pathsep + os.environ['PATH']


Example #1: Create an orange cube and apply some transformations

    import meshlabxml as mlx

    orange_cube = mlx.FilterScript(file_out='orange_cube.ply', ml_version='2016.12')
    mlx.create.cube(orange_cube, size=[3.0, 4.0, 5.0], center=True, color='orange')
    mlx.transform.rotate(orange_cube, axis='x', angle=45)
    mlx.transform.rotate(orange_cube, axis='y', angle=45)
    mlx.transform.translate(orange_cube, value=[0, 5.0, 0])
    orange_cube.run_script()

  Output:

![orange_cube](https://user-images.githubusercontent.com/15272764/30234857-4214198c-94c7-11e7-80b4-e0d73ee60126.png)


Example #2: Measure the built-in Stanford Bunny test model and print the results

    import meshlabxml as mlx

    aabb, geometry, topology = mlx.files.measure_all('bunny', ml_version='2016.12')

  Output:

    max        = [103.817589, 87.032661, 191.203903]
    diagonal   = 310.4472554416525
    size       = [193.95133199999998, 149.001499, 191.203903]
    center     = [6.841923000000001, 12.531911500000003, 95.6019515]
    min        = [-90.133743, -61.968838, 0.0]
    volume_cm3                  = 1486.804
    inertia_tensor              = [[3170550016.0, -46370464.0, 987163904.0], [-46370464.0, 5072923136.0, -58690096.0], [987163904.0, -58690096.0, 3817212928.0]]
    area_cm2                    = 901.506875
    center_of_mass              = [1.747876, -2.226919, 64.788971]
    total_edge_length           = 179819.484375
    volume_mm3                  = 1486804.0
    principal_axes              = [[0.809736, 0.001188, -0.586793], [0.581329, 0.134539, 	0.802468], [-0.0799, 0.990908, -0.108251]]
    total_edge_length_incl_faux = 179819.484375
    area_mm2                    = 90150.6875
    axis_momenta                = [2455110656.0, 4522500608.0, 5083073024.0]
    genus            = 0
    manifold         = True
    non_manifold_E   = 0
    vert_num         = 32285
    boundry_edge_num = 0
    hole_num         = 0
    unref_vert_num   = 0
    edge_num         = 96849
    face_num         = 64566
    non_manifold_V   = 0
    part_num         = 1

Check out the "examples" directory for more complex examples.

## Logo

The MLX logo is a rainbow colored quatrefoil torus knot with Voronoi meshing. This model is created entirely using MLX; it's source code is included in the "examples" directory.  This is a moderately complex script that should give you an idea of some of the things that MLX can do; it makes heavy use of the powerful muparser functions.


## Tips

 * MeshLabServer can be a bit unstable, especially on certain filters such as mlx.remesh.uniform_resampling. If you have many filters to run, it is better to break the project up into smaller scripts and run problematic filters or sequences independently.
 * It is not currently possible to measure a mesh and use the results in the same script; you will need to measure the mesh and input the results into another instance. For example, if you want to simplify a mesh based on a percentage of the number of faces, you would first need to measure the number of faces with mlx.compute.measure_topology, then input the results into mlx.remesh.simplify.


## Status

MLX is still under heavy development and the API is not yet considered stable. Still, it is already quite useful, and is used for production purposes within our small company.

## License

MLX is released under [LGPL version 2.1](http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)

Example code is released into the public domain, except the quatrefoil logo, which is LGPL.

Any included models (such as the Stanford Bunny) are released under their own licenses.

Much of the documentation for the filter functions is taken directly from MeshLab, and is under the MeshLab license [GPL version 3](https://www.gnu.org/licenses/gpl-3.0-standalone.html)
