from setuptools import setup, find_packages


# REQUIREMENTS = ["requests"]
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="gitignore-create",
    version="0.0.1a",
    description="A CLI tool to generate gitignore files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/iliailmer/gitignore-create",
    author="Ilia Ilmer",
    author_email="i.ilmer@icloud.com",
    license="GNU GENERAL PUBLIC LICENSE",
    packages=find_packages(),
    entry_points={"console_scripts": ["gitignore-create=ignore:main"]},
    # install_requires=REQUIREMENTS,
    keywords="gitignore git",
)
