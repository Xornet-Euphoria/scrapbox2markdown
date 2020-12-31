from setuptools import setup, find_packages


setup(
    name="sb2md",
    version="0.1",
    install_requires=["requests"],
    package_dir={"": "src"},
    packages=find_packages("src"),
    scripts=["scripts/sb2md.py"]
)