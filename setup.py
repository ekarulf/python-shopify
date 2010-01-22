from setuptools import setup, find_packages

setup(
    name = "shopipy",
    version = "0.1",
    url = 'http://www.bitbucket.org/pennyarcade/shopipy/',
    license = 'MIT',
    description = "A simple Shopify API wrapper",
    author = 'Erik Karulf <erik@karulf.com>',
    # Below this line is tasty Kool-Aide provided by the Cargo Cult
    packages = find_packages('src'),
    package_dir = {'': 'src'},
    install_requires = ['setuptools'],
)