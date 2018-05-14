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
          'matplotlib==2.2.2',
          'numpy==1.14.3',
          'pymongo==3.6.1',
          'pyparsing==2.2.0',
          'python-dateutil==2.7.3',
          'pytz==2018.4',
          'PyYAML==3.12',
          'scikit-learn==0.19.1',
          'scikit-optimize==0.5.2',
          'scipy==1.1.0',
          'six==1.11.0'
      ],
      zip_safe=False)
