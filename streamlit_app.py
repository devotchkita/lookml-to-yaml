import streamlit as st
import re
from typing import Dict, Any, Optional, Tuple
import yaml
from io import StringIO

# Page configuration
st.set_page_config(
    page_title="LookML to Omni YAML Converter",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for better styling
st.markdown("""
<style>
    .stApp {
        background-color: #f5f7fa;
    }
    .main-header {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 2rem;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 2rem;
    }
    .stTextArea textarea {
        font-family: 'Monaco', 'Consolas', 'Courier New', monospace;
        font-size: 14px;
        background-color: #ffffff;
        border: 2px solid #e1e4e8;
        border-radius: 8px;
    }
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        padding: 0.5rem 2rem;
        font-weight: 600;
        border-radius: 8px;
        transition: all 0.3s ease;
    }
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 5px 15px rgba(0,0,0,0.2);
    }
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 0.5rem;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 2.5rem;">LookML to Omni YAML Converter</h1>
    <p style="margin: 0.5rem 0 0 0; opacity: 0.9;">Transform your Looker LookML code into Omni-compatible YAML syntax</p>
</div>
""", unsafe_allow_html=True)

class LookMLToOmniConverter:
    """Converter class for transforming LookML to Omni YAML format"""
    
    def __init__(self):
        self.property_mappings = {
            'hidden': self._map_hidden,
            'primary_key': self._map_primary_key,
            'value_format_name': self._map_value_format,
            'type': self._map_type,
        }
        
    def _map_hidden(self, value: Any) -> Optional[Dict[str, Any]]:
        """Map hidden property to tags"""
        if value == 'no' or value is False:
            return {'tags': ['business_facing']}
        return None
    
    def _map_primary_key(self, value: Any) -> Optional[Dict[str, Any]]:
        """Map primary_key property"""
        if value == 'yes' or value is True:
            return {'primary_key': True}
        return None
    
    def _map_value_format(self, value: str) -> Dict[str, Any]:
        """Map value_format_name to format"""
        format_mappings = {
            'decimal_0': 'NUMBER',
            'decimal_1': 'NUMBER',
            'decimal_2': 'NUMBER',
            'percent_0': 'PERCENT',
            'percent_1': 'PERCENT',
            'percent_2': 'PERCENT',
            'usd': 'CURRENCY',
            'eur': 'CURRENCY',
        }
        return {'format': format_mappings.get(value, value.upper())}
    
    def _map_type(self, value: str, object_type: str) -> Optional[Dict[str, Any]]:
        """Map type property based on object type"""
        if object_type == 'measure':
            aggregate_mappings = {
                'count': 'count',
                'count_distinct': 'count_distinct',
                'sum': 'sum',
                'average': 'avg',
                'avg': 'avg',
                'max': 'max',
                'min': 'min',
                'median': 'median',
            }
            if value in aggregate_mappings:
                return {'aggregate_type': aggregate_mappings[value]}
        elif value == 'yesno':
            return {'type': 'boolean'}
        return None
    
    def parse_lookml(self, lookml_code: str) -> Dict[str, Any]:
        """Parse LookML code and convert to structured format"""
        lines = lookml_code.split('\n')
        result = {
            'dimensions': {},
            'dimension_groups': {},
            'measures': {}
        }
        
        current_object = None
        current_type = None
        current_props = {}
        in_timeframes = False
        timeframes_list = []
        in_case = False
        case_depth = 0
        
        for line in lines:
            trimmed = line.strip()
            
            # Skip empty lines and comments
            if not trimmed or trimmed.startswith('#'):
                continue
            
            # Check for object declarations
            dimension_match = re.match(r'^dimension:\s*(\w+)\s*{', trimmed)
            dimension_group_match = re.match(r'^dimension_group:\s*(\w+)\s*{', trimmed)
            measure_match = re.match(r'^measure:\s*(\w+)\s*{', trimmed)
            
            if dimension_match:
                if current_object and current_type:
                    self._save_object(result, current_type, current_object, current_props)
                current_object = dimension_match.group(1)
                current_type = 'dimension'
                current_props = {}
            elif dimension_group_match:
                if current_object and current_type:
                    self._save_object(result, current_type, current_object, current_props)
                current_object = dimension_group_match.group(1)
                current_type = 'dimension_group'
                current_props = {}
            elif measure_match:
                if current_object and current_type:
                    self._save_object(result, current_type, current_object, current_props)
                current_object = measure_match.group(1)
                current_type = 'measure'
                current_props = {}
            elif trimmed == '}':
                if in_case and case_depth > 0:
                    case_depth -= 1
                    if case_depth == 0:
                        in_case = False
                elif in_timeframes:
                    in_timeframes = False
                    current_props['timeframes'] = timeframes_list
                    timeframes_list = []
            elif trimmed == 'case: {':
                in_case = True
                case_depth = 1
            elif in_case:
                if '{' in trimmed:
                    case_depth += 1
                # Skip case content for now
                continue
            elif trimmed == 'timeframes: [':
                in_timeframes = True
            elif in_timeframes:
                # Extract timeframe values
                tf_match = re.match(r'^(\w+),?$', trimmed)
                if tf_match:
                    timeframes_list.append(tf_match.group(1))
            elif current_object:
                # Parse property lines
                prop = self._parse_property(trimmed)
                if prop:
                    key, value = prop
                    current_props[key] = value
        
        # Save last object
        if current_object and current_type:
            self._save_object(result, current_type, current_object, current_props)
        
        return result
    
    def _parse_property(self, line: str) -> Optional[Tuple[str, Any]]:
        """Parse a property line"""
        # Handle timeframes array in single line
        timeframes_match = re.match(r'timeframes:\s*\[(.*?)\]', line)
        if timeframes_match:
            timeframes = [t.strip() for t in timeframes_match.group(1).split(',')]
            return ('timeframes', timeframes)
        
        # Handle regular properties
        match = re.match(r'^(\w+):\s*(.+?)(?:\s*;;)?$', line)
        if match:
            key = match.group(1)
            value = match.group(2).strip()
            
            # Remove trailing semicolons
            value = re.sub(r'\s*;;\s*$', '', value)
            
            # Handle quoted values
            if value.startswith('"') and value.endswith('"'):
                value = value[1:-1]
            
            # Convert boolean values
            if value in ('yes', 'true'):
                value = True
            elif value in ('no', 'false'):
                value = False
            
            return (key, value)
        
        return None
    
    def _save_object(self, result: Dict, obj_type: str, name: str, props: Dict[str, Any]):
        """Save parsed object to result"""
        plural_type = obj_type + 's'
        if obj_type == 'dimension_group':
            plural_type = 'dimensions'  # dimension_groups go under dimensions in the output
        
        converted_props = {}
        
        for key, value in props.items():
            # Apply property mappings
            if key in self.property_mappings:
                if key == 'type':
                    mapped = self.property_mappings[key](value, obj_type)
                else:
                    mapped = self.property_mappings[key](value)
                if mapped:
                    converted_props.update(mapped)
                    if key != 'type' or obj_type != 'measure':
                        continue
            
            # Skip certain properties
            if key in ('drill_fields', 'case'):
                continue
            
            # Direct mappings
            if key == 'sql':
                # Clean up SQL references
                sql_value = value
                if not sql_value.startswith('"'):
                    sql_value = f'"{sql_value}"'
                converted_props[key] = sql_value
            else:
                converted_props[key] = value
        
        # Add group_label for dimension_groups
        if obj_type == 'dimension_group':
            if 'group_label' not in converted_props:
                # Capitalize first letter of each word
                label = ' '.join(word.capitalize() for word in name.split('_'))
                converted_props['group_label'] = label
        
        result[plural_type][name] = converted_props
    
    def convert_to_yaml(self, parsed_data: Dict[str, Any]) -> str:
        """Convert parsed data to YAML format"""
        output = []
        
        # Process dimensions and dimension_groups
        if parsed_data['dimensions'] or parsed_data['dimension_groups']:
            output.append('dimensions:')
            
            # Add regular dimensions
            for name, props in parsed_data['dimensions'].items():
                output.append(f'  {name}:')
                output.extend(self._format_properties(props, 4))
                output.append('')
            
            # Add dimension groups
            for name, props in parsed_data['dimension_groups'].items():
                output.append(f'  {name}:')
                output.extend(self._format_properties(props, 4))
                output.append('')
        
        # Process measures
        if parsed_data['measures']:
            if output:
                output.append('')
            output.append('measures:')
            for name, props in parsed_data['measures'].items():
                output.append(f'  {name}:')
                output.extend(self._format_properties(props, 4))
                output.append('')
        
        return '\n'.join(output).rstrip() + '\n'
    
    def _format_properties(self, props: Dict[str, Any], indent: int) -> list:
        """Format properties as YAML lines"""
        lines = []
        indent_str = ' ' * indent
        
        # Property order for better organization
        property_order = [
            'sql', 'label', 'tags', 'format', 'description', 
            'display_order', 'group_label', 'primary_key', 
            'aggregate_type', 'timeframes'
        ]
        
        # Add ordered properties first
        for key in property_order:
            if key in props:
                lines.extend(self._format_property(key, props[key], indent))
        
        # Add remaining properties
        for key, value in props.items():
            if key not in property_order:
                lines.extend(self._format_property(key, value, indent))
        
        return lines
    
    def _format_property(self, key: str, value: Any, indent: int) -> list:
        """Format a single property"""
        indent_str = ' ' * indent
        lines = []
        
        if isinstance(value, list):
            if key == 'timeframes':
                lines.append(f'{indent_str}{key}:')
                lines.append(f'{indent_str}  [')
                for i, item in enumerate(value):
                    suffix = ',' if i < len(value) - 1 else ''
                    lines.append(f'{indent_str}    {item}{suffix}')
                lines.append(f'{indent_str}  ]')
            else:
                lines.append(f'{indent_str}{key}: [ {", ".join(map(str, value))} ]')
        elif isinstance(value, bool):
            lines.append(f'{indent_str}{key}: {str(value).lower()}')
        elif isinstance(value, str):
            # Handle multiline descriptions
            if key == 'description' and len(value) > 60:
                lines.append(f'{indent_str}{key}: |')
                lines.append(f'{indent_str}  {value}')
            else:
                lines.append(f'{indent_str}{key}: {value}')
        else:
            lines.append(f'{indent_str}{key}: {value}')
        
        return lines

# Initialize converter
converter = LookMLToOmniConverter()

# Create two columns for input and output
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.subheader("📝 LookML Input")
    lookml_input = st.text_area(
        "Paste your LookML code here:",
        height=500,
        placeholder="""Example:
dimension: parking_action_id {
  label: "Parking Action ID"
  description: "Id of the parking action"
  hidden: no
  primary_key: yes
  type: string
  sql: ${TABLE}.parking_action_id ;;
}""",
        key="lookml_input"
    )

with col2:
    st.subheader("📄 Omni YAML Output")
    omni_output_placeholder = st.empty()

# Buttons row
button_col1, button_col2, button_col3 = st.columns([2, 1, 1], gap="small")

with button_col1:
    convert_button = st.button("🔄 Convert to Omni", type="primary", use_container_width=True)

with button_col2:
    clear_button = st.button("🗑️ Clear All", use_container_width=True)

with button_col3:
    # Create a placeholder for the copy button feedback
    copy_feedback = st.empty()

# Handle conversion
if convert_button and lookml_input:
    try:
        # Parse and convert
        parsed_data = converter.parse_lookml(lookml_input)
        omni_yaml = converter.convert_to_yaml(parsed_data)
        
        # Display output
        with col2:
            st.text_area(
                "Converted YAML:",
                value=omni_yaml,
                height=500,
                key="omni_output"
            )
            
            # Download button
            st.download_button(
                label="📥 Download YAML",
                data=omni_yaml,
                file_name="omni_config.yaml",
                mime="text/yaml"
            )
        
        st.success("✅ Conversion successful!")
        
    except Exception as e:
        st.error(f"❌ Error during conversion: {str(e)}")

# Handle clear button
if clear_button:
    st.rerun()

# Show example in sidebar
with st.sidebar:
    st.header("📚 How to Use")
    st.markdown("""
    1. **Paste** your LookML code in the left editor
    2. **Click** "Convert to Omni" button
    3. **Copy** or download the converted YAML
    
    ### Supported Conversions:
    - ✅ Dimensions
    - ✅ Dimension Groups
    - ✅ Measures
    - ✅ Property mappings
    - ✅ SQL field references
    - ✅ Timeframes
    - ✅ Boolean conversions
    
    ### Property Mappings:
    - `hidden: no` → `tags: [business_facing]`
    - `type: yesno` → boolean
    - `value_format_name` → `format`
    - Measure types → `aggregate_type`
    """)
    
    st.header("💡 Example")
    if st.button("Load Example"):
        st.session_state.lookml_input = """dimension: parking_action_id {
  label: "Parking Action ID"
  description: "Id of the parking action"
  hidden: no
  primary_key: yes
  type: string
  sql: ${TABLE}.parking_action_id ;;
}

dimension_group: checkin {
  type: time
  sql: ${TABLE}.checkin_at ;;
  timeframes: [
    raw,
    year,
    month,
    date,
    hour
  ]
}

measure: count {
  label: "Count (Total)"
  type: count
  drill_fields: [pa_drill*]
}"""
        st.rerun()

# Footer
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        Built with ❤️ using Streamlit | LookML to Omni YAML Converter
    </div>
    """,
    unsafe_allow_html=True
)
