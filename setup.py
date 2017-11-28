import io
from setuptools import setup

setup(
    name='django-cmd',
    description='Get a django command',
    long_description=io.open('README.rst', encoding='utf-8').read(),
    author='Ryan Hiebert',
    author_email='ryan@ryanhiebert.com',
    url='https://github.com/ryanhiebert/django-cmd',
    license='MIT',
    version='1.0',
    package_dir={'': 'src'},
    py_modules=['django_cmd'],
    install_requires=['Django'],
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Framework :: Django :: 1.8',
        'Framework :: Django :: 1.10',
        'Framework :: Django :: 1.11',
        'Framework :: Django :: 2.0',
    ],
    entry_points={
        'console_scripts': [
            'django = django_cmd:main',
        ],
    },
)
