from setuptools import setup, find_packages

setup(
    name='panya',
    version='dev',
    description='Panya Base CMS App.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/panya',
    packages = find_packages(),
    dependency_links = [
        'http://dist.plone.org/thirdparty/',
    ],
    install_requires = [
        'PIL>=1.1.6',
        'django-tagging>=0.3.1',
        'django-secretballot>=0.2.3',
    ],
    include_package_data=True,
)
