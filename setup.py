from setuptools import setup

setup(
    name='puppetparser',
    version='0.1.1',
    author='Nuno Saavedra',
    author_email='nuno.saavedra',
    packages=['puppetparser'],
    description='A parser for Puppet',
    install_requires=[
    "ply"
    ],
)