from setuptools import setup

setup(
    install_requires=[
        "antlr4-python3-runtime~=4.13.2",
        "pandas~=2.2.3",
        "coverage~=7.6.12",
        "mutmut~=3.2.3",
        "parso~=0.8.4"
    ],
    name='arena-python',
    version='0.1',
    packages=['arena', 'tests'],
    url='https://github.com/SoftwareObservatorium/',
    license='GPL3',
    author='Marcus Kessel',
    author_email='marcus.kessel@uni-mannheim.de',
    description='LASSO Arena for Python'
)
