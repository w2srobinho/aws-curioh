import curioh

from setuptools import find_packages, setup

version = curioh.__version__

setup(
    name='Curioh',
    version=version,
    description=('Simple Amazon AWS requests.'),
    url='https://github.com/w2srobinho/curioh',
    author='Willian de Souza',
    author_email='willianstosouza@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'boto3>=1.2.6'
    ],
)