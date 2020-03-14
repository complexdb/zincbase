from pip._internal.req import parse_requirements
from setuptools import setup, find_packages

from zincbase import __version__

def _parse(filename):
    """Parse a requirements file, including `-r requirements.txt` references"""
    return [str(r.req) for r in parse_requirements(filename, session=False)]

setup(name='zincbase',
      version=__version__,
      description='A state of the art knowledge base',
      long_description=open("README.md", "r").read(),
      long_description_content_type="text/markdown",
      url='https://github.com/complexdb/zincbase',
      author='ComplexDB',
      author_email='tom@complexdb.com',
      license='MIT',
      packages=find_packages(exclude=['test']),
      classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
      ],
      include_package_data=True,
      install_requires=_parse("requirements.txt"),
      extras_require={
        'web': ['flask-socketio', 'redis']
      },
      python_requires='>=3.6'
      )