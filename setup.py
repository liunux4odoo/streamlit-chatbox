import setuptools
from pathlib import Path


def readme():
    readme = Path(__file__).parent.absolute().joinpath('README.md')
    return readme.read_text("utf-8")


setuptools.setup(
    name='streamlit-chatbox',
    version='1.1.11',
    author='liunux',
    author_email='liunux@qq.com',
    description='A chat box and some helpful tools used to build chatbot app with streamlit',
    long_description=readme(),
    long_description_content_type='text/markdown',
    url='https://github.com/liunux4odoo/streamlit-chatbox',
    packages=setuptools.find_packages(),
    include_package_data=True,
    classifiers=[],
    python_requires='>=3.8',
    install_requires=[
        'streamlit>=1.26.0',
        'simplejson',
        'streamlit-feedback',
    ]
)
