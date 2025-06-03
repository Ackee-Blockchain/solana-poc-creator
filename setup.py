from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="solgen",
    version="0.1.0",
    author="Andrej",
    description="Vibe coded python tool to generate test templates for Solana audits",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Ackee-Blockchain/solana-poc-creator",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.6",
    entry_points={
        'console_scripts': [
            'solgen=solgen.generator:main',
        ],
    },
    install_requires=[
        'typing-extensions>=4.0.0',
    ],
)
