from setuptools import setup, find_packages

setup(
    name='netcapt',
    version='0.1.2',
    packages=find_packages(),
    url='https://github.com/rubengm13/netcapt',
    license='GNU GPL',
    author='Ruben Gutierrez',
    author_email='rubeng318@ucla.edu',
    description='Capture Network Data from CLI output.',
    include_package_data=True,
    package_data={"netcapt": ["ntc_templates/textfsm_templates/*", "ntc_templates/templates/*"]},
    install_requires=[
        'netmiko',
        'ciscoconfparse'
    ]
)
