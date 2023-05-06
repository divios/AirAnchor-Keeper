import os
import subprocess

from setuptools import setup, find_packages


data_files = []

if os.path.exists("/etc/default"):
    data_files.append(
        ('/etc/default', ['packaging/systemd/air-anchor-tracker']))

if os.path.exists("/lib/systemd/system"):
    data_files.append(
        ('/lib/systemd/system',
         ['packaging/systemd/air-anchor-tracker.service']))

setup(
    name='air_anchor_tracker',
    version='1.0',
    description='Air anchor tracker',
    author='divios',
    url='',
    packages=find_packages(),
    install_requires=[
        "zmq",
        "pymongo",
        "sawtooth-sdk",
        "colorlog",
        "protobuf==3.20.*",
        "pika"
    ],
    data_files=data_files,
    entry_points={
        'console_scripts': [
            'air-anchor-tracker = air_anchor_tracker.main:main'
        ]
    })