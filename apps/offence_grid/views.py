from django.shortcuts import render
import pandas as pd
import sys
import re
from pathlib import Path

# Add src to Python path for importing tools
src_path = Path(__file__).resolve().parent.parent.parent / 'src'
sys.path.append(str(src_path))

from tools import ca_collateral_consequences
from tools.cc_rules_current import (
    check_discharge_available,
    check_cso_availablity,
    check_intermittent_available,
    check_suspended_sentence_available,
    check_dna_designation,
    check_soira,
    check_section_109_weapons_prohibition,
    reverse_onus,
    check_section_469_offence,
    check_section_515_mandatory_weapons_prohibition,
    check_offence_type,
    check_prelim_available,
    check_jury_trial_available
)

def format_section(section):
    """Format section numbers for display by replacing prefix with § symbol."""
    if not section:
        return section
    # Replace any prefix (like cc_, ycja_, cdsa_) and underscore with "§ "
    return re.sub(r'^[a-z]+_', '§ ', section)

def clean_section_display(section):
    """Remove any '#' and everything after from the section string."""
    return section.split('#')[0]

def load_offences():
    """Load offences from all CSV files and tag with statute prefix, replacing code prefixes in section numbers."""
    base_path = Path(__file__).resolve().parent.parent.parent / 'src/data/offence/'
    sources = [
        ("cc-offences-2024-09-16.csv", "Criminal Code ", None),
        ("cannabis-offences-2024-09-16.csv", "Cannabis Act ", r"^cannabis_"),
        ("cdsa-offences-2024-09-16.csv", "CDSA ", r"^cdsa_"),
        ("ycja-offences-2024-09-16.csv", "YCJA ", r"^ycja_"),
    ]
    offences = []
    for filename, prefix, code_prefix in sources:
        csv_path = base_path / filename
        if not csv_path.exists():
            continue
        df = pd.read_csv(csv_path, keep_default_na=False)
        for _, row in df.iterrows():
            section = row['section']
            if code_prefix:
                section = re.sub(code_prefix, '', section)
            # Remove # and everything after for display
            section_display = clean_section_display(section)
            offences.append((row['section'], prefix + format_section(section_display), row['offence_name'],
                             row['maximum_indictable'], row['maximum_sc'],
                             row['minimum_indictable'], row['minimum_sc'], prefix.rstrip()))
    return offences

def parse_minimum(min_value):
    """Parse minimum sentence value into a dictionary format."""
    empty_result = {
        "jail": {"amount": None, "unit": None},
        "fine": {"amount": None, "unit": None}
    }
    
    if pd.isna(min_value) or not min_value:
        return empty_result
    
    # Check for fine amount (e.g., "1000$")
    fine_match = re.match(r'(\d+)\$', min_value)
    if fine_match:
        amount = fine_match.group(1)
        return {
            "jail": {"amount": None, "unit": None},
            "fine": {"amount": int(amount), "unit": None}
        }
    
    # Check for jail time (e.g., "90d", "6m", "2y")
    jail_match = re.match(r'(\d+)([dmy])', min_value)
    if jail_match:
        amount, unit = jail_match.groups()
        unit_map = {'d': 'days', 'm': 'months', 'y': 'years'}
        return {
            "jail": {"amount": int(amount), "unit": unit_map[unit]},
            "fine": {"amount": None, "unit": None}
        }
    
    return empty_result

