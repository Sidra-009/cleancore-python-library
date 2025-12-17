from setuptools import setup, find_packages

setup(
    name="mathnexus", 
    version="0.3.4",   
    author="Sidra Saqlain",
    author_email="sidrasaqlain11@gmail.com", 
    description="A library for Linear Algebra, 2D Geometry, and Physics Simulations.",
    long_description=open("README.md", encoding="utf-8").read(), 
    long_description_content_type="text/markdown",
    url="https://github.com/Sidra-009/mathnexus", 
    project_urls={
        "Documentation": "https://mathnexus.readthedocs.io/",
        "Source": "https://github.com/Sidra-009/mathnexus",
        "Tracker": "https://github.com/Sidra-009/mathnexus/issues",
    },
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.7',
)