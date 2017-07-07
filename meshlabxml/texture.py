""" MeshLabXML texture functions """

from . import util


def flat_plane(script, plane=0, aspect_ratio=False):
    """Flat plane parameterization

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Parametrization: Flat Plane ">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="projectionPlane"',
        'value="%d"' % plane,
        'description="Projection plane"',
        'enum_val0="XY"',
        'enum_val1="XZ"',
        'enum_val2="YZ"',
        'enum_cardinality="3"',
        'type="RichEnum"',
        'tooltip="Choose the projection plane"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="aspectRatio"',
        'value="%s"' % str(aspect_ratio).lower(),
        'description="Preserve Ratio"',
        'type="RichBool"',
        'tooltip="If checked the resulting parametrization will preserve the original apsect ratio of the model otherwise it will fill up the whole 0..1 uv space"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def per_triangle(script, sidedim=0, textdim=1024, border=2, method=1):
    """Trivial Per-Triangle parameterization

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Parametrization: Trivial Per-Triangle ">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="sidedim"',
        'value="%d"' % sidedim,
        'description="Quads per line"',
        'type="RichInt"',
        'tooltip="Indicates how many triangles have to be put on each line (every quad contains two triangles). Leave 0 for automatic calculation"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textdim"',
        'value="%d"' % textdim,
        'description="Texture Dimension (px)"',
        'type="RichInt"',
        'tooltip="Gives an indication on how big the texture is"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="border"',
        'value="%d"' % border,
        'description="Inter-Triangle border (px)"',
        'type="RichInt"',
        'tooltip="Specifies how many pixels to be left between triangles in parametrization domain"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="method"',
        'value="%d"' % method,
        'description="Method"',
        'enum_val0="Basic"',
        'enum_val1="Space-optimizing"',
        'enum_cardinality="2"',
        'type="RichEnum"',
        'tooltip="Choose space optimizing to map smaller faces into smaller triangles in parametrizazion domain"'
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def voronoi(script, region_num=10, overlap=False):
    """Voronoi Atlas parameterization

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Parametrization: Voronoi Atlas">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="regionNum"',
        'value="%d"' % region_num,
        'description="Approx. Region Num"',
        'type="RichInt"',
        'tooltip="An estimation of the number of regions that must be generated. Smaller regions could lead to parametrizations with smaller distortion."',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="overlapFlag"',
        'value="%s"' % str(overlap).lower(),
        'description="Overlap"',
        'type="RichBool"',
        'tooltip="If checked the resulting parametrization will be composed by overlapping regions, e.g. the resulting mesh will have duplicated faces: each region will have a ring of ovelapping duplicate faces that will ensure that border regions will be parametrized in the atlas twice. This is quite useful for building mipmap robust atlases"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric(script, targetAbstractMinFaceNum=140, targetAbstractMaxFaceNum=180,
              stopCriteria=1, convergenceSpeed=1, DoubleStep=True):
    """Isometric parameterization

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="targetAbstractMinFaceNum"',
        'value="%d"' % targetAbstractMinFaceNum,
        'description="Abstract Min Mesh Size"',
        'type="RichInt"',
        'tooltip="This number and the following one indicate the range face number of the abstract mesh that is used for the parametrization process. The algorithm will choose the best abstract mesh with the number of triangles within the specified interval. If the mesh has a very simple structure this range can be very low and strict; for a roughly spherical object if you can specify a range of [8,8] faces you get a octahedral abstract mesh, e.g. a geometry image. &lt;br>Large numbers (greater than 400) are usually not of practical use."',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="targetAbstractMaxFaceNum"',
        'value="%d"' % targetAbstractMaxFaceNum,
        'description="Abstract Max Mesh Size"',
        'type="RichInt"',
        'tooltip="Please notice that a large interval requires huge amount of memory to be allocated, in order save the intermediate results. An interval of 40 should be fine."',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="stopCriteria"',
        'value="%d"' % stopCriteria,
        'description="Optimization Criteria"',
        'enum_val0="Best Heuristic"',
        'enum_val1="Area + Angle"',
        'enum_val2="Regularity"',
        'enum_val3="L2"',
        'enum_cardinality="4"',
        'type="RichEnum"',
        'tooltip="Choose a metric to stop the parametrization within the interval. 1: Best Heuristic : stop considering both isometry and number of faces of base domain. 2: Area + Angle : stop at minimum area and angle distorsion. 3: Regularity : stop at minimum number of irregular vertices. 4: L2 : stop at minimum OneWay L2 Stretch Eff"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="convergenceSpeed"',
        'value="%d"' % convergenceSpeed,
        'description="Convergence Precision"',
        'type="RichInt"',
        'tooltip="This parameter controls the convergence speed/precision of the optimization of the texture coordinates. Larger the number slower the processing and, eventually, slightly better results"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="DoubleStep"',
        'value="%s"' % str(DoubleStep).lower(),
        'description="Double Step"',
        'type="RichBool"',
        'tooltip="Use this bool to divide the parameterization in 2 steps. Double step makes the overall process faster and robust. Consider to disable this bool in case the object has topologycal noise or small handles."',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric_build_atlased_mesh(script, BorderSize=0.1):
    """Isometric parameterization: Build Atlased Mesh

    This actually generates the UV mapping from the isometric parameterization

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization Build Atlased Mesh">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="BorderSize"',
        'value="%s"' % BorderSize,
        'description="BorderSize ratio"',
        'min="0.01"',
        'max="0.5"',
        'type="RichDynamicFloat"',
        'tooltip="This parameter controls the amount of space that must be left between each diamond when building the atlas. It directly affects how many triangle are splitted during this conversion. In abstract parametrization mesh triangles can naturally cross the triangles of the abstract domain, so when converting to a standard parametrization we must cut all the triangles that protrudes outside each diamond more than the specified threshold. The unit of the threshold is in percentage of the size of the diamond, the bigger the threshold the less triangles are splitted, but the more UV space is used (wasted)."',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric_save(script, AbsName="TEMP3D.abs"):
    """Isometric parameterization: Save Abstract Domain

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization Save Abstract Domain">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="AbsName"',
        'value="%s"' % AbsName,
        'description="Abstract Mesh file"',
        'type="RichString"',
        'tooltip="The filename where the abstract mesh has to be saved"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric_load(script, AbsName="TEMP3D.abs"):
    """Isometric parameterization: Load Abstract Domain

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization Load Abstract Domain">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="AbsName"',
        'value="%s"' % AbsName,
        'description="Abstract Mesh file"',
        'type="RichString"',
        'tooltip="The filename of the abstract mesh that has to be loaded"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric_transfer(script, sourceMesh=0, targetMesh=1):
    """Isometric parameterization: transfer between meshes

    Provide the layer numbers of the source and target meshes.

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization transfer between meshes">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="sourceMesh"',
        'value="%s"' % sourceMesh,
        'description="Source Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh already having an Isoparameterization"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="targetMesh"',
        'value="%s"' % targetMesh,
        'description="Target Mesh"',
        'type="RichMesh"',
        'tooltip="The mesh to be Isoparameterized"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def isometric_remesh(script, SamplingRate=10):
    """Isometric parameterization: remeshing

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Iso Parametrization Remeshing">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="SamplingRate"',
        'value="%d"' % SamplingRate,
        'description="Sampling Rate"',
        'type="RichInt"',
        'tooltip="This specify the sampling rate for remeshing."',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def set_texture(script, textName="TEMP3D.png", textDim=1024):
    """Set texture

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Set Texture">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="textName"',
        'value="%s"' % textName,
        'description="Texture file"',
        'type="RichString"',
        'tooltip="If the file exists it will be associated to the mesh else a dummy one will be created"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textDim"',
        'value="%d"' % textDim,
        'description="Texture Dimension (px)"',
        'type="RichInt"',
        'tooltip="If the named texture doesn\'t exists the dummy one will be squared with this size"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def project_rasters(script, tex_file_out="TEMP3D.png", tex_size=1024,
                    fill_atlas_gaps=False, depth_threshold=0.5,
                    selected=False, use_angle=True, use_distance=True,
                    use_borders=True, use_silhouettes=True, use_alpha=False):
    """Set texture

    Creates new texture file
    tex_file_out = must be png
    fill_atlas_gaps  = setting this to false will leave the unprojected area transparent. This can then be easily composed with the original texture with PIL

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Project active rasters color to current mesh, filling the texture">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="textName"',
        'value="%s"' % tex_file_out,
        'description="Texture file"',
        'type="RichString"',
        'tooltip="The texture file to be created"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="texsize"',
        'value="%d"' % tex_size,
        'description="pixel size of texture image"',
        'type="RichInt"',
        'tooltip="pixel size of texture image, the image will be a square tsize X tsize, most applications do require that tsize is a power of 2"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="dorefill"',
        'value="%s"' % str(fill_atlas_gaps).lower(),
        'description="fill atlas gaps"',
        'type="RichBool"',
        'tooltip="If true, unfilled areas of the mesh are interpolated, to avoid visible seams while mipmapping"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="deptheta"',
        'value="%s"' % depth_threshold,
        'description="depth threshold"',
        'type="RichFloat"',
        'tooltip="threshold value for depth buffer projection (shadow buffer)"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="onselection"',
        'value="%s"' % str(selected).lower(),
        'description="Only on selecton"',
        'type="RichBool"',
        'tooltip="If true, projection is only done for selected vertices"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useangle"',
        'value="%s"' % str(use_angle).lower(),
        'description="use angle weight"',
        'type="RichBool"',
        'tooltip="If true, color contribution is weighted by pixel view angle"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="usedistance"',
        'value="%s"' % str(use_distance).lower(),
        'description="use distance weight"',
        'type="RichBool"',
        'tooltip="If true, color contribution is weighted by pixel view distance"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useborders"',
        'value="%s"' % str(use_borders).lower(),
        'description="use image borders weight"',
        'type="RichBool"',
        'tooltip="If true, color contribution is weighted by pixel distance from image boundaries"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="usesilhouettes"',
        'value="%s"' % str(use_silhouettes).lower(),
        'description="use depth discontinuities weight"',
        'type="RichBool"',
        'tooltip="If true, color contribution is weighted by pixel distance from depth discontinuities (external and internal silhouettes)"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="usealpha"',
        'value="%s"' % str(use_alpha).lower(),
        'description="use image alpha weight"',
        'type="RichBool"',
        'tooltip="If true, alpha channel of the image is used as additional weight. In this way it is possible to mask-out parts of the images that should not be projected on the mesh. Please note this is not a transparency effect, but just influences the weighting between different images"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def param_texture_from_rasters(script, textName="TEMP3D.png", texsize=1024,
                               colorCorrection=True, colorCorrectionFilterSize=1,
                               useDistanceWeight=True, useImgBorderWeight=True,
                               useAlphaWeight=False, cleanIsolatedTriangles=True,
                               stretchingAllowed=False, textureGutter=4):
    """Set texture

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Parameterization + texturing from registered rasters">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="textureSize"',
        'value="%d"' % texsize,
        'description="Texture size"',
        'type="RichInt"',
        'tooltip="Specifies the dimension of the generated texture"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textureName"',
        'value="%s"' % textName,
        'description="Texture name"',
        'type="RichString"',
        'tooltip="Specifies the name of the file into which the texture image will be saved"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="colorCorrection"',
        'value="%s"' % str(colorCorrection).lower(),
        'description="Color correction"',
        'type="RichBool"',
        'tooltip="If true, the final texture is corrected so as to ensure seamless transitions"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="colorCorrectionFilterSize"',
        'value="%d"' % colorCorrectionFilterSize,
        'description="Color correction filter"',
        'type="RichInt"',
        'tooltip="It is the radius (in pixel) of the kernel that is used to compute the difference between corresponding texels in different rasters. Default is 1 that generate a 3x3 kernel. Highest values increase the robustness of the color correction process in the case of strong image-to-geometry misalignments"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useDistanceWeight"',
        'value="%s"' % str(useDistanceWeight).lower(),
        'description="Use distance weight"',
        'type="RichBool"',
        'tooltip="Includes a weight accounting for the distance to the camera during the computation of reference images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useImgBorderWeight"',
        'value="%s"' % str(useImgBorderWeight).lower(),
        'description="Use image border weight"',
        'type="RichBool"',
        'tooltip="Includes a weight accounting for the distance to the image border during the computation of reference images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useAlphaWeight"',
        'value="%s"' % str(useAlphaWeight).lower(),
        'description="Use image alpha weight"',
        'type="RichBool"',
        'tooltip="If true, alpha channel of the image is used as additional weight. In this way it is possible to mask-out parts of the images that should not be projected on the mesh. Please note this is not a transparency effect, but just influences the weigthing between different images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="cleanIsolatedTriangles"',
        'value="%s"' % str(cleanIsolatedTriangles).lower(),
        'description="Clean isolated triangles"',
        'type="RichBool"',
        'tooltip="Remove all patches compound of a single triangle by aggregating them to adjacent patches"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="stretchingAllowed"',
        'value="%s"' % str(stretchingAllowed).lower(),
        'description="UV stretching"',
        'type="RichBool"',
        'tooltip="If true, texture coordinates are stretched so as to cover the full interval [0,1] for both directions"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textureGutter"',
        'value="%d"' % textureGutter,
        'description="Texture gutter"',
        'type="RichInt"',
        'tooltip="Extra boundary to add to each patch before packing in texture space (in pixels)"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return


