from setuptools import setup

setup(name='tspec',
      version='0.1',
      description='Tuning spec python package',
      author='Tuowen Zhao',
      author_email='ztuowen@gmail.com',
      license='MIT',
      packages=['tspec'],
      install_requires=[
          'cycler==0.10.0',
          'dill==0.2.7.1',
          'dnspython==1.15.0',
          'matplotlib==2.1.2',
          'numpy==1.14.0',
          'pymongo==3.6.0',
          'pyparsing==2.2.0',
          'python-dateutil==2.6.1',
          'pytz==2018.3',
          'PyYAML==3.12',
          'scikit-learn==0.19.1',
          'scikit-optimize==0.5.1',
          'scipy==1.0.0',
          'six==1.11.0'
      ],
      zip_safe=False)
