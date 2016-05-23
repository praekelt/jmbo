from setuptools import setup, find_packages

setup(
    name='jmbo',
    version='2.0.16',
    description='The Jmbo base product introduces a content type and various tools required to build Jmbo products.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://www.jmbo.org',
    packages = find_packages(),
    install_requires = [
        # The bare minimum requirements. The tests use explicit versions.
        'Pillow',
        'pytz',
        'django>=1.9',
        'django-category>=1.9',
        'django-likes>=0.0.8',
        'django-pagination-fork>=1.0.17',
        'django-preferences',
        'django-photologue>=3.3',
        'django-sites-groups',
        'django-ultracache>=1.9',
    ],
    include_package_data=True,
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: BSD License",
        "Development Status :: 5 - Production/Stable",
        "Operating System :: OS Independent",
        "Framework :: Django",
        "Intended Audience :: Developers",
        "Topic :: Internet :: WWW/HTTP :: Dynamic Content",
    ],
    zip_safe=False,
)
