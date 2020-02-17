import os
import re

from setuptools import setup, find_packages


def get_version():
    path = os.path.join(os.path.dirname(__file__), 'rouge', '__init__.py')
    with open(path, 'r') as f:
        content = f.read()
    m = re.search(r'__version__\s*=\s*"(.+)"', content)
    assert m is not None
    return m.group(1)


def long_description():
    this_directory = os.path.abspath(os.path.dirname(__file__))
    with open(os.path.join(this_directory, 'README.md'), encoding='utf-8') as f:
        return f.read()


version = get_version()

setup(
    name="rouge",
    version=version,
    description="Full Python ROUGE Score Implementation (not a wrapper)",
    url="http://github.com/pltrdy/rouge",
    download_url="https://github.com/pltrdy/rouge/archive/%s.tar.gz" % version,
    author="pltrdy",
    author_email="pltrdy@gmail.com",
    keywords=["NL", "CL", "natural language processing",
              "computational linguistics", "summarization"],
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Linguistic"
    ],
    license="LICENCE.txt",
    long_description=long_description(),
    long_description_content_type='text/markdown',
    test_suite="nose.collector",
    tests_require=['nose'],
    install_requires=['six'],
    entry_points={
        'console_scripts': [
            'rouge=bin.rouge_cmd:main'
        ]
    }
)
