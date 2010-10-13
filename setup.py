from setuptools import setup, find_packages
import shopipy

setup(
    name = "shopipy",
    version = shopipy.__version__,
    url = 'http://www.github.com/penny-arcade/shopipy/',
    license = 'MIT',
    description = "A simple Shopify API wrapper",
    author = 'Erik Karulf <erik@karulf.com>',
    # Below this line is tasty Kool-Aide provided by the Cargo Cult
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)