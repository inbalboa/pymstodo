import setuptools


def long_description():
    long_description = ''
    with open('README.md', 'r') as ld:
        long_description = ld.read()
    return long_description

def find_requires():
    requirements = []
    with open('requirements.txt', 'r') as reqs:
        requirements = reqs.readlines()
    return requirements

def find_version():
    with open('VERSION', 'r') as ver:
        version_ = ver.readline().strip()
    return version_


setuptools.setup(
    name='pymstodo',
    version=find_version(),
    author='Sergey Shlyapugin',
    author_email='shlyapugin@gmail.com',
    description='Microsoft To Do API client',
    long_description=long_description(),
    long_description_content_type='text/markdown',
    url='https://github.com/inbalboa/pymstodo',
    packages=setuptools.find_packages(),
    install_requires=find_requires(),
    python_requires='>=3.7,<4.0',
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3 :: Only',
        'License :: OSI Approved',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: OS Independent',
    ],
    license='GPLv3'
)