def parse_maximum(max_value):
    """Parse maximum sentence value into a dictionary format."""
    if pd.isna(max_value) or not max_value:
        return None
    
    # Handle combined fine and jail time (e.g., "100$&90d" or "100&90d")
    if isinstance(max_value, str) and '&' in max_value:
        fine_part, jail_part = max_value.split('&')
        # Handle fine part - strip $ if present
        fine_amount = int(fine_part.rstrip('$')) if fine_part.strip('$').isdigit() else None
        
        # Parse jail part
        if jail_part.endswith('y'):
            jail_amount = int(jail_part.rstrip('y'))
            jail_unit = "years"
        elif jail_part.endswith('m'):
            jail_amount = int(jail_part.rstrip('m'))
            jail_unit = "months"
        elif jail_part.endswith('d'):
            jail_amount = int(jail_part.rstrip('d'))
            jail_unit = "days"
        else:
            jail_amount = None
            jail_unit = None
            
        return {
            "jail": {"amount": jail_amount, "unit": jail_unit},
            "fine": {"amount": fine_amount, "unit": "dollars"}
        }
    
    # Handle jail time only
    if isinstance(max_value, str):
        if max_value.endswith('y'):
            return {
                "jail": {"amount": int(max_value.rstrip('y')), "unit": "years"},
                "fine": {"amount": None, "unit": None}
            }
        elif max_value.endswith('m'):
            return {
                "jail": {"amount": int(max_value.rstrip('m')), "unit": "months"},
                "fine": {"amount": None, "unit": None}
            }
        elif max_value.endswith('d'):
            return {
                "jail": {"amount": int(max_value.rstrip('d')), "unit": "days"},
                "fine": {"amount": None, "unit": None}
            }
    
    return None

