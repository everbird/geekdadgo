#!/usr/bin/env python3

import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="geekdadgo",
    version="0.1.1",
    author="everbird",
    author_email="stephen.zhuang@gmail.com",
    description="Assist parents in exporting their child's personal data from Procare, including photos, videos, notes, meals, and more.",
    include_package_data=True,
    install_requires=[
        'click==8.1.3',
        'imutils==0.5.4',
        'opencv-python==4.7.0.72',
        'PyExifTool==0.5.5',
        'pytesseract==0.3.10',
        'python-dateutil==2.8.2',
        'requests==2.31.0',
        'tomli==2.0.1',
        'tomlkit==0.11.8',
        'urllib3==1.26.15',
    ],
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/everbird/geekdadgo",
    packages=setuptools.find_packages(),
    package_data = {'': ['LICENSE', "config/*.conf"]},
    entry_points={
        'console_scripts': [
            'geekdadgo=geekdadgo.cli:main',
        ]
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    setup_requires=["pytest-runner"],
    tests_require=["pytest"],
)
