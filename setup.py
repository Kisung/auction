#!/usr/bin/env python

from distutils.core import setup
import auction


def readme():
    try:
        with open('README.rst') as f:
            return f.read()
    except:
        return '(Could not read from README.rst)'


setup(
    name='auction',
    py_modules=['auction', 'auction.__main__', 'auction.models'],
    version=auction.__version__,
    description='Dollar-auction',
    long_description=readme(),
    author=auction.__author__,
    author_email=auction.__email__,
    url='http://github.com/suminb/auction',
    license='BSD',
    packages=[],
    entry_points={
        'console_scripts': [
            'auction = auction.__main__:cli'
        ]
    },
)