def get_collateral_consequences(section, max_indictable, max_sc, min_indictable, min_sc, citizenship_status=None):
    """Get collateral consequences for an offence."""
    consequences = {}

    # Parse the sentences
    summary_min = parse_minimum(min_sc)
    indictable_min = parse_minimum(min_indictable)
    indictable_max = parse_maximum(max_indictable)

    # Determine mode based on maximum sentences
    mode = "summary" if pd.isna(max_indictable) and not pd.isna(max_sc) else "indictable"
    if not pd.isna(max_indictable) and not pd.isna(max_sc):
        mode = "hybrid"

    # Get bail information
    consequences['bail'] = {
        'reverse_onus': reverse_onus(),
        'section_469': check_section_469_offence(section),
        'mandatory_weapons_prohibition': check_section_515_mandatory_weapons_prohibition(section)
    }

    # Get immigration consequences
    max_years = indictable_max["jail"]["amount"] if indictable_max and indictable_max["jail"]["amount"] else 0
    immigration_results = ca_collateral_consequences.check_inadmissibility(
        section=section,
        mode=mode,
        indictable_maximum=max_years,
        citizenship_status=citizenship_status
    )
    consequences['immigration'] = immigration_results

    # Get procedure information
    procedure = {
        'prelim_available': check_prelim_available(
            indictable_maximum=indictable_max
        ),
        'jury_trial_available': check_jury_trial_available(
            section=section,
            indictable_maximum=indictable_max
        )
    }
    consequences['procedure'] = procedure

    # Jury trial footnote
    jta = procedure['jury_trial_available']
    jury_footnote_obj = None
    if jta.get('notes') or jta.get('jury_conflict_footnote'):
        jury_footnote_obj = {
            'label': 'jury',
            'text': (jta.get('jury_conflict_footnote') or jta.get('notes')),
            'anchor': f"jury-PLACEHOLDER",
            'number': None
        }
        consequences['procedure']['jury_footnote'] = jury_footnote_obj
    else:
        consequences['procedure']['jury_footnote'] = None

    # Preliminary inquiry footnote
    prelim_footnote_obj = None
    if procedure['prelim_available'].get('notes'):
        prelim_footnote_obj = {
            'label': 'prelim',
            'text': procedure['prelim_available']['notes'] + (f" ({', '.join(procedure['prelim_available'].get('sections', []))})" if procedure['prelim_available'].get('sections') else ""),
            'anchor': f"prelim-PLACEHOLDER",
            'number': None
        }
        consequences['procedure']['prelim_footnote'] = prelim_footnote_obj
    else:
        consequences['procedure']['prelim_footnote'] = None

    # Get sentencing options
    consequences['sentencing_options'] = {
        'discharge': check_discharge_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min,
            indictable_maximum=indictable_max
        ),
        'cso': check_cso_availablity(
            section=section,
            summary_minimum=summary_min,
            indictable_minimum=indictable_min,
            indictable_maximum=indictable_max,
            mode=mode
        ),
        'intermittent': check_intermittent_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min
        ),
        'suspended': check_suspended_sentence_available(
            summary_minimum=summary_min,
            indictable_minimum=indictable_min
        )
    }

    # Get ancillary orders
    consequences['ancillary_orders'] = {
        'dna': check_dna_designation(
            offence=[section],
            mode=mode,
            quantum=indictable_max
        ),
        'soira': check_soira(
            section=section,
            mode=mode,
            indictable_maximum=indictable_max
        ),
        'weapons': check_section_109_weapons_prohibition([
            section,
            None,  # offence name not needed
            max_indictable,
            max_sc,
            min_indictable,
            min_sc
        ])
    }

    # --- Footnotes system ---
    footnotes = []
    footnote_refs = {}

    # Immigration footnotes (attach to immigration_result)
    for imm_result in immigration_results:
        if imm_result.get('sections'):
            footnote_obj = {
                'label': 'immigration',
                'text': f"Relevant sections: {', '.join(imm_result['sections'])}",
                'anchor': f"imm-{len(footnotes)+1}",
                'number': None
            }
            imm_result['footnote'] = footnote_obj
            footnotes.append(('immigration', footnote_obj, imm_result))
    consequences['immigration'] = immigration_results

    # Sentencing Options footnotes
    so = consequences['sentencing_options']
    so_footnotes = {}
    for key, label in [('discharge', 'dis'), ('cso', 'cso'), ('intermittent', 'int'), ('suspended', 'sus')]:
        note = so[key].get('notes')
        if note:
            footnote_obj = {
                'label': label,
                'text': note,
                'anchor': f"{label}-PLACEHOLDER",
                'number': None
            }
            so[key]['footnote'] = footnote_obj
            so_footnotes[key] = footnote_obj
        else:
            so[key]['footnote'] = None

    # Ancillary Orders footnotes
    ao = consequences['ancillary_orders']
    ao_footnotes = {'dna': None, 'soira': [], 'weapons': None}
    # DNA
    if ao['dna'].get('notes'):
        footnote_obj = {
            'label': 'dna',
            'text': ao['dna']['notes'] + (f" ({', '.join(ao['dna'].get('sections', []))})" if ao['dna'].get('sections') else ""),
            'anchor': f"dna-PLACEHOLDER",
            'number': None
        }
        ao['dna']['footnote'] = footnote_obj
        ao_footnotes['dna'] = footnote_obj
    else:
        ao['dna']['footnote'] = None
    # SOIRA (may be a list)
    if isinstance(ao['soira'], list):
        for idx, item in enumerate(ao['soira']):
            if item.get('notes'):
                footnote_obj = {
                    'label': f'soira{idx+1}',
                    'text': item['notes'] + (f" ({', '.join(item.get('sections', []))})" if item.get('sections') else ""),
                    'anchor': f"soira-{idx+1}-PLACEHOLDER",
                    'number': None
                }
                item['footnote'] = footnote_obj
                ao_footnotes['soira'].append(footnote_obj)
            else:
                item['footnote'] = None
    else:
        if ao['soira'].get('notes'):
            footnote_obj = {
                'label': 'soira',
                'text': ao['soira']['notes'] + (f" ({', '.join(ao['soira'].get('sections', []))})" if ao['soira'].get('sections') else ""),
                'anchor': f"soira-PLACEHOLDER",
                'number': None
            }
            ao['soira']['footnote'] = footnote_obj
            ao_footnotes['soira'].append(footnote_obj)
        else:
            ao['soira']['footnote'] = None
    # Weapons
    if ao['weapons'].get('notes'):
        footnote_obj = {
            'label': 'mwp',
            'text': ao['weapons']['notes'] + (f" ({', '.join(ao['weapons'].get('sections', []))})" if ao['weapons'].get('sections') else ""),
            'anchor': f"mwp-PLACEHOLDER",
            'number': None
        }
        ao['weapons']['footnote'] = footnote_obj
        ao_footnotes['weapons'] = footnote_obj
    else:
        ao['weapons']['footnote'] = None

    # --- Order footnotes to match template appearance (Procedure first, then Immigration, etc.) ---
    ordered_footnotes = []
    # 1. Procedure (prelim)
    if prelim_footnote_obj:
        ordered_footnotes.append(prelim_footnote_obj)
    # 2. Procedure (jury)
    if jury_footnote_obj:
        ordered_footnotes.append(jury_footnote_obj)
    # 3. Immigration (may be multiple)
    for imm_result in immigration_results:
        if imm_result.get('footnote'):
            ordered_footnotes.append(imm_result['footnote'])
    # 4. Sentencing Options
    for key in ['discharge', 'cso', 'intermittent', 'suspended']:
        if so_footnotes.get(key):
            ordered_footnotes.append(so_footnotes[key])
    # 5. Ancillary Orders
    if ao_footnotes['dna']:
        ordered_footnotes.append(ao_footnotes['dna'])
    for soira_footnote in ao_footnotes['soira']:
        ordered_footnotes.append(soira_footnote)
    if ao_footnotes['weapons']:
        ordered_footnotes.append(ao_footnotes['weapons'])

    # Assign numbers and anchors
    for i, footnote in enumerate(ordered_footnotes):
        footnote['number'] = i + 1
        # Update anchor to match new number
        base_anchor = footnote['anchor'].split('-')[0]
        footnote['anchor'] = f"{base_anchor}-{i+1}"
    consequences['footnotes'] = ordered_footnotes

    return consequences

