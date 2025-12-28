from setuptools import setup, find_packages
from pathlib import Path

# Read the contents of README file
this_directory = Path(__file__).parent
long_description = (this_directory / "README.md").read_text(encoding='utf-8')

setup(
    name='torcrawl',
    version='1.34',
    description='A Python script to crawl and extract (regular or onion) webpages through TOR network.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/MikeMeliz/TorCrawl.py',
    author='MikeMeliz',
    author_email='mike@mikemeliz.com',
    license='GNU General Public License v3.0',
    keywords='osint, web-scraping, crawler, tor, onion, web-crawler, scraping, anonymous, privacy, security, data-extraction',
    project_urls={
        'Homepage': 'https://github.com/MikeMeliz/TorCrawl.py',
        'Repository': 'https://github.com/MikeMeliz/TorCrawl.py',
        'Issue Tracker': 'https://github.com/MikeMeliz/TorCrawl.py/issues',
    },
    packages=find_packages(),
    py_modules=['torcrawl'],
    install_requires=[
        'pysocks',
        'beautifulsoup4>=4.7.1',
        'yara-python',
        'lxml',
    ],
    package_data={
        'res': ['keywords.yar', 'proxies.txt', 'user_agents.txt'],
    },
    include_package_data=True,
    entry_points={
        'console_scripts': [
            'torcrawl=torcrawl:main',
        ],
    },
    python_requires='>=3.9',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Intended Audience :: Information Technology',
        'Intended Audience :: Education',
        'Intended Audience :: Science/Research',
        'Intended Audience :: Other Audience',
        'License :: OSI Approved :: GNU General Public License v3 (GPLv3)',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Topic :: Internet :: WWW/HTTP :: Indexing/Search',
        'Topic :: Security',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
)
