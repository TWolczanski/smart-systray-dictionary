# Installation
1. Create a Python virtual environment and activate it.

On Linux:
```
python3 -m venv .venv
source .venv/bin/activate
```
On Windows:
```
py -3 -m venv .venv
.venv\scripts\activate
```
2. Install necessary packages:

On Linux:
```
python3 -m pip install -r requirements.txt
```
On Windows:
```
python -m pip install -r requirements.txt
```

# Launching the program
On Linux:
```
python3 main.py
```
On Windows:
```
python main.py
```

# Generating documentation
```
sphinx-build -b html docs/source/ docs/build/html
```