# Installation
1. Create a Python virtual environment and activate it:
```
python3 -m venv .venv
source .venv/bin/activate
```
2. Install necessary packages:
```
python3 -m pip install -r requirements.txt
```

# Launching the program
```
source .venv/bin/activate
python3 main.py
```

# Generating documentation
```
sphinx-build -b html docs/source/ docs/build/html
```