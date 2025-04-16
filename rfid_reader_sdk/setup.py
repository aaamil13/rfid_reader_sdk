#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Конфигурационен файл за инсталиране на библиотеката.
"""

from setuptools import setup, find_packages

setup(
    name="rfid_reader_sdk",
    version="0.1.0",  # увеличете версията, ако желаете, например на "0.2.0"
    description="RFID Reader SDK",
    author="Your Name",
    author_email="your.email@example.com",
    packages=find_packages(),
    # Добавете uhf_protocol пакета
    package_data={
        "rfid": ["*"],
        "rfid.reader": ["*"],
        "rfid.reader.uhf_protocol": ["*"],  # добавете новия подпакет
    },
    python_requires=">=3.6",
    install_requires=[
        "pyserial>=3.5",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
    ],
)