import setuptools

with open("README", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="zvm", # Replace with your own username
    version="1.0.0",
    author="Ben Collins-Sussman",
    author_email="sussman@gmail.com",
    description="A pure-python implementation of a Z-machine for interactive fiction",
    long_description=long_description,
    long_description_content_type="text/x-rst",
    url="https://github.com/sussman/zvm",
    project_urls={
        "Bug Tracker": "https://github.com/sussman/zvm/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD License",
        "Operating System :: OS Independent",
        "Topic :: Games/Entertainment",
    ],
    packages=setuptools.find_packages(include=["zvm"]),
    python_requires=">=3.6",
)
