"""
Flask-Swagger
-------------

This is the description for that library
"""
from setuptools import setup


setup(
    name='Flask-Swagger',
    version='1.0',
    url='https://github.com/hobbeswalsh/flask-swagger',
    license='BSD',
    author='Robin Walsh & Harvey Rogers',
    author_email='rob.walsh@gmail.com',
    description='So you want to implement an auto-documenting API?',
    long_description=__doc__,
    py_modules=['flask_swagger'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask'
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ]
)
