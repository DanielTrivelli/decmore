from setuptools import setup

extras_require = {
    "doc": [
        "Sphinx>=1.6.5,<2",
        "sphinx_rtd_theme>=0.1.9",
    ],
}

install_requires = [
    "numpy~=1.26.1"
]

setup(
    name="decmore",
    use_scm_version={"version_scheme": "post-release"},
    setup_requires=["setuptools_scm"],
    url="https://github.com/DanielTrivelli/decmore",
    license="MIT",
    description="Useful decorators for your application.",
    author="Daniel Trivelli",
    author_email="drtrivelli@gmail.com",
    python_requires=">=3.7",
    install_requires=install_requires,
    extras_require=extras_require,
    include_package_data=True,
    zip_safe=False,
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Topic :: Software Development :: Libraries"
    ],
)