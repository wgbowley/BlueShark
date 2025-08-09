from setuptools import setup, find_packages

setup(
    name='blueshark',
    version='1.2.0',
    description=(
        'Modular FEMM-based linear and tubular motor simulation framework'
    ),
    author='William Bowley',
    author_email='wgrantbowley@gmail.com',
    packages=find_packages(include=["blueshark", "blueshark.*"]),
    install_requires=[
        'PyYAML',
        'pyfemm',
        'matplotlib',
        'deap',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Topic :: Scientific/Engineering',
    ],
    python_requires='>=3.8',
)
