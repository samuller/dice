from setuptools import setup, find_packages
from os import path
from dice import __version__

here = path.abspath(path.dirname(__file__))

try:
    with open(path.join(here, 'requirements.txt')) as f:
        requirements = f.read().splitlines()
except Exception:
    requirements = []

# Get the long description from the README file
# pandoc --from=markdown --to=rst --output=README.rst README.md
with open(path.join(here, 'README.rst'), encoding='utf-8') as f:
    long_description = f.read()

setup(
    name='dice-sim',
    version=__version__,
    author='Simon Muller',
    author_email='samullers@gmail.com',
    url='https://github.com/samuller/dice',
    description='Simulate various dice throw situations',
    long_description=long_description,
    py_modules=['dice'],
    packages=find_packages(exclude=['*.tests*']),
    install_requires=requirements,
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'dice=dice:main',
        ],
    },
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU Lesser General Public License v2 (LGPLv2)',
        'Natural Language :: English',
        'Programming Language :: Python',
        'Topic :: Games/Entertainment',
        'Topic :: Games/Entertainment :: Board Games',
        'Topic :: Utilities',
    ],
)