def get_offence_summary(section, max_indictable, max_sc, min_indictable, min_sc):
    """Generate a summary of the offence including mode and sentences."""
    summary = {}
    
    # Parse the quantum values
    max_indictable_dict = parse_maximum(max_indictable) if max_indictable else None
    max_sc_dict = parse_maximum(max_sc) if max_sc else None
    min_indictable_dict = parse_minimum(min_indictable) if min_indictable else None
    min_sc_dict = parse_minimum(min_sc) if min_sc else None
    
    # Add sentence information
    if max_indictable_dict:
        summary['indictable_maximum'] = max_indictable_dict
        summary['indictable_minimum'] = min_indictable_dict or {'jail': {'amount': None, 'unit': None}, 'fine': {'amount': None, 'unit': None}}
    
    # For hybrid offences and summary offences, handle summary maximum
    if max_sc == 'sc':  # If explicitly marked as summary conviction
        summary['summary_maximum'] = {'jail': {'amount': 729, 'unit': 'days'}, 'fine': {'amount': None, 'unit': None}}
    elif max_sc_dict and (max_sc_dict['jail']['amount'] or max_sc_dict['fine']['amount']):
        summary['summary_maximum'] = max_sc_dict
    
    # Only add summary minimum if we have a summary maximum
    if 'summary_maximum' in summary:
        summary['summary_minimum'] = min_sc_dict or {'jail': {'amount': None, 'unit': None}, 'fine': {'amount': None, 'unit': None}}
    
    return summary

def offence_grid(request):
    """Landing page for the offence grid tool."""
    offences = load_offences()
    selected_offences = request.GET.getlist('offences')
    citizenship_status = request.GET.get('citizenship_status', None)
    if citizenship_status is not None:
        print(f"[OFFENCE GRID] Citizenship status selected: {citizenship_status}")
    results = {}
    if selected_offences:
        for section in selected_offences:
            for offence_data in offences:
                if offence_data[0] == section:
                    offence_list = list(offence_data)
                    mode = check_offence_type(offence_list)
                    summary = get_offence_summary(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6]
                    )
                    summary['mode'] = mode.title()
                    summary['description'] = offence_data[2]
                    summary['statute_prefix'] = offence_data[7] if len(offence_data) > 7 else "CC"
                    consequences = get_collateral_consequences(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6],
                        citizenship_status=citizenship_status
                    )
                    results[offence_data[1]] = {
                        'summary': summary,
                        **consequences
                    }
                    break
    show_irpa_footnote = False
    if citizenship_status == 'foreign' and results:
        for result in results.values():
            for immigration_result in result.get('immigration', []):
                if immigration_result['status']['notes'] != 'both' and immigration_result['status']['notes'] != 'foreign national':
                    show_irpa_footnote = True
                    break
            if show_irpa_footnote:
                break
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
        'offences': [(o[0], f"{o[1]} - {o[2]}") for o in offences],
        'selected_offences': selected_offences,
        'citizenship_status': citizenship_status,
        'results': results,
        'show_irpa_footnote': show_irpa_footnote,
    })
