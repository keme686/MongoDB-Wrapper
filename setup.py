#!/usr/bin/env python

from distutils.core import setup
from setuptools import find_packages

setup(name='MongoDBWrapper',
      version='0.1',
      description='MongoDB wrapper REST service',
      author='Kemele M. Endris',
      author_email='endris@cs.uni-bonn.de',
      url='https://github.com/EIS-Bonn/Ontario-Wrappers',
      packages=find_packages(exclude=['docs']),
      scripts=['endpointservice/MongodbEndpoint.py'],
      install_requires=["flask", "pymongo"],
      include_package_data=True,
      license='GNU/GPL v2'
     )