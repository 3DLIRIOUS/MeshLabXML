
# MeshLabXML

----
## Description

[MeshLab](http://meshlab.sourceforge.net/) is an excellent program for the processing and editing of unstructured 3D triangular meshes. MeshLab comes with a basic scripting ability whereby you provide a list of filters and parameters in XML format (file extension .mlx) that MeshLab can run either in the GUI or in headless mode (via the meshlabserver executable). MeshLab has the ability to record and save mlx scripts from the GUI, however generating mlx scripts from scratch is difficult.

**MeshLabXML** is a 3rd party library intended to fill this gap by providing a way to programmatically create and run MeshLab XML filter scripts using Python 3. In addition to running many of the built-in filters, MeshLabXML also contains additional functions and features, as well as work-arounds for some of MeshLab's bugs and idiosyncrasies.

MeshLabXML is currently written against MeshLab version 1.34BETA, which at the time of this writing (September 2016) is only available for 64 bit Windows. MeshLabXML may also work with older versions of MeshLab and on different platforms, however this has not been extensively tested and some features may not be available or work properly.

----
## Installation

MeshLabXML can be installed via PyPI and pip:

    pip --install meshlabxml

----
## Examples

Example #1: Create an orange cube and apply some transformations

    import os
    import meshlabxml as mlx

    # Add meshlabserver directory to OS PATH; omit this if it is already in
    # your PATH
    MESHLABSERVER_PATH = 'C:\\Program Files\\VCG\\MeshLab'
    os.environ['PATH'] += os.pathsep + MESHLABSERVER_PATH

    script = 'orange_cube.mlx' # script file
    model = 'orange_cube.ply' # output file
    log = 'orange_cube_log.txt' # log file

    mlx.begin(script=script) # Start writing the script to the script file
    mlx.create.cube(script=script, size=[3.0, 3.0, 2.0], center=True, color='orange')
    mlx.transform.rotate(script=script, axis='x', angle=45)
    mlx.transform.translate(script=script, value=[5.0, 0, 0])
    mlx.end(script=script) # Finish writing the script to the script file

    mlx.run(script=script, log=log, file_out=model) # Run the script using meshlabserver and output the result
    mlx.util.delete_all('TEMP3D*') # Delete temp files


Example #2: Measure the built-in Stanford Bunny test model and print the results

    import os
    import meshlabxml as mlx

    # Add meshlabserver directory to OS PATH; omit this if it is already in
    # your PATH
    MESHLABSERVER_PATH = 'C:\\Program Files\\VCG\\MeshLab'
    os.environ['PATH'] += os.pathsep + MESHLABSERVER_PATH

    aabb, geometry, topology = mlx.files.measure_all('bunny')

Check out the "examples" directory for more complex examples.

----
## Status

MeshLabXML is still under heavy development and the API is not yet considered stable.

* Many filters have not yet been implemented. Filters are generally added "as I need them". If you have a need for a specific filter, please open an issue requesting that it be added.

* Documentation is still lacking or incomplete in many areas. For the MeshLab built-in functions, usage is typically the same or similar to MeshLab.

----
## License

MeshLabXML is released under [LGPL version 2.1](http://www.gnu.org/licenses/old-licenses/lgpl-2.1.en.html)

Example code is released into the public domain.

Any included models (such as the Stanford Bunny) are released under their own licenses.
