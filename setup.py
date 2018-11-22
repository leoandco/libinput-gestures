#!/usr/bin/env python3

from distutils.core import setup

from setuptools import find_packages

setup(name='libinputgestures',
      version='1.0',
      description='Monitor libinput debug-events for gestures and dispatch a script.',
      author='Leo Xiong',
      author_email='hello@leoxiong.com',
      url='https://github.com/leoxiong/libinput-gestures',
      packages=find_packages(),
      install_requires=['Click'],
      entry_points={
          'console_scripts': ['libinput-gestures=libinput_gestures.__main__:listen'],
      },
      )
