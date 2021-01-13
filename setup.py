import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    install_requires = fh.readlines()

setuptools.setup(
    name="erika3004",
    version="0.0.1",
    author="CCCP Erika Team",
    description="Basic Erika3004 Control.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Chaostreff-Potsdam/erika3004/tree/minimal",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
    install_requires=install_requires
)