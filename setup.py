from setuptools import setup
from pathlib import Path

setup(
    name="sourceknight",
    version="0.2",
    author="travis mick",
    author_email="root@lo.calho.st",
    description="simple dependency manager for sourcemod projects",
    long_description=(Path(__file__).parent / "README.md").read_text(),
    long_description_content_type="text/markdown",
    url="https://github.com/tmick0/sourceknight",
    packages=['sourceknight', 'sourceknight.drivers'],
    python_requires='>=3.8',
    install_requires=['pyyaml>=5.4,<6', 'GitPython>=3.1,<4', 'requests>=2.25,<3'],
    entry_points={'console_scripts': ["sourceknight=sourceknight.main:main"]}
)
