#!/usr/bin/env python
from setuptools import setup, find_packages

# read the contents of your README file
from pathlib import Path
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text()

requirements = []
with open("requirements.txt") as f:
    for line in f:
        stripped = line.split("#")[0].strip()
        if len(stripped) > 0:
            requirements.append(stripped)

setup(
    name='get-station-data',
    version='0.1',
    author='J. Scott Hosking',
    author_email='jask@bas.ac.uk',
    packages=find_packages(),
    url='https://github.com/scotthosking/get-station-data',
    description='Package for fetching weather station data from GHCN-Daily and GHCN-monthly',
    long_description=long_description,
    install_requires=requirements,
)
