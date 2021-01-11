from setuptools import setup


# read the contents of your README file
import io
from os import path
this_directory = path.abspath(path.dirname(__file__))
with io.open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

setup(name='MeshLabXML',
      version='2018.3',
      description='Create and run MeshLab XML scripts',
      long_description=long_description,
      long_description_content_type='text/markdown',
      url='https://github.com/3DLIRIOUS/MeshLabXML',
      author='3DLirious, LLC',
      author_email='3DLirious@gmail.com',
      license='LGPL-2.1',
      packages=['meshlabxml'],
      include_package_data=True)
