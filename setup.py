from setuptools import setup

setup(name='tspec',
      version='0.1',
      description='Tuning spec python package',
      author='Tuowen Zhao',
      author_email='ztuowen@gmail.com',
      license='MIT',
      packages=['tspec'],
      install_requires = [
            'dnspython==1.15.0',
            'pymongo==3.6.0',
            'PyYAML==3.12'
          ],
      zip_safe=False)
