import os
import glob
import setuptools
from distutils.core import setup

with open("README.md", 'r') as readme:
    long_description = readme.read()

setup(
    name='vivarium_models',
    version='0.0.1',
    packages=[
        'vivarium_models',
        'vivarium_models.processes',
        'vivarium_models.compartments',
        'vivarium_models.experiments',
    ],
    author='',  # TODO: Put your name here.
    author_email='',  # TODO: Put your email here.
    url='',  # TODO: Put your project URL here.
    license='',  # TODO: Choose a license.
    entry_points={
        'console_scripts': []},
    short_description='',  # TODO: Describe your project briefely.
    long_description=long_description,
    long_description_content_type='text/markdown',
    package_data={},
    include_package_data=True,
    install_requires=[
        'vivarium-core',
        # TODO: Add other dependencies.
    ],
)
