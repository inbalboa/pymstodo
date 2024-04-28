from pathlib import Path

import setuptools


def long_description():
    with Path('README.md').open() as ld:
        return ld.read()


def find_requires():
    with Path('requirements.txt').open() as reqs:
        return reqs.readlines()


def find_version():
    with Path('VERSION').open() as ver:
        return ver.readline().strip()


setuptools.setup(
    name='pymstodo',
    version=find_version(),
    author='Serhiy Shliapuhin',
    author_email='shlyapugin@gmail.com',
    description='Microsoft To Do API client',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/inbalboa/pymstodo',
    packages=setuptools.find_packages(),
    install_requires=find_requires(),
    python_requires='>=3.10,<4.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    license='GPLv3'
)
