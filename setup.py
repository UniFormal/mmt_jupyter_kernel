from distutils.core import setup

with open('README.md') as f:
    readme = f.read()

setup(
    name='mmt_kernel',
    version='1.0',
    packages=['mmt_kernel'],
    description='Simple example kernel for MMT',
    long_description=readme,
    author='Tom Wiesing',
    author_email='tom.wiesing@fau.de',
    url='https://github.com/UniFormal/mmt_kernel',
    install_requires=[
          'jupyter_client', 'IPython', 'ipykernel', 'requests', 'pexpect'
    ],
    classifiers=[
        'Intended Audience :: Developers',
        'License :: OSI Approved :: BSD License',
        'Programming Language :: Python :: 3',
    ],
)
