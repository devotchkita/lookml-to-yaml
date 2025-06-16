import streamlit as st
import re
from typing import Dict, Any, Optional, Tuple

# Page configuration
st.set_page_config(
    page_title="LookML to Omni YAML Converter - Tasman",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS following Tasman brand guidelines
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto+Mono:wght@400&display=swap');
    
    /* Background color from Tasman palette */
    .stApp {
        background-color: #fff9eb;
    }
    
    /* Main header with Tasman black */
    .main-header {
        background: #000000;
        padding: 3rem;
        border-radius: 0;
        color: #ffffff;
        text-align: center;
        margin-bottom: 3rem;
        position: relative;
    }
    
    /* Grid overlay effect */
    .main-header::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        bottom: 0;
        background-image: 
            linear-gradient(rgba(255,255,255,0.1) 1px, transparent 1px),
            linear-gradient(90deg, rgba(255,255,255,0.1) 1px, transparent 1px);
        background-size: 50px 50px;
        pointer-events: none;
    }
    
    /* Typography following Tasman guidelines */
    h1 {
        font-family: Georgia, serif;
        letter-spacing: -0.02em;
        line-height: 1.1;
        font-weight: normal;
    }
    
    .stSubheader {
        font-family: Georgia, serif;
        color: #000000;
        letter-spacing: -0.02em;
        font-size: 1.8rem;
        margin-bottom: 1rem;
    }
    
    /* Text areas with Tasman styling */
    .stTextArea textarea {
        font-family: 'Roboto Mono', monospace;
        font-size: 14px;
        background-color: #ffffff;
        border: 1px solid #cccccc;
        border-radius: 0;
        color: #000000;
        line-height: 1.4;
    }
    
    .stTextArea textarea:focus {
        border-color: #595959;
        box-shadow: none;
    }
    
    /* Buttons following Tasman design */
    .stButton > button {
        background: #000000;
        color: #ffffff;
        border: none;
        padding: 0.75rem 2rem;
        font-family: 'Roboto Mono', monospace;
        font-size: 0.875rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        border-radius: 0;
        transition: all 0.2s ease;
        position: relative;
        overflow: hidden;
    }
    
    .stButton > button:hover {
        background: #595959;
        transform: none;
        box-shadow: none;
    }
    
    /* Primary button with accent color */
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button {
        background: #000000;
    }
    
    div[data-testid="stHorizontalBlock"] > div:first-child .stButton > button:hover {
        background: #536476;
    }
    
    /* Secondary buttons */
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button,
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button {
        background: #ffffff;
        color: #000000;
        border: 1px solid #000000;
    }
    
    div[data-testid="stHorizontalBlock"] > div:nth-child(2) .stButton > button:hover,
    div[data-testid="stHorizontalBlock"] > div:nth-child(3) .stButton > button:hover {
        background: #000000;
        color: #ffffff;
    }
    
    /* Column spacing */
    div[data-testid="stHorizontalBlock"] > div {
        padding: 0 0.5rem;
    }
    
    /* Success/Error messages with Tasman colors */
    .stSuccess {
        background-color: rgba(144, 179, 157, 0.1);
        color: #536476;
        border-left: 4px solid #90b39d;
    }
    
    .stError {
        background-color: rgba(158, 48, 36, 0.1);
        color: #9e3024;
        border-left: 4px solid #9e3024;
    }
    
    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: #ffffff;
        border-right: 1px solid #cccccc;
    }
    
    section[data-testid="stSidebar"] h1,
    section[data-testid="stSidebar"] h2,
    section[data-testid="stSidebar"] h3 {
        font-family: Georgia, serif;
        color: #000000;
        letter-spacing: -0.02em;
    }
    
    /* Download button with Tasman accent */
    .stDownloadButton > button {
        background: #90b39d;
        color: #000000;
        border: none;
        font-family: 'Roboto Mono', monospace;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        font-size: 0.875rem;
    }
    
    .stDownloadButton > button:hover {
        background: #536476;
        color: #ffffff;
    }
    
    /* Grid pattern for sections */
    .grid-section {
        position: relative;
        padding: 2rem;
        margin: 2rem 0;
    }
    
    .grid-section::before {
        content: "";
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 1px;
        background: #cccccc;
    }
