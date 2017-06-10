import sys
from setuptools import setup, find_packages

if sys.version_info.major < 3:
    raise RuntimeError('Installing requires Python 3 or newer')

setup(
    name="prometheus-pgbouncer-exporter",
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-pgbouncer-exporter = prometheus_pgbouncer_exporter.cli:main',
        ],
    },
)
