from setuptools import setup

setup(
    name='tigergrader',
    version='0.1.0',
    author='Pablo Oliveira',
    author_email='pablo@sifflez.org',
    url='http://github.com/pablooliveira/tigergrader',
    long_description=__doc__,
    packages=['tigergrader'],
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        "Flask>=0.9",
        "celery>=3.1",
        "argparse",
        "distribute",
    ],
    extras_require=dict(test = [
        "coverage",
        "nose",
        "mock"
    ]),
)
