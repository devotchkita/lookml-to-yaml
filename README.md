# LookML to Omni YAML Converter

A Streamlit app that converts Looker's LookML code to Omni-compatible YAML syntax.

## Features
- Convert dimensions, dimension_groups, and measures
- Handle complex SQL statements and timeframes
- Download converted YAML files
- Clean, intuitive interface

## Usage
1. Paste your LookML code in the left panel
2. Click "Convert to Omni"
3. Copy or download the converted YAML from the right panel

### How to run it on your own machine

1. Install the requirements

   ```
   $ pip install -r requirements.txt
   ```

2. Run the app

   ```
   $ streamlit run streamlit_app.py
   ```