def param_from_rasters(script, useDistanceWeight=True, useImgBorderWeight=True,
                       useAlphaWeight=False, cleanIsolatedTriangles=True,
                       stretchingAllowed=False, textureGutter=4):
    """Set texture

    """
    script_file = open(script, 'a')
    script_file.write('  <filter name="Parameterization from registered rasters">\n')
    script_file.write(' '.join([
        '    <Param',
        'name="useDistanceWeight"',
        'value="%s"' % str(useDistanceWeight).lower(),
        'description="Use distance weight"',
        'type="RichBool"',
        'tooltip="Includes a weight accounting for the distance to the camera during the computation of reference images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useImgBorderWeight"',
        'value="%s"' % str(useImgBorderWeight).lower(),
        'description="Use image border weight"',
        'type="RichBool"',
        'tooltip="Includes a weight accounting for the distance to the image border during the computation of reference images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="useAlphaWeight"',
        'value="%s"' % str(useAlphaWeight).lower(),
        'description="Use image alpha weight"',
        'type="RichBool"',
        'tooltip="If true, alpha channel of the image is used as additional weight. In this way it is possible to mask-out parts of the images that should not be projected on the mesh. Please note this is not a transparency effect, but just influences the weighting between different images"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="cleanIsolatedTriangles"',
        'value="%s"' % str(cleanIsolatedTriangles).lower(),
        'description="Clean isolated triangles"',
        'type="RichBool"',
        'tooltip="Remove all patches compound of a single triangle by aggregating them to adjacent patches"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="stretchingAllowed"',
        'value="%s"' % str(stretchingAllowed).lower(),
        'description="UV stretching"',
        'type="RichBool"',
        'tooltip="If true, texture coordinates are stretched so as to cover the full interval [0,1] for both directions"',
        '/>\n']))
    script_file.write(' '.join([
        '    <Param',
        'name="textureGutter"',
        'value="%d"' % textureGutter,
        'description="Texture gutter"',
        'type="RichInt"',
        'tooltip="Extra boundary to add to each patch before packing in texture space (in pixels)"',
        '/>\n']))
    script_file.write('  </filter>\n')
    script_file.close()
    return
