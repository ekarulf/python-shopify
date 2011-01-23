from distutils.core import setup

version = '0.3.0'

setup(name='shopify',
      version=version,
      description='Python bindings to Shopify API',
      author='Erik Karulf',
      author_email='erik@karulf.com',
      url='http://pypi.python.org/pypi/shopify',
      packages=['shopify'],
      package_dir={'shopify':'src'},
      license='MIT License',
      requires=['pyactiveresource>1.0.0']
      platforms=['any'],
      classifiers=['Development Status :: 3 - Alpha',
                   'Intended Audience :: Developers', 
                   'License :: OSI Approved :: MIT License', 
                   'Operating System :: OS Independent', 
                   'Programming Language :: Python', 
                   'Topic :: Software Development', 
                   'Topic :: Software Development :: Libraries', 
                   'Topic :: Software Development :: Libraries :: Python Modules']
      
    )
