from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="xml-editor",
    version="1.0.0",
    author="XML Editor Team",
    author_email="",
    description="A fully-featured cross-platform XML editor with XPath, validation, and schema support",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/profiluefter/xml-editor",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Text Editors",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.8",
    install_requires=[
        "PyQt6>=6.6.0",
        "PyQt6-QScintilla>=2.14.0",
        "lxml>=5.0.0",
        "pygments>=2.17.0",
    ],
    entry_points={
        "console_scripts": [
            "xml-editor=xmleditor.main:main",
        ],
        "gui_scripts": [
            "xml-editor-gui=xmleditor.main:main",
        ],
    },
    include_package_data=True,
    package_data={
        "xmleditor": [
            "resources/*",
            "resources/dist/*",
            "resources/web/dist/*",
        ],
    },
)
