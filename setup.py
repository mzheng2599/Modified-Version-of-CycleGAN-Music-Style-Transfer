from setuptools import find_packages
from setuptools import setup

REQUIRED_PACKAGES = ['tensorflow==2.5.1', 'scipy==1.2.2', 'pretty_midi==0.2.8', 'imageio==2.4.1', 'metrics==0.3.3', ]

setup(
	name = 'trainer',
	version = '0.0',
	install_requires = REQUIRED_PACKAGES,
	packages = find_packages(),
	include_package_data = True,
	description = 'Generic example trainer package.',
)