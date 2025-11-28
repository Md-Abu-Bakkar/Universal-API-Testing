from setuptools import setup, find_packages
import os

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read().splitlines()

setup(
    name="universal-api-tester",
    version="1.0.0",
    author="Md Abu Bakkar",
    author_email="abubakkar678121@gmail.com",
    description="Automated API Detection, Testing, and Bot Code Generation Tool",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Md-Abu-Bakkar/Universal-API-Testing",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "api-tester=main:main",
            "universal-api-tester=main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "universal_api_tester": [
            "templates/*.py",
            "templates/*.txt",
            "examples/*.json",
            "examples/*.txt",
        ],
    },
)
