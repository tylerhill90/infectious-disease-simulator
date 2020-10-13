import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="COVID-19-Simulator",
    version="0.0.1",
    author="Tyler Hill",
    author_email="tylerhill90@gmail.com",
    description="An infectious disease simulator",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://https://github.com/tylerhill90/COVID-19-Simulator",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',
)