import setuptools

setuptools.setup(
    name="icu",
    version="0.0.2",
    description="Integrated Cognitive User Assistance",
    url="https://github.com/dicelab-rhul/ICU",
    author="Benedict Wilkins",
    author_email="benrjw@googlemail.co.uk",
    license="GNU3",
    packages=setuptools.find_packages(),
    package_data={"icu": ["*.json"]},
    include_package_data=True,
    install_requires=[],
    python_requires=">=3.10",
    extras_require={"tobii": ["tobii-research==1.11.0"]},
    classifiers=[
        "Programming Language :: Python :: 3.7",
        "Development Status :: 2 - Pre-Alpha",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
