#!/usr/bin/env python
from setuptools import setup, find_packages


setup(name='drawinvoice',
        version='0.1',
        url='https://github.com/temaput/drawinvoice',
        author="Artem Putilov",
        author_email="putilkin@gmail.com",
        description="generate invoices in pdf with reportlab",
        long_description=open('README.md').read(),
        keywords="Invoice, Sales Slip",
        license='BSD',
        packages=find_packages(),
        include_package_data=True,
        install_requires=['reportlab>=2', 'pytils', 'babel'],
        # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=['Environment :: Commercial',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Unix',
            'Programming Language :: Python']
        )
