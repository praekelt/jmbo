from setuptools import setup, find_packages


setup(
    name='jmbo',
    version='3.0.2',
    description='The Jmbo base product introduces a content type and various tools required to build Jmbo products.',
    long_description = open('README.rst', 'r').read() + open('AUTHORS.rst', 'r').read() + open('CHANGELOG.rst', 'r').read(),
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    license='BSD',
    url='http://www.jmbo.org',
    packages = find_packages(),
    install_requires = [
        # The bare minimum requirements. The tests use explicit versions.
        "Pillow",
        "pytz",
        "django>=1.9",
        "django-category>=1.9",
        "django-layers-hr>=1.10.1",
        "django-likes>=1.11",
        "django-pagination-fork>=1.0.17",
        "django-preferences",
        "django-photologue>=3.3",
        "djangorestframework-extras>=0.2",
        "djangorestframework-jwt==1.8.0",
        "django-sites-groups>=1.9.1",
        "django-sortedm2m>=1.4.0",
        "django-ultracache>=1.10.2",
        "django-crum",
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
