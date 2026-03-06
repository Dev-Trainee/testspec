from setuptools import setup, find_packages

setup(
    name="testspec-kit",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "typer>=0.12.0",
        "rich>=13.0.0",
        "openai>=1.30.0",
        "openpyxl>=3.1.0",
        "pyyaml>=6.0",
    ],
    entry_points={
        "console_scripts": [
            "testspec=testspec.cli:app",
        ],
    },
    python_requires=">=3.9",
)