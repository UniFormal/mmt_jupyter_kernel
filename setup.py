from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='mmt_kernel',
    version='1.0',
    packages=['mmt_kernel'],
    package_data={
        'mmt_kernel' : ['unicode-latex-map']
    },
    description='Simple example kernel for MMT',
    long_description=readme,
    author='Tom Wiesing',
    author_email='tom.wiesing@fau.de',
    url='https://github.com/UniFormal/mmt_kernel',
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ]
    
)
