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
        'http://dist.repoze.org/',
    ],
    install_requires = [
        'PIL==1.1.6',
        'django-photologue==2.3',
        'django-tagging==0.3.1',
        'django-tagging-autocomplete==0.3.1',
    ],
    include_package_data=True,
)
