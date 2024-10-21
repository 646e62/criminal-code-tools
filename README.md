# criminal-code-offence-parser
Sentence calculation tools for Criminal Code, RSC 1985, c C-46

```python
> from main import parse_offence
> parse_offence("cc266")
{'section': 'cc266',
 'description': 'assault',
 'mode': 'hybrid',
 'summary_minimum': {'amount': None, 'unit': None},
 'summary_maximum': {'amount': '729', 'unit': 'days'},
 'indictable_minimum': {'amount': None, 'unit': None},
 'indictable_maximum': {'amount': '5', 'unit': 'years'},
 'section_469_offence': False,
 'prelim_available': False,
 'cso_available': {'section': 'cc742.1',
  'status': 'available',
  'reason': None},
 'dna_designation': 'secondary',
 'inadmissibility': [{'section': 'irpa36(2)',
   'status': 'foreign national',
   'reason': 'criminality'}]}
```