# Solana PoC Template generator

Vibe coded python tool to generate test templates for Solana audits

The package is not released yet, but you can install it from this repository.


This tool will create Typescript template from IDL file.

## Install

(Optional) Create a virtual environment

```bash
python3 -m venv ./audit-tests
source ./audit-tests/bin/activate
```

Install the package

```bash
pip install git+https://github.com/Ackee-Blockchain/solana-poc-creator.git@master
```

## Usage

```bash
solgen <IDL_PATH> <OUTPUT_DIR>
```
