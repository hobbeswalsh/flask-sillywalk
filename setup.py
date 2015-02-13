"""
Flask-Swagger
-------------

This is the description for that library
"""
from setuptools import setup, find_packages


with open('README.md') as f:
    description = f.read()

setup(
    name='Flask-Sillywalk',
    version='1.0',
    url='https://github.com/hobbeswalsh/flask-swagger',
    license='BSD',
    author='Robin Walsh & Harvey Rogers',
    author_email='rob.walsh@gmail.com',
    description='So you want to implement an auto-documenting API?',
    long_description=description,
    packages=find_packages(exclude=['ez_setup', 'examples']),
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask',
        'nose',
        'coverage',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
)
