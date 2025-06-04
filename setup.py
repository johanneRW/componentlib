from setuptools import setup, find_packages

setup(
    name="componentlib",
    version="0.1",
    packages=find_packages(),
    include_package_data=True,
    description="A Django component library",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/johanneRW/componentlib.git",
    author="Johanne R. W.",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Framework :: Django",
    ],
    python_requires=">=3.6",
    install_requires=[
        "Django>=3.0",
        # Add other dependencies here
    ],
)
