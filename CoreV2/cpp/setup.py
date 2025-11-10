from setuptools import setup, Extension
import pybind11

ext_modules = [
    Extension(
        'your_module_name',
        ['your_source_file.cpp'],

        include_dirs=[pybind11.get_include()],
        language='c++'
    )
]

setup(
    name='CoreV2_cpp',
    version='0.0.1',
    author='Your Name',
    ext_modules=ext_modules
)