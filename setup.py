#!/usr/bin/env python

"""The setup script."""

from setuptools import setup, find_packages

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

with open('requirements.txt') as requirements_file:
    requirements = requirements_file.read()

setup_requirements = []

test_requirements = []

setup(
    author="Richard Boltze",
    author_email='rboltze@protonmail.com',
    python_requires='>=3.6',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    description="The library was created to be used as a building block for applications were information "
                "should appear on the surface of a sphere. It allows for creating spheres with nodes "
                "and edges that can be dragged on its surface. Nodes and edges can added and removed "
                "from the sphere surface. This library is written in Python, PyOpenGL and PyQT5 ",
    install_requires=requirements,
    license="MIT license",
    long_description=readme,
    include_package_data=True,
    keywords='sphere_base',
    name='sphere_base',
    packages=find_packages(include=['sphere_base*'], exclude=['examples*', 'test*']),
    setup_requires=setup_requirements,
    test_suite='tests',
    tests_require=test_requirements,
    url='https://github.com/rboltze/spherebase',
    version='0.1.1',
    zip_safe=False,
)
