from distutils.core import setup
from setuptools import find_packages

with open('README.md') as readme:
    long_description = readme.read()

with open('requirements.txt') as reqs:
    install_requires = [
        line for line in reqs.read().split('\n') if (line and not
                                                     line.startswith('--'))
    ]

setup(
    name = 'GraphSpace Server',
    version = '1.3.0',
    url = 'http://graphspace.org',
    license = 'GNU GENERAL PUBLIC LICENSE',
    author = 'adb',
    author_email = 'adb@vt.edu',
    description = 'The interactive graph sharing website.',
    long_description=long_description,
    packages=['graphspace'],
    include_package_data=False,
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
    ],
    zip_safe=False,
    install_requires=install_requires
)
