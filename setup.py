import setuptools
from pathlib import Path


def readme():
    return Path(__file__).parent.absolute().joinpath('README.md').read_text()


setuptools.setup(
    name='streamlit-chatbox',
    version='0.2.1',
    author='liunux',
    author_email='liunux@qq.com',
    description='A chat box used in streamlit',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/liunux4odoo/streamlit-chatbox',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires='>=3.6',
    install_requires=[
                'streamlit',
    ]
)
