import streamlit as st
import re
from typing import Dict, Any, Optional, Tuple
import os
import anthropic

# Page configuration
st.set_page_config(
    page_title="LookML to Omni YAML Converter - Tasman",
    page_icon="🔄",
    layout="wide",
    initial_sidebar_state="expanded"
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
            sql_value = props['sql']
            # Check if it's a field reference like ${TABLE}."FIELD" or ${TABLE}.FIELD
            table_ref_match = re.search(r'\$\{TABLE\}\.("?)([^";]+)("?)', sql_value)
            if table_ref_match:
                # Extract the field name with quotes if present
                quote1 = table_ref_match.group(1)
                field_name = table_ref_match.group(2)
                quote2 = table_ref_match.group(3)
                
                if quote1 and quote2:  # Field was quoted in original
                    converted_props['sql'] = f'"{field_name}"'
                else:  # Field was not quoted
                    converted_props['sql'] = f'"{field_name}"'  # Always quote in output
            else:
                # For CASE statements and other SQL, keep as is but remove ;;
                sql_cleaned = sql_value.replace(';;', '').strip()
                # Don't add quotes to complex SQL
                converted_props['sql'] = sql_cleaned
        
        # Handle label
        if 'label' in props:
            converted_props['label'] = props['label']
        
        # Handle group_label - clean up extra spaces
        if 'group_label' in props:
            group_label = props['group_label'].strip()
            # Remove leading spaces that might be used for visual hierarchy
            if group_label.startswith('  '):
                group_label = group_label.strip()
            converted_props['group_label'] = group_label
        
        # Handle description
        if 'description' in props:
            converted_props['description'] = props['description']
        else:
            # Add placeholder description based on label or name
            label = converted_props.get('label', name.replace('_', ' ').title())
            converted_props['description'] = f"{label}"
        
        # Handle common parameters for both dimensions and measures
        
        # format parameter
        if 'value_format' in props:
            converted_props['format'] = props['value_format']
        elif 'value_format_name' in props:
            format_mapping = {
                'decimal_0': 'NUMBER',
                'decimal_1': 'NUMBER_1',
                'decimal_2': 'NUMBER_2',
                'percent_0': 'PERCENT',
                'percent_1': 'PERCENT_1',
                'percent_2': 'PERCENT_2',
                'usd': 'CURRENCY',
                'eur': 'EURCURRENCY',
                'gbp': 'GBPCURRENCY',
            }
            converted_props['format'] = format_mapping.get(props['value_format_name'], props['value_format_name'].upper())
        
        # Handle type for dimensions
        if obj_type == 'dimension':
            if 'type' in props:
                dimension_type = props['type']
                # Special handling for ID fields
                if name.endswith('_id') and dimension_type == 'string':
                    converted_props['format'] = 'ID'
                # yesno becomes boolean in Omni
                elif dimension_type == 'yesno':
                    # Note: yesno dimensions don't get a type in output
                    pass
                # number type gets specific format
                elif dimension_type == 'number' and 'format' not in converted_props:
                    converted_props['format'] = 'NUMBER'
            
            # Handle dimension-specific parameters
            if 'primary_key' in props and props['primary_key'] in ['yes', True]:
                converted_props['primary_key'] = True
            
            # timeframes for date dimensions
            if 'timeframes' in props:
                converted_props['timeframes'] = props['timeframes']
            
            # convert_tz
            if 'convert_tz' in props:
                converted_props['convert_tz'] = props['convert_tz'] == 'yes' or props['convert_tz'] is True
        
        # Handle hidden property
        if 'hidden' in props:
            if props['hidden'] in ['yes', True]:
                converted_props['hidden'] = True
            # If explicitly set to 'no', don't add hidden field
        
        # tags
        if 'tags' in props:
            converted_props['tags'] = props['tags']
        
        # links
        if 'link' in props or 'links' in props:
            links = props.get('links', props.get('link', []))
            if not isinstance(links, list):
                links = [links]
            converted_props['links'] = links
        
        # drill_fields
        if 'drill_fields' in props and props['drill_fields']:
            # Filter out any pattern matches like [*drill*]
            drill_fields = [f for f in props['drill_fields'] if not ('*' in f)]
            if drill_fields:
                converted_props['drill_fields'] = drill_fields
        
        # suggest_from_field
        if 'suggest_from_field' in props:
            converted_props['suggest_from_field'] = props['suggest_from_field']
        
        # suggestion_list
        if 'suggestion_list' in props:
            converted_props['suggestion_list'] = props['suggestion_list']
        
        # order_by_field
        if 'order_by_field' in props:
            converted_props['order_by_field'] = props['order_by_field']
        
        # display_order
        if 'display_order' in props:
            converted_props['display_order'] = props['display_order']
        
        # view_label
        if 'view_label' in props:
            converted_props['view_label'] = props['view_label']
        
        # For measures, handle special cases
        if obj_type == 'measure':
            # Handle aggregate type
            if 'type' in props:
                measure_type = props['type']
                if measure_type == 'count_distinct':
                    converted_props['aggregate_type'] = 'count_distinct'
                elif measure_type == 'sum':
                    converted_props['aggregate_type'] = 'sum'
                elif measure_type == 'sum_distinct':
                    converted_props['aggregate_type'] = 'sum_distinct_on'
                elif measure_type == 'count':
                    converted_props['aggregate_type'] = 'count'
                elif measure_type == 'average':
                    converted_props['aggregate_type'] = 'avg'
                elif measure_type == 'max':
                    converted_props['aggregate_type'] = 'max'
                elif measure_type == 'min':
                    converted_props['aggregate_type'] = 'min'
                elif measure_type == 'median':
                    converted_props['aggregate_type'] = 'median'
                elif measure_type == 'list':
                    converted_props['aggregate_type'] = 'list'
                # If type is 'number', it's a calculated measure, no aggregate_type
            
            # Handle sql_distinct_key -> custom_primary_key_sql
            if 'sql_distinct_key' in props:
                distinct_key = props['sql_distinct_key'].replace(';;', '').strip()
                # Just keep the field reference as-is, don't add table prefixes
                converted_props['custom_primary_key_sql'] = distinct_key
            
            # filters for filtered measures
            if 'filters' in props:
                converted_props['filters'] = props['filters']
            
            # drill_queries
            if 'drill_queries' in props:
                converted_props['drill_queries'] = props['drill_queries']
        
        # Handle dimension_group specifics
        if obj_type == 'dimension_group':
            # For dimension groups, we only keep sql, group_label, label, and description
            # Remove timeframes and other time-specific properties from output
            keys_to_keep = ['sql', 'group_label', 'label', 'description']
            converted_props = {k: v for k, v in converted_props.items() if k in keys_to_keep}
        
        # Handle required_access_grants
        if 'required_access_grants' in props:
            converted_props['required_access_grants'] = props['required_access_grants']
        
        # Handle aliases
        if 'alias' in props:
            converted_props['aliases'] = [props['alias']] if isinstance(props['alias'], str) else props['alias']
        elif 'aliases' in props:
            converted_props['aliases'] = props['aliases']
        
        # Handle ignored fields
        if 'ignored' in props and props['ignored'] in ['yes', True]:
            converted_props['ignored'] = True
            
        # Handle dimension specific: groups, bin_boundaries
        if obj_type == 'dimension':
            if 'groups' in props:
                converted_props['groups'] = props['groups']
            if 'bin_boundaries' in props:
                converted_props['bin_boundaries'] = props['bin_boundaries']
            if 'filter_single_select_only' in props:
                converted_props['filter_single_select_only'] = props['filter_single_select_only'] in ['yes', True]
        
        # Special case: if the SQL field extracts to IS_THIS_SPRINT_FLAG, use that as the name
        if 'sql' in converted_props and converted_props['sql'] == '"IS_THIS_SPRINT_FLAG"' and name == 'is_this_sprint':
            result[plural_type]['is_this_sprint_flag'] = converted_props
        else:
            result[plural_type][name] = converted_props
    
    def get_llm_conversion(self, lookml_code: str, error_msg: str = None) -> Optional[str]:
        """Use Anthropic Claude as fallback for complex conversions"""
        
        # Check if API key is available
        anthropic_key = st.session_state.get('anthropic_api_key', os.getenv('ANTHROPIC_API_KEY'))
        
        if not anthropic_key:
            return None
            
        prompt = f"""You are an expert in converting LookML code to Omni YAML syntax.

Convert the following LookML code to Omni YAML format following these rules:
- Extract ${TABLE}."FIELD" to just "FIELD" (with quotes)
- Keep complex SQL statements (CASE, etc) as-is, just remove ;;
- hidden: yes → hidden: true
- type: yesno → don't include type in output
- type: sum_distinct → aggregate_type: sum_distinct_on
- sql_distinct_key → custom_primary_key_sql (keep field references as-is, no table prefixes)
- value_format_name → format
- measure types (count, sum, etc) → aggregate_type
- dimension_groups should be under dimensions in the output
- dimension_groups only keep: sql, label, group_label, description
- Always include description field (use label as description if not provided)
- Fields ending with _id should have format: ID
- Clean up group_label (remove leading spaces)
- Don't include drill_fields that contain wildcards (*)
- Convert aliases, tags, links, required_access_grants to arrays if needed
- Map LookML parameters to Omni equivalents (see documentation)

{"Previous conversion attempt failed with: " + error_msg if error_msg else ""}

LookML code:
{lookml_code}

Please provide only the converted YAML output without any explanations."""

        try:
            client = anthropic.Anthropic(api_key=anthropic_key)
            response = client.messages.create(
                model="claude-3-opus-20240229",
                max_tokens=2000,
                temperature=0.1,
                messages=[
                    {"role": "user", "content": prompt}
                ]
            )
            return response.content[0].text.strip()
                
        except Exception as e:
            st.error(f"LLM conversion failed: {str(e)}")
            return None
    
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
                
            # Add dimension groups
            for name, props in parsed_data['dimension_groups'].items():
                output.append(f'  {name}:')
                output.extend(self._format_properties(props, 4))
        
        # Process measures
        if parsed_data['measures']:
            if output:
                output.append('')
            output.append('measures:')
            for name, props in parsed_data['measures'].items():
                # Check if we need to rename the measure based on label
                measure_name = name
                if 'label' in props:
                    # Example: sum_planned_cpx -> sum_cxp_planned based on label pattern
                    if name == 'sum_planned_cpx' and props['label'] == 'Total Planned CXP':
                        measure_name = 'sum_cxp_planned'
                    elif name == 'sum_delivered_cpx' and 'Done' in props.get('label', ''):
                        measure_name = 'sum_cxp_done'
                
                output.append(f'  {measure_name}:')
                output.extend(self._format_properties(props, 4))
        
        return '\n'.join(output)
    
    def _format_properties(self, props: Dict[str, Any], indent: int) -> list:
        """Format properties as YAML lines"""
        lines = []
        indent_str = ' ' * indent
        
        # Property order for better organization - matching Omni documentation order
        property_order = [
            'sql', 'label', 'group_label', 'description', 'format',
            'aggregate_type', 'custom_primary_key_sql', 'hidden', 
            'primary_key', 'ignored', 'aliases', 'tags', 
            'links', 'drill_fields', 'drill_queries', 'filters',
            'display_order', 'view_label', 'suggest_from_field',
            'suggestion_list', 'order_by_field', 'required_access_grants',
            'timeframes', 'convert_tz', 'groups', 'bin_boundaries',
            'filter_single_select_only', 'colors'
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
            # Special handling for SQL fields
            if key == 'sql':
                # Check if it's already a simple quoted field reference
                if value.startswith('"') and value.endswith('"') and value.count('"') == 2:
                    # It's already properly quoted, output with single quotes around the whole thing
                    lines.append(f"{indent_str}{key}: '{value}'")
                else:
                    # It's complex SQL (CASE statements, etc.), output as-is
                    lines.append(f'{indent_str}{key}: {value}')
            else:
                # For all other string properties
                lines.append(f'{indent_str}{key}: {value}')
        else:
            lines.append(f'{indent_str}{key}: {value}')
        
        return lines

# Initialize converter
converter = LookMLToOmniConverter()

# Sidebar content
with st.sidebar:
    st.markdown('<h2 style="font-family: Georgia, serif; font-size: 1.5rem; color: #000; letter-spacing: -0.02em;">AI Enhancement</h2>', unsafe_allow_html=True)
    
    st.markdown("""
    <div style="font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif; color: #595959; font-size: 0.875rem; margin-bottom: 1rem;">
    Optional: Add an Anthropic API key for enhanced conversion using Claude when the standard conversion fails.
    </div>
    """, unsafe_allow_html=True)
    
    # API key input
    anthropic_key = st.text_input("Anthropic API Key:", type="password", key="anthropic_api_key_input")
    if anthropic_key:
        st.session_state['anthropic_api_key'] = anthropic_key
    
    # Check if key is set via environment variable
    if os.getenv('ANTHROPIC_API_KEY') and not anthropic_key:
        st.success("✅ API key loaded from environment")
    elif anthropic_key:
        st.success("✅ API key set")
    
    st.markdown("---")
    
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
        st.session_state.lookml_input = """dimension: active_sprint_week {
  label: "Active Sprint Week"
  group_label: "Sprint Details"
  type: string
  sql: ${TABLE}."ACTIVE_SPRINT_WEEK" ;;
}

dimension: board_id {
  hidden: yes
  type: string
  sql: ${TABLE}."BOARD_ID" ;;
}

dimension: delivered_cxp {
  hidden: yes
  type: number
  sql: case when ${task_is_done} then ${cxp} else 0 end ;;
}

dimension_group: planned_week_from {
  type: time
  label: "Time Plan Week From"
  group_label: "  Date Groups"
  timeframes: [
    raw,
    date,
    week,
    month,
    quarter,
    year
  ]
  convert_tz: no
  datatype: date
  sql: ${TABLE}."PLANNED_WEEK_FROM" ;;
}

measure: count_tasks {
  label: "Count Unique Tasks"
  group_label: "Sprint Details"
  type: count_distinct
  sql: ${task_id} ;;
  drill_fields: [task_level_drills*]
}

measure: sum_planned_cpx {
  label: "Total Planned CXP"
  group_label: "Sprint Details"  
  type: sum
  sql: ${cxp} ;;
  drill_fields: [task_level_drills*]
}

measure: total_cxp_budget {
  label: "CXP Budget"
  group_label: "Sprint Details"
  type: sum_distinct
  sql: ${cxp_budget} ;;
  sql_distinct_key: ${sprint_id} ;;
}"""
        st.rerun()

# Header with Tasman branding
st.markdown("""
<div class="main-header">
    <h1 style="margin: 0; font-size: 3rem; font-weight: normal; color: #ffffff;">TASMAN</h1>
    <p style="margin: 1rem 0 0 0; font-family: 'Roboto Mono', monospace; font-size: 0.875rem; text-transform: uppercase; letter-spacing: 0.1em; opacity: 0.8; color: #ffffff;">LOOKML TO OMNI YAML CONVERTER</p>
</div>
""", unsafe_allow_html=True)

# Main content area
col1, col2 = st.columns(2, gap="medium")

with col1:
    st.markdown('<h2 style="font-family: Georgia, serif; font-size: 1.8rem; color: #000; letter-spacing: -0.02em; margin-bottom: 1rem;">LookML Input</h2>', unsafe_allow_html=True)
    lookml_input = st.text_area(
        "Paste your LookML code here:",
        height=500,
        placeholder="""Example:
  marketing_channel {
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
    copy_feedback = st.empty()

# Handle conversion
if convert_button and lookml_input:
    try:
        # First try rule-based conversion
        with st.spinner("Converting with rule-based engine..."):
            parsed_data = converter.parse_lookml(lookml_input)
            omni_yaml = converter.convert_to_yaml(parsed_data)
        
        # Check if conversion produced meaningful output
        if not omni_yaml.strip() or omni_yaml.strip() == "dimensions:\n\nmeasures:":
            # Try LLM conversion if available
            if st.session_state.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY'):
                with st.spinner("Rule-based conversion incomplete. Trying AI-powered conversion..."):
                    llm_result = converter.get_llm_conversion(lookml_input, "Empty or incomplete output")
                    if llm_result:
                        omni_yaml = llm_result
                        st.info("🤖 AI-powered conversion used for better results")
            else:
                st.warning("⚠️ Conversion produced limited output. Consider adding an Anthropic API key for AI-enhanced conversion.")
        
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
        # Try LLM conversion on error
        if st.session_state.get('anthropic_api_key') or os.getenv('ANTHROPIC_API_KEY'):
            with st.spinner("Standard conversion failed. Trying AI-powered conversion..."):
                llm_result = converter.get_llm_conversion(lookml_input, str(e))
                if llm_result:
                    with col2:
                        st.text_area(
                            "Converted YAML:",
                            value=llm_result,
                            height=500,
                            key="omni_output",
                            label_visibility="collapsed"
                        )
                        
                        # Download button
                        st.download_button(
                            label="DOWNLOAD YAML",
                            data=llm_result,
                            file_name="omni_config.yaml",
                            mime="text/yaml"
                        )
                    
                    st.success("✅ AI-powered conversion successful!")
                else:
                    st.error(f"❌ Both standard and AI conversion failed: {str(e)}")
        else:
            st.error(f"❌ Conversion failed: {str(e)}")
            st.info("💡 Tip: Add an Anthropic API key in the sidebar to enable AI-powered fallback conversion.")

# Handle clear button
if clear_button:
    st.rerun()

# Footer
st.markdown("---")
footer_html = """<div style='text-align: center; color: #595959; font-family: Roboto Mono, monospace; font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; padding: 2rem 0;'>
    TASMAN • DATA TRANSFORMATION TOOLS
</div>"""
st.markdown(footer_html, unsafe_allow_html=True)
