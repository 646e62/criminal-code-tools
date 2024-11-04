# criminal-code-offence-parser
Offence analysis tools for *Criminal Code*, RSC 1985, c C-46 and related statutes.

The tools are designed to provide domain-specific expert inferences with human-readable explanations for the results. The tools themselves are functions that translate statutory legal logic into computational logic. The provided explanations include citations to the statute where the unformatted legislative logic is located.

The tools will work as intended when they return accurate results with complete explanations of the program's logic. 

```python
> from main import parse_offence
> parse_offence("cc266")
{'section': 'cc266',
 'description': 'assault',
 'mode': 'hybrid',
 'summary_minimum': {'amount': None, 'unit': None},
 'summary_maximum': {'amount': '729', 'unit': 'days'},
 'indictable_minimum': {'amount': None, 'unit': None},
 'indictable_maximum': {'amount': 5, 'unit': 'years'},
 'absolute_jurisdiction': [{'status': {'absolute_jurisdiction': False,
    'notes': ''},
   'section': 'cc553',
   'reason': ''}],
 'prelim_available': {'status': ({'available': False, 'notes': ''},),
  'section': 'cc535',
  'reason': 'maximum term of less than 14y'},
 'release_by_superior_court_judge': False,
 'cso_available': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc742.1',
  'reason': None},
 'intermittent_available': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc732(1)',
  'reason': 'no minimum term of imprisonment'},
 'suspended_sentence_available': {'status': ({'available': True,
    'notes': ''},),
  'section': 'cc731(1)',
  'reason': None},
 'discharge_available': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc730(1)',
  'reason': None},
 'prison_and_probation_available': {'status': ({'available': True,
    'notes': ''},),
  'section': 'cc732(1)',
  'reason': 'no minimum term of imprisonment'},
 'fine_alone': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc734(1)',
  'reason': 'no mandatory minimum term of imprisonment'},
 'fine_and_probation': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc732(1)',
  'reason': 'no minimum term of imprisonment'},
 'dna_designation': {'status': ({'available': True, 'notes': ''},),
  'section': 'cc487.04',
  'reason': 'secondary designated offence'},
 'soira': None,
 'proceeds_of_crime_forfeiture': [{'section': ['cc462.3[designated offence]',
    'cc462.37(1)'],
   'status': 'available',
   'reason': 'offence prosecutable by indictment'}],
 'section_164.2_forfeiture_order': [],
 'inadmissibility': [{'section': 'irpa36(2)',
   'status': 'foreign national',
   'reason': 'criminality'}]}
```