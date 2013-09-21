#!/usr/bin/env python
from distutils.core import setup


setup(name='drawinvoice',
        version='0.3.1',
        url='https://github.com/temaput/drawinvoice',
        author="Artem Putilov",
        author_email="putilkin@gmail.com",
        description="generate russian invoices in pdf with reportlab",
        long_description=open('README.md').read(),
        keywords="Invoice, Sales Slip",
        license='BSD',
        packages=['drawinvoice'],
        package_data={'drawinvoice': ['fonts/*.ttf']},
        requires=['reportlab(>=2.0)', 'pytils', 'babel'],
        # See http://pypi.python.org/pypi?%3Aaction=list_classifiers
        classifiers=['Environment :: Commercial',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: BSD License',
            'Operating System :: Unix',
            'Programming Language :: Python']
        )
