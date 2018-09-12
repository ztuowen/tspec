from setuptools import setup

with open('requirements.txt', 'r') as f:
    requires = list(f.readlines())

setup(name='tspec',
      version='0.1',
      description='Tuning spec python package',
      author='Tuowen Zhao',
      author_email='ztuowen@gmail.com',
      license='MIT',
      packages=['tspec'],
      python_requires='>=3.6.0',
      install_requires=requires,
      zip_safe=False)
