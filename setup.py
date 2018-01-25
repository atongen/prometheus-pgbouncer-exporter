import sys
from setuptools import setup, find_packages

if sys.version_info.major < 3:
    raise RuntimeError('Installing requires Python 3 or newer')

setup(
    name="prometheus-pgbouncer-exporter",
    version="0.1.8",
    python_requires='>=3',
    packages=find_packages(),
    entry_points={
        'console_scripts': [
            'prometheus-pgbouncer-exporter = prometheus_pgbouncer_exporter.cli:main',
        ],
    },
    install_requires=[
        'psycopg2',
        'ConfigArgParse',
        'prometheus_client',
    ],
)
