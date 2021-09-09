import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="slivka-irv",
    version="1.0.0",
    author="Nathan White, Andreas Bugler",
    author_email="nathanwhite2022@u.northwestern.edu, andreas@u.northwestern.edu",
    description="IRV Algorithm and Wildcat Connection Parser",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/nathanllww/slivka-irv",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)