from setuptools import setup

setup(
    name="sourceknight",
    version="0.0.1",
    author="travis mick",
    author_email="root@lo.calho.st",
    description="simple dependency manager for sourcemod projects",
    packages=['sourceknight'],
    python_requires='>=3.8',
    install_requires=['pyyaml>=5.4,<6'],
    entry_points={'console_scripts': ["sourceknight=sourceknight.main:main"]}
)
