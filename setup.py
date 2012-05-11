import os
from setuptools import setup, find_packages

from gitsummary import VERSION


def read(fname):
    return open(os.path.join(os.path.dirname(__file__), fname)).read()

requirements = read('requirements.txt').split('\n')
dependency_links = read('dependency_links.txt').split('\n')

setup(
    name = "Gitsummary",
    version = ".".join(map(str, VERSION)),
    description = "",
    long_description = read('README.rst'),
    url = '',
    license = 'MIT',
    author = 'The World Company',
    author_email = 'support@ellingtoncms.com',
    packages = find_packages(exclude=['tests']),
    classifiers = [
        'Development Status :: 3 - Alpha',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'Intended Audience :: Information Technology',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
    ],
    install_requires = requirements,
    dependency_links = dependency_links,
)
