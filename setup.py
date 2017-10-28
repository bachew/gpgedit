# -*- coding: utf-8 -*-
from glob import glob
from os import path as osp
from setuptools import setup, find_packages


proj_dir = osp.dirname(__file__)
modules = [osp.splitext(osp.basename(path))[0]
           for path in glob(osp.join(proj_dir, 'src/*.py'))]
config = {
    'name': 'gpgedit',
    'version': '0.0.5',
    'description': 'GpgEdit lets you edit a gpg-encrypted file',
    'license': 'MIT',
    'author': 'Chew Boon Aik',
    'author_email': 'bachew@gmail.com',
    'url': 'https://github.com/bachew/gpgedit',
    'download_url': 'https://github.com/bachew/gpgedit/archive/master.zip',
    'packages': find_packages('src'),
    'package_dir': {'': 'src'},
    'py_modules': modules,
    'install_requires': [
        'click>=6.7',
        'gevent>=1.2.2',
    ],
    'entry_points': {
        'console_scripts': [
            'gpgedit=gpgedit:cli',
        ],
    },
    'zip_safe': False,
    'classifiers': [
        'Development Status :: 4 - Beta',
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Operating System :: Unix',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',

        'Topic :: Software Development :: Build Tools',
        'Topic :: Utilities',

    ],
}
setup(**config)
