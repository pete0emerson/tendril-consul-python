from setuptools import setup

setup(
    name='tendril',
    version='0.1',
    py_modules=['tendril'],
    install_requires=[
        'Click',
    ],
    entry_points='''
        [console_scripts]
        tendril=cli:cli
    ''',
)

