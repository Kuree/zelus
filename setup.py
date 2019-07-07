from setuptools import setup


setup(
    name='zelus',
    packages=[
        "zelus"
    ],
    version='0.0.1',
    author='Keyi Zhang',
    author_email='keyi@stanford.edu',
    description='Zelus is a collections of useful circuits based on kratos',
    url="https://github.com/Kuree/zelus",
    install_requires=[
        "kratos",
    ],
)
