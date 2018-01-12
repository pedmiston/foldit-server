from setuptools import setup

setup(
    name='folditdb',
    version='0.1.0',
    packages=['folditdb'],
    install_requires=[
     'SQLAlchemy==1.2.0',
     'PyMySQL==0.8.0',
    ],
)
