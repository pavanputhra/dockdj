import pathlib
from setuptools import setup

# The directory containing this file
HERE = pathlib.Path(__file__).parent

# The text of the README file
README = (HERE / "README.md").read_text()

# This call to setup() does all the work
setup(
    name="dockdj",
    version="2.2.2",
    description="Deploy the Django app to Ubuntu server as docker container.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/pavanputhra/dockdj",
    author="Pavan Kumar",
    author_email="pavanputhra@gmail.com",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
    ],
    packages=["dockdj"],
    include_package_data=True,
    install_requires=["fabric", "PyYAML"],
    entry_points={
        "console_scripts": [
            "dockdj=dockdj.__main__:main",
        ]
    },
)