</style>
""", unsafe_allow_html=True)

# Header with Tasman branding
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 3rem; font-weight: normal;">TASMAN</h1>
    <p style="margin: 1rem 0 0 0; font-family: 'Roboto Mono', monospace; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8;">LOOKML TO OMNI YAML CONVERTER</p>
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
        in_sql = False
        sql_lines = []
        sql_key = None
        
        for i, line in enumerate(lines):
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
                # Check if we're in a multi-line SQL statement
                if in_sql:
                    # Check if this line ends the SQL statement
                    if trimmed.endswith(';;'):
                        sql_lines.append(line.rstrip())
                        # Join all SQL lines and clean up
                        full_sql = ' '.join(sql_lines)
                        full_sql = re.sub(r'\s*;;\s*$', '', full_sql)
                        full_sql = re.sub(r'^sql:\s*', '', full_sql).strip()
                        current_props[sql_key] = full_sql
                        in_sql = False
                        sql_lines = []
                        sql_key = None
                    else:
                        sql_lines.append(line.rstrip())
                else:
                    # Check if this line starts a SQL statement
                    sql_match = re.match(r'^(sql(?:_\w+)?):\s*(.*)$', trimmed)
                    if sql_match:
                        sql_key = sql_match.group(1)
                        sql_value = sql_match.group(2)
                        
                        # Check if it's a complete SQL statement
                        if sql_value.endswith(';;'):
                            sql_value = re.sub(r'\s*;;\s*$', '', sql_value)
                            current_props[sql_key] = sql_value
                        else:
                            # Start of multi-line SQL
                            in_sql = True
                            sql_lines = [f"{sql_key}: {sql_value}"]
                    else:
                        # Parse regular property lines
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
        
        # First, handle SQL field which is critical
        if 'sql' in props:
            converted_props['sql'] = f'"{props["sql"]}"'
        
        # Apply property mappings
        for key, value in props.items():
            if key == 'sql':
                continue  # Already handled
                
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
            if key.startswith('sql_'):
                converted_props[key] = f'"{value}"'
            elif key not in ['hidden', 'type', 'value_format_name', 'primary_key']:
                converted_props[key] = value
        
        # Add required metadata with defaults if not present
        if obj_type in ['dimension', 'dimension_group']:
            # Ensure label exists
            if 'label' not in converted_props:
                # Generate label from name
                converted_props['label'] = ' '.join(word.capitalize() for word in name.split('_'))
            
            # Add group_label
            if 'group_label' not in converted_props:
                if obj_type == 'dimension_group':
                    converted_props['group_label'] = ' '.join(word.capitalize() for word in name.split('_'))
                else:
                    # Try to infer group from name or use a default
                    parts = name.split('_')
                    if len(parts) > 1:
                        converted_props['group_label'] = parts[0].capitalize()
                    else:
                        converted_props['group_label'] = 'Dimensions'
            
            # Add description if not present
            if 'description' not in converted_props:
                converted_props['description'] = f"Description for {converted_props['label']}"
            
            # Handle hidden property
            if 'hidden' in props and props['hidden'] in ['yes', True]:
                converted_props['hidden'] = 'yes'
            else:
                # If hidden was 'no' or not specified, add business_facing tag
                if 'tags' not in converted_props:
                    converted_props['tags'] = ['business_facing']
                converted_props['hidden'] = 'no'
                
        elif obj_type == 'measure':
            # For measures, ensure we have aggregate_type
            if 'aggregate_type' not in converted_props:
                # Try to infer from type or name
                if 'type' in props:
                    measure_type = props['type']
                    if measure_type in ['count', 'count_distinct', 'sum', 'average', 'max', 'min', 'median']:
                        converted_props['aggregate_type'] = 'avg' if measure_type == 'average' else measure_type
                    else:
                        converted_props['aggregate_type'] = 'sum'  # default
                else:
                    converted_props['aggregate_type'] = 'sum'  # default
            
            # Ensure label exists
            if 'label' not in converted_props:
                converted_props['label'] = ' '.join(word.capitalize() for word in name.split('_'))
            
            # Add group_label
            if 'group_label' not in converted_props:
                # Try to infer from name
                parts = name.split('_')
                if len(parts) > 1 and parts[0] in ['sum', 'count', 'avg', 'max', 'min']:
                    converted_props['group_label'] = ' '.join(word.capitalize() for word in parts[1:])
                else:
                    converted_props['group_label'] = 'Measures'
        
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
            'sql', 'label', 'group_label', 'description', 'hidden',
            'tags', 'format', 'display_order', 'primary_key', 
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
    st.markdown('<h2 style="font-family: Georgia, serif; font-size: 1.8rem; color: #000; letter-spacing: -0.02em; margin-bottom: 1rem;">LookML Input</h2>', unsafe_allow_html=True)
    lookml_input = st.text_area(
        "Paste your LookML code here:",
        height=500,
        placeholder="""Example:
