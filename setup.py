from setuptools import setup, find_packages
import rouge

version = rouge.__version__
setup(
    name="rouge",
    version=version,
    description="Full Python ROUGE Score Implementation (not a wrapper)",
    url="http://github.com/pltrdy/rouge",
    download_url="https://github.com/pltrdy/rouge/archive/%s.tar.gz" % version,
    author="pltrdy",
    author_email="pltrdy@gmail.com",
    keywords=["NL", "CL", "natural language processing", "computational linguistics", "summarization"],
    packages=find_packages(),
    classifiers=[
        "Intended Audience :: Science/Research",
        "Programming Language :: Python :: 3",
        "Topic :: Text Processing :: Linguistic"
        ],
    license="LICENCE.txt",
    long_description=open("README.md").read(),
    test_suite="nose.collector",
    tests_require=['nose'],

    entry_points={
      'console_scripts': [
        'rouge=bin.rouge_cmd:main'
      ]
    }
)
