from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="google-indexing-api-automation",
    version="1.0.0",
    author="KemalYildirim",
    description="Google Indexing API automation tool for bulk URL submissions",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/loydi/google-indexing-api-automation",
    py_modules=["main"],
    classifiers=[
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.31.0",
        "google-auth>=2.27.0",
    ],
)
