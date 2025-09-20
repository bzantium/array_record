"""Setup.py file for array_record."""

from setuptools import find_packages
from setuptools import setup
from setuptools.dist import Distribution

REQUIRED_PACKAGES = [
    'absl-py',
    'etils[epath]',
]

TF_PACKAGE = ['tensorflow>=2.20.0']

BEAM_EXTRAS = [
    'apache-beam[gcp]>=2.53.0',
    'google-cloud-storage>=2.11.0',
] + TF_PACKAGE

TEST_EXTRAS = [
    'jax',
    'grain',
] + TF_PACKAGE


class BinaryDistribution(Distribution):
  """This class makes 'bdist_wheel' include an ABI tag on the wheel."""

  def has_ext_modules(self):
    return True


setup(
    name='array-record-python',
    version='0.8.1',
    description='A high-performance file format for ML data storage with parallel I/O and random access',
    long_description=open('README.md').read(),
    long_description_content_type='text/markdown',
    author='ArrayRecord Python Contributors',
    author_email='bzantium@users.noreply.github.com',
    packages=find_packages(),
    include_package_data=True,
    package_data={'': ['*.so']},
    python_requires='>=3.10',
    install_requires=REQUIRED_PACKAGES,
    extras_require={'beam': BEAM_EXTRAS, 'test': TEST_EXTRAS},
    url='https://github.com/bzantium/array_record',
    project_urls={
        'Documentation': 'https://arrayrecord.readthedocs.io',
        'Bug Reports': 'https://github.com/bzantium/array_record/issues',
        'Source': 'https://github.com/bzantium/array_record',
    },
    license='Apache-2.0',
    keywords=['machine-learning', 'data-storage', 'parallel-io', 'compression', 'tensorflow', 'jax'],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Intended Audience :: Science/Research',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        'Programming Language :: Python :: 3.12',
        'Programming Language :: Python :: 3.13',
        'Programming Language :: C++',
        'Topic :: Scientific/Engineering :: Artificial Intelligence',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: System :: Archiving :: Compression',
        'Operating System :: POSIX :: Linux',
        'Operating System :: MacOS',
    ],
    zip_safe=False,
    distclass=BinaryDistribution,
)
