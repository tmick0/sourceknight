from setuptools import setup

setup(
    name="sourceknight",
    version="0.1",
    author="travis mick",
    author_email="root@lo.calho.st",
    description="simple dependency manager for sourcemod projects",
    long_description="file:README.md",
    long_description_content_type="text/markdown",
    url="https://github.com/tmick0/sourceknight",
    packages=['sourceknight', 'sourceknight.drivers'],
    python_requires='>=3.8',
    install_requires=['pyyaml>=5.4,<6', 'GitPython>=3.1,<4', 'requests>=2.25,<3'],
    entry_points={'console_scripts': ["sourceknight=sourceknight.main:main"]}
)
