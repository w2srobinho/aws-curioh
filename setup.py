import aws_curioh

from setuptools import find_packages, setup

version = aws_curioh.__version__

setup(
    name='aws-curioh',
    version=version,
    description=('Simple Amazon AWS requests.'),
    url='https://github.com/w2srobinho/aws-curioh',
    author='Willian de Souza',
    author_email='willianstosouza@gmail.com',
    license='MIT',
    packages=find_packages(exclude=['tests']),
    install_requires=[
        'boto3>=1.2.6'
    ],
)
