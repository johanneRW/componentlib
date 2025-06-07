from setuptools import setup, find_packages

setup(
    name="componentlib",
    version="0.3",
    packages=find_packages(),
    include_package_data=True,
    package_data={
        'componentlib': ['components/*', 'templates/*', 'static/*'],
    },
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
        "Django>=4.2",
        "pyyaml",
        "rapidfuzz>=3.13.0",
        "watchdog>=6.0.0",
        "pydantic>=2.11.4",
        # Add other dependencies here
    ],
)
