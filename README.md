# Criminal Code Offence Parser

## Overview
Offence analysis tools for *Criminal Code*, RSC 1985, c C-46 and related statutes.

The program provides domain-specific expert inferences with human-readable explanations for the results. The program's tools are functions that translate statutory legal logic into computational logic. The provided explanations include citations to the statute where the unformatted legislative logic is located.

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/criminal-code-offence-parser.git
cd criminal-code-offence-parser
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

## Project Structure

```
criminal-code-offence-parser/
├── src/
│   └── criminal-code-offence-parser/
│       ├── main.py              # Main parsing functionality
│       ├── cc_rules_current.py  # Current Criminal Code rules
│       ├── constants.py         # Constant definitions
│       ├── utils.py            # Utility functions
│       └── map.py              # Mapping definitions
├── data/
│   └── cc-offences-2024-09-16.csv  # Offence data
├── tests/                      # Unit tests
├── README.md
└── requirements.txt
```

## Usage

### Basic Call
The main function call provides customizable output. The program call will always produce basic offence information:

```python
from main import parse_offence

# Basic offence information
result = parse_offence("cc266")
```

### Available Arguments

The following arguments can be used to customize the output:

- `mode`: Mode of proceeding ("summary" or "indictable")
- `full`: Return all available information
- `procedure`: Include procedural details
- `ancillary_orders`: Include ancillary order details
- `sentencing`: Include sentencing details
- `collateral_consequences`: Include collateral consequence details

### Examples

1. **Basic Offence Information**
```python
from main import parse_offence
result = parse_offence("cc266")
```

2. **With Collateral Consequences**
```python
result = parse_offence("cc151", collateral_consequences=True)
```

3. **Multiple Arguments**
```python
result = parse_offence("cc811", ancillary_orders=True, procedure=True)
```

4. **Full Output**
```python
result = parse_offence("cc172.2", full=True)
```

## Return Data Structure

The function returns a dictionary containing requested information. The basic structure includes:

```python
{
    'offence_data': {
        'section': str,          # Criminal Code section
        'description': str,      # Offence description
        'mode': str,            # 'summary', 'indictable', or 'hybrid'
        'summary_minimum': dict, # Minimum sentence for summary proceedings
        'summary_maximum': dict, # Maximum sentence for summary proceedings
        'indictable_minimum': dict, # Minimum sentence for indictable proceedings
        'indictable_maximum': dict, # Maximum sentence for indictable proceedings
        'absolute_jurisdiction': list # Absolute jurisdiction information
    }
}
```

Additional sections (procedure, sentencing, etc.) are added based on the arguments provided.

## Error Handling

The parser includes comprehensive error handling for:
- Invalid offence codes
- Missing data
- Invalid modes of prosecution
- File access issues

Errors will raise appropriate exceptions with descriptive messages.

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Run the tests
5. Submit a pull request

## License

This project is licensed under the GNU General Public License v3.0 (GPL-3.0). This means:

- You are free to use, modify, and distribute this software
- If you distribute modified versions, you must:
  - Make your source code available
  - License it under GPL-3.0
  - Document your changes
- There is no warranty for this program

For more details, see the [LICENSE](LICENSE) file in the repository.
