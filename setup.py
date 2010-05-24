from setuptools import setup, find_packages

setup(
    name='django-content',
    version='dev',
    description='Django CMS base content app.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/django-content',
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
