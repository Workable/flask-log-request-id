import re
import ast
from setuptools import setup


_version_re = re.compile(r'__version__\s+=\s+(.*)')

with open('flask_log_request_id/__init__.py', 'rb') as f:
    version = str(ast.literal_eval(_version_re.search(
        f.read().decode('utf-8')).group(1)))


setup(
    name='Flask-Log-Request-ID',
    version='0.1.0',
    url='http://github.com/Workable/flask-log-request-id',
    license='BSD',
    author='Konstantinos Paliouras, Ioannis Foukarakis',
    author_email='squarious@gmail.com, foukarakis@workable.com',
    description='An extension that detects request id headers on request '
                'and propagates on logging module through the life-cycle of request',
    maintainer="Konstantinos Paliouras",
    maintainer_email="squarious@gmail.com",
    packages=[
        'flask_log_request_id',
        'flask_log_request_id.extras'],
    zip_safe=False,
    include_package_data=True,
    platforms='any',
    install_requires=[
        'Flask>=0.8',
    ],
    tests_require=[
        'nose',
        'mock==2.0.0',
        'coverage~=4.3.4',
        'celery~=4.1.0'
    ],
    setup_requires=[
        "flake8"
    ],
    test_suite='nose.collector',
    classifiers=[
        'Environment :: Web Environment', 'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent', 'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ])
