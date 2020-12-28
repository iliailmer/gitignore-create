from setuptools import setup


REQUIREMENTS = ["requests"]


setup(
    name="gitignore-create",
    version="0.0.1",
    description="A small CLI tool to generate gitignore files",
    url="https://github.com/iliailmer/gitignore-create",
    author="Ilia Ilmer",
    author_email="i.ilmer@icloud.com",
    license="GNU GENERAL PUBLIC LICENSE",
    packages=["ignore"],
    entry_points={"console_scripts": ["gitignore-create=ignore:main"]},
    install_requires=REQUIREMENTS,
    keywords="gitignore git",
)
