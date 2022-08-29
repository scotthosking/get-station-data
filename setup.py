from setuptools import setup, find_packages

setup(
    name='getGHCN',
    version='0.1',
    author='Scott Hosking',
    author_email='jask@bas.ac.uk',
    packages=find_packages(),
    url='https://github.com/scotthosking/get-station-data',
    description='Package for fetching weather station data from GHCN-Daily and GHCN-monthly',
    long_description=open('README.md').read(),
    license='TBD',
    keywords = "meteorology climatology analysis in_situ",
    scripts=['getGHCN/ghcnd.py', 'getGHCN/ghcnm.py'],
    data_files = [("", ["LICENSE.txt"])],
    install_requires=[
          'numpy',
          'pandas',
          'datetime',
    ],
)