dimension: marketing_channel {
  label: "Marketing Channel"
  description: "Channel where the activity occurred"
  hidden: no
  type: string
  sql: ${TABLE}.marketing_channel ;;
}""",
        key="lookml_input",
        label_visibility="collapsed"
    )

with col2:
    st.markdown('<h2 style="font-family: Georgia, serif; font-size: 1.8rem; color: #000; letter-spacing: -0.02em; margin-bottom: 1rem;">Omni YAML Output</h2>', unsafe_allow_html=True)
    omni_output_placeholder = st.empty()

# Buttons row
button_col1, button_col2, button_col3 = st.columns([2, 1, 1], gap="small")

with button_col1:
    convert_button = st.button("CONVERT TO OMNI", type="primary", use_container_width=True)

with button_col2:
    clear_button = st.button("CLEAR ALL", use_container_width=True)

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
                key="omni_output",
                label_visibility="collapsed"
            )
            
            # Download button
            st.download_button(
                label="DOWNLOAD YAML",
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
    st.markdown('<h2 style="font-family: Georgia, serif; font-size: 1.5rem; color: #000; letter-spacing: -0.02em;">How to Use</h2>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #595959; line-height: 1.4;">
    <ol>
        <li style="margin-bottom: 0.5rem;"><strong>Paste</strong> your LookML code in the left editor</li>
        <li style="margin-bottom: 0.5rem;"><strong>Click</strong> "CONVERT TO OMNI" button</li>
        <li style="margin-bottom: 0.5rem;"><strong>Copy</strong> or download the converted YAML</li>
    </ol>
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-family: Georgia, serif; font-size: 1.3rem; color: #000; letter-spacing: -0.02em; margin-top: 2rem;">Supported Conversions</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Roboto Mono', monospace; font-size: 0.875rem; color: #595959;">
    ✓ Dimensions<br>
    ✓ Dimension Groups<br>
    ✓ Measures<br>
    ✓ Property mappings<br>
    ✓ SQL field references<br>
    ✓ Timeframes<br>
    ✓ Boolean conversions
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown('<h3 style="font-family: Georgia, serif; font-size: 1.3rem; color: #000; letter-spacing: -0.02em; margin-top: 2rem;">Property Mappings</h3>', unsafe_allow_html=True)
    st.markdown("""
    <div style="font-family: 'Roboto Mono', monospace; font-size: 0.8rem; color: #595959; line-height: 1.6;">
    • hidden: no → tags: [business_facing]<br>
    • type: yesno → boolean<br>
    • value_format_name → format<br>
    • measure types → aggregate_type
    </div>
    """, unsafe_allow_html=True)
    
    st.markdown("---")
    st.markdown('<h3 style="font-family: Georgia, serif; font-size: 1.3rem; color: #000; letter-spacing: -0.02em;">Example</h3>', unsafe_allow_html=True)
    if st.button("LOAD EXAMPLE", use_container_width=True):
        st.session_state.lookml_input = """dimension: marketing_channel {
  label: "Marketing Channel"
  description: "Channel where the activity occurred"
  hidden: no
  type: string
  sql: ${TABLE}.marketing_channel ;;
}

dimension: status {
  description: "Status of the parking action"
  hidden: no
  type: string
  sql: case
          when ${TABLE}.parking_action_status = 'Open' or ${TABLE}.checkout_at is null then 'Open'
          else ${TABLE}.parking_action_status
        end;;
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
}

measure: sum_queued_cxp {
  type: sum
  sql: ${queued_cxp} ;;
  label: "Total Queued CXP"
}"""
        st.rerun()

# Footer
st.markdown("---")
footer_html = """<div style='text-align: center; color: #595959; font-family: Roboto Mono, monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; padding: 2rem 0;'>
    TASMAN • DATA TRANSFORMATION TOOLS
</div>"""
st.markdown(footer_html, unsafe_allow_html=True)
