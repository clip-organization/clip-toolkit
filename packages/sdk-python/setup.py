from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="clip-sdk",
    version="0.1.0",
    author="CLIP Team",
    author_email="info@clip-spec.org",
    description="Python SDK for the Context Link Interface Protocol (CLIP)",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/clip-spec/clip-toolkit",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "jsonschema>=4.0.0",
        "requests>=2.25.0",
        "pydantic>=1.8.0",
        "aiohttp>=3.7.0"
    ],
) 