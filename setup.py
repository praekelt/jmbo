from setuptools import setup, find_packages

setup(
    name='django-content',
    version='dev',
    description='Django CMS base content app.',
    author='Praekelt Consulting',
    author_email='dev@praekelt.com',
    url='https://github.com/praekelt/django-content',
    packages = find_packages(),
    include_package_data=True,
)
