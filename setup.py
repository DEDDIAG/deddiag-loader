from setuptools import setup, find_packages

__version__ = "0.1.2"

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(name='deddiag-loader',
      version=__version__,
      url='',
      packages=find_packages(),
      install_requires=["pandas", "sqlalchemy", "psycopg2", "click"],
      author='Marc Wenninger',
      author_email='pypi@walwe.de',
      description='Loader for DEDDIAG, a Domestic Energy Demand Dataset of Individual Appliances Germany',
      long_description=long_description,
      long_description_content_type='text/markdown',
      classifiers=[
            'Programming Language :: Python :: 3',
            'License :: OSI Approved :: MIT License',
            'Operating System :: OS Independent',
      ],
      python_requires='>=3.6',
)
