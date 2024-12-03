# ArhamLab - Patient Report Generating Software

ArhamLab is a patient report-generating desktop application designed to streamline medical report generation and distribution processes. This software is packaged into a standalone executable using PyInstaller, making it easy to deploy without requiring users to install Python or additional dependencies.

![Logo](./assets/logo.png)

## Tech Stack

**Backend:**
Python, Jinja2

**Frontend:**
PyQt5

**PDF:**
WeasyPrint, pikepdf

**Barcode and QR Code Generation:**
python-barcode, qrcode

**Packaging and Deployment:**
PyInstaller

## Usage/Examples

#### Create a virutal environment

```bash
python -m venv env
```

#### Activate the environment

On Windows:

```bash
env\Scripts\activate
```

On macOS/Linux:

```bash
source env/bin/activate
```

#### Install the requirements

```bash
pip install -r requirements.txt

```

#### Run the app

```bash
python main.py

```

or

#### Generate the executable:

```bash
pyinstaller --name ArhamLab --onefile --windowed --icon=icon.ico --add-data "data;data" --add-data "assets;assets" --add-data "templates;templates" main.py
```

## Acknowledgements

- [License](./license.txt)
