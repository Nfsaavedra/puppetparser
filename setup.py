from setuptools import setup
import pathlib

here = pathlib.Path(__file__).parent.resolve()
long_description = (here / "README.md").read_text(encoding="utf-8")

setup(
    name='puppetparser',
    version='0.2.2',
    author='Nuno Saavedra',
    author_email='nuno.saavedra@tecnico.ulisboa.pt',
    url="https://github.com/Nfsaavedra/puppetparser",
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Topic :: Software Development :: Build Tools",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3 :: Only",
    ],
    keywords="puppet, parser, model",
    python_requires=">=3.9, <4", 
    packages=['puppetparser'],
    description='A parser from Puppet to an object model',
    long_description=long_description,
    long_description_content_type="text/markdown", 
    install_requires=[
        "ply"
    ],
    project_urls={
        "Bug Reports": "https://github.com/Nfsaavedra/puppetparser/issues",
        "Source": "https://github.com/Nfsaavedra/puppetparser",
    },
)
