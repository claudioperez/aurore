import io
from os.path import splitext, basename, join, dirname
from glob import glob

from setuptools import Extension
from setuptools import find_packages
from setuptools import setup


def read(*names, **kwargs):
    with io.open(
        join(dirname(__file__), *names),
        encoding=kwargs.get('encoding', 'utf8')
    ) as fh:
        return fh.read()

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="aurore",
    version="0.0.1",
    author="Claudio Perez",
    author_email="claudio_perez@berkeley.edu",
    description="Utilities",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/claudioperez/aurore",
    py_modules=[splitext(basename(path))[0] for path in glob("src/*.py")],
    include_package_data=True,
    packages=find_packages('src'),
    package_dir={'': 'src'},
    entry_points={
        'console_scripts': [
            'aurore = aurore.__main__:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    install_requires=[
        "docutils",
        # "coloredlogs",
        "pyyaml",
        #"rendre"
    ]
)
