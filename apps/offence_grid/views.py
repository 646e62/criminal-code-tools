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
    irpa_text = 'See <a href="https://canlii.ca/t/7vwq#sec36" target="_blank" rel="noopener noreferrer" class="text-blue-600 underline hover:text-blue-800 visited:text-purple-600">IRPA § 36(2)(a)</a>: A foreign national is inadmissible on grounds of criminality for having been convicted in Canada of ... two offences under any Act of Parliament not arising out of a single occurrence.'
    irpa_anchor = "irpa-36-2-a"
    irpa_footnote = None

    for imm_result in immigration_results:
        # Attach a footnote for all results
        if imm_result.get('sections'):
            footnote_text = f"Relevant sections: {', '.join(imm_result['sections'])}"
            footnote_anchor = f"imm-section-{hash(footnote_text)}"
            if footnote_anchor not in footnote_refs:
                footnote_obj = {
                    'label': 'imm-section',
                    'text': footnote_text,
                    'anchor': footnote_anchor,
                    'number': None
                }
                footnotes.append(footnote_obj)
                footnote_refs[footnote_anchor] = footnote_obj
            imm_result['footnote'] = {
                'anchor': footnote_anchor,
                'number': None  # Will be filled later
            }
        elif citizenship_status == 'foreign' and imm_result['status']['notes'] not in ['both', 'foreign national']:
            if not irpa_footnote:
                irpa_footnote = {
                    'label': 'irpa',
                    'text': irpa_text,
                    'anchor': irpa_anchor,
                    'number': None
                }
                footnotes.append(irpa_footnote)
                footnote_refs[irpa_anchor] = irpa_footnote
            imm_result['footnote'] = {
                'anchor': irpa_anchor,
                'number': None  # Will be filled later
            }
        elif citizenship_status == 'pr':
            footnote_text = "No admissibility consequences for permanent residents under IRPA for this offence."
            footnote_anchor = f"imm-pr-{hash(footnote_text)}"
            if footnote_anchor not in footnote_refs:
                footnote_obj = {
                    'label': 'imm-pr',
                    'text': footnote_text,
                    'anchor': footnote_anchor,
                    'number': None
                }
                footnotes.append(footnote_obj)
                footnote_refs[footnote_anchor] = footnote_obj
            imm_result['footnote'] = {
                'anchor': footnote_anchor,
                'number': None  # Will be filled later
            }
        # else: no footnote

    # Gather all other footnotes (procedure, sentencing, ancillary) as before
    extra_footnotes = []
    number = 1
    # Procedure
    if prelim_footnote_obj:
        prelim_footnote_obj['number'] = number
        extra_footnotes.append(prelim_footnote_obj)
        number += 1
    if jury_footnote_obj:
        jury_footnote_obj['number'] = number
        extra_footnotes.append(jury_footnote_obj)
        number += 1
    # Immigration (assign numbers now)
    for f in footnotes:
        f['number'] = number
        number += 1
    # Sentencing Options
    so = consequences['sentencing_options']
    for key, label in [('discharge', 'dis'), ('cso', 'cso'), ('intermittent', 'int'), ('suspended', 'sus')]:
        note = so[key].get('notes')
        if note:
            footnote_obj = {
                'label': label,
                'text': note,
                'anchor': f"{label}-PLACEHOLDER",
                'number': number
            }
            so[key]['footnote'] = footnote_obj
            extra_footnotes.append(footnote_obj)
            number += 1
    # Ancillary Orders
    ancillary = consequences['ancillary_orders']
    # DNA
    if ancillary['dna'].get('notes'):
        footnote_obj = {
            'label': 'dna',
            'text': ancillary['dna']['notes'] + (f" ({', '.join(ancillary['dna'].get('sections', []))})" if ancillary['dna'].get('sections') else ""),
            'anchor': 'dna-footnote',
            'number': number
        }
        ancillary['dna']['footnote'] = footnote_obj
        extra_footnotes.append(footnote_obj)
        number += 1
    # SOIRA (may be a list)
    soira = ancillary['soira'][0] if isinstance(ancillary['soira'], list) and ancillary['soira'] else ancillary['soira']
    if soira.get('notes'):
        footnote_obj = {
            'label': 'soira',
            'text': soira['notes'] + (f" ({', '.join(soira.get('sections', []))})" if soira.get('sections') else ""),
            'anchor': 'soira-footnote',
            'number': number
        }
        soira['footnote'] = footnote_obj
        extra_footnotes.append(footnote_obj)
        number += 1
    # Weapons
    if ancillary['weapons'].get('notes'):
        footnote_obj = {
            'label': 'weapons',
            'text': ancillary['weapons']['notes'] + (f" ({', '.join(ancillary['weapons'].get('sections', []))})" if ancillary['weapons'].get('sections') else ""),
            'anchor': 'weapons-footnote',
            'number': number
        }
        ancillary['weapons']['footnote'] = footnote_obj
        extra_footnotes.append(footnote_obj)
        number += 1

    # Compose final footnote list: procedure, immigration, sentencing, ancillary
    all_footnotes = extra_footnotes[:2] + footnotes + extra_footnotes[2:]
    consequences['footnotes'] = all_footnotes

    # Now update all footnote references with their assigned numbers
    anchor_to_number = {f['anchor']: f['number'] for f in all_footnotes}
    # Immigration
    for imm_result in immigration_results:
        if 'footnote' in imm_result and imm_result['footnote']['anchor'] in anchor_to_number:
            imm_result['footnote']['number'] = anchor_to_number[imm_result['footnote']['anchor']]
    # Procedure
    if prelim_footnote_obj:
        consequences['procedure']['prelim_footnote']['number'] = anchor_to_number[prelim_footnote_obj['anchor']]
    if jury_footnote_obj:
        consequences['procedure']['jury_footnote']['number'] = anchor_to_number[jury_footnote_obj['anchor']]
    # Sentencing
    for key, label in [('discharge', 'dis'), ('cso', 'cso'), ('intermittent', 'int'), ('suspended', 'sus')]:
        if so[key].get('footnote'):
            so[key]['footnote']['number'] = anchor_to_number[so[key]['footnote']['anchor']]
    # Ancillary
    if ancillary['dna'].get('footnote'):
        ancillary['dna']['footnote']['number'] = anchor_to_number[ancillary['dna']['footnote']['anchor']]
    if soira.get('footnote'):
        soira['footnote']['number'] = anchor_to_number[soira['footnote']['anchor']]
    if ancillary['weapons'].get('footnote'):
        ancillary['weapons']['footnote']['number'] = anchor_to_number[ancillary['weapons']['footnote']['anchor']]
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
    if citizenship_status in [None, '', 'None']:
        citizenship_status = 'canadian'
    results = []
    if selected_offences:
        # Also get crown election from GET params (may be one or many)
        crown_elections = request.GET.getlist('crown_election')
        for idx, section in enumerate(selected_offences):
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
                    # Add crown election logic
                    if mode == 'hybrid':
                        # Try to get the corresponding crown election from the GET params (by index)
                        crown_election = crown_elections[idx] if idx < len(crown_elections) and crown_elections[idx] else 'None'
                        summary['crown_election'] = crown_election.title()
                    else:
                        summary['crown_election'] = 'N/A'
                    consequences = get_collateral_consequences(
                        section=section,
                        max_indictable=offence_data[3],
                        max_sc=offence_data[4],
                        min_indictable=offence_data[5],
                        min_sc=offence_data[6],
                        citizenship_status=citizenship_status
                    )
                    results.append({
                        'display': offence_data[1],
                        'description': offence_data[2],
                        'summary': summary,
                        **consequences
                    })
                    break
    show_irpa_footnote = False
    if citizenship_status == 'foreign' and results:
        for result in results:
            for immigration_result in result.get('immigration', []):
                if immigration_result['status']['notes'] != 'both' and immigration_result['status']['notes'] != 'foreign national':
                    show_irpa_footnote = True
                    break
            if show_irpa_footnote:
                break
    # Prepare offences for template with mode computed in Python, not the template
    offences_with_mode = []
    for tup in offences:
        section, display, offence_name, max_indictable, max_sc, min_indictable, min_sc, prefix = tup
        if max_indictable and max_sc:
            mode = 'hybrid'
        elif max_indictable:
            mode = 'indictable'
        elif max_sc:
            mode = 'summary'
        else:
            mode = ''
        offences_with_mode.append((section, display, offence_name, max_indictable, max_sc, min_indictable, min_sc, prefix, mode))
    return render(request, 'offence_grid/index.html', {
        'title': 'Offence Grid',
        'offences': offences_with_mode,
        'selected_offences': selected_offences,
        'citizenship_status': citizenship_status,
        'results': results,
        'show_irpa_footnote': show_irpa_footnote,
    })
