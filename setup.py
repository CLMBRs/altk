import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="altk",
    version="1.0.0",
    author="Nathaniel Imel, Shane Steinert-Threlkeld",
    author_email="nimel@uci.edu, shanest@uw.edu",
    description="The Artificial Language ToolKit",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CLMBRs/altk",
    project_urls={
        "Bug Tracker": "https://github.com/CLMBRs/altk/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "src"},
    packages=setuptools.find_packages(where="src"),
    python_requires=">=3.6",
    install_requires=["numpy","nltk","pyyaml","pandas","plotnine","pathos","embo","pytest"]
)
