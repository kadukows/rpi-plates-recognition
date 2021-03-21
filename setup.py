from setuptools import find_packages, setup

setup(
    name='rpiplatesrecognition',
    version='0.0.1',
    url='https://github.com/kadukows/rpi-plates-recognition',
    package_dir={'': 'src'},
    packages=find_packages(where='src'),
    python_requires='>=3.6',
    include_package_data=True,
    zip_safe=False,
    install_requires=[
        'flask',
    ],
)
