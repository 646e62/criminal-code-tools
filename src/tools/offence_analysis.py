from typing import Dict, Optional
from .main import initialize, generate_basic_offence_details
import src.tools.main as main
from .cc_rules_current import (
    check_offence_type,
    check_discharge_available,
    check_cso_availablity,
    check_intermittent_available,
    check_suspended_sentence_available,
    check_prelim_available,
    check_jury_trial_available,
    reverse_onus,
    check_section_469_offence,
    check_dna_designation,
    check_soira
)

def _convert_amount_to_int(val):
    try:
        return int(val)
    except (ValueError, TypeError):
        return 0

def _convert_jail_amount_to_int(jail_dict):
    if not isinstance(jail_dict, dict):
        return 0
    amt = jail_dict.get("amount", 0)
    return _convert_amount_to_int(amt)

class OffenceAnalysis:
    def __init__(
        self,
        section: str,
        citizenship_status: Optional[str] = None,
        ordinarily_resident: Optional[bool] = True,
    ):
        initialize()
        found_row = None
        for row in main.data:
            if row[0] == section:
                found_row = row
                break
        if not found_row:
            raise ValueError(f"Section {section} not found in offence data.")
        self.offence_data = generate_basic_offence_details(found_row)
        self.citizenship_status = citizenship_status
        self.ordinarily_resident = ordinarily_resident

    def _to_offence_list(self):
        return [
            self.offence_data.get('section', ''),
            self.offence_data.get('description', ''),
            '',
            self.offence_data.get('indictable_maximum', ''),
            self.offence_data.get('summary_maximum', ''),
        ]
    
    def offence_type(self) -> str:
        return check_offence_type(self._to_offence_list())

    # Sentencing options
    def discharge_available(self):
        smin = self.offence_data['summary_minimum'].copy()
        imin = self.offence_data['indictable_minimum'].copy()
        imax = self.offence_data['indictable_maximum'].copy()
        smin['jail'] = smin.get('jail', {}).copy()
        imin['jail'] = imin.get('jail', {}).copy()
        imax['jail'] = imax.get('jail', {}).copy()
        smin['jail']['amount'] = _convert_jail_amount_to_int(smin['jail'])
        imin['jail']['amount'] = _convert_jail_amount_to_int(imin['jail'])
        imax['jail']['amount'] = _convert_jail_amount_to_int(imax['jail'])
        return check_discharge_available(smin, imin, imax)

    def cso_available(self):
        smin = self.offence_data['summary_minimum'].copy()
        imin = self.offence_data['indictable_minimum'].copy()
        imax = self.offence_data['indictable_maximum'].copy()
        smin['jail'] = smin.get('jail', {}).copy()
        imin['jail'] = imin.get('jail', {}).copy()
        imax['jail'] = imax.get('jail', {}).copy()
        smin['jail']['amount'] = _convert_jail_amount_to_int(smin['jail'])
        imin['jail']['amount'] = _convert_jail_amount_to_int(imin['jail'])
        imax['jail']['amount'] = _convert_jail_amount_to_int(imax['jail'])
        return check_cso_availablity(
            self.offence_data['section'],
            smin,
            imin,
            imax,
            self.offence_data['mode'],
        )

    def intermittent_available(self):
        smin = self.offence_data['summary_minimum'].copy()
        imin = self.offence_data['indictable_minimum'].copy()
        smin['jail'] = smin.get('jail', {}).copy()
        imin['jail'] = imin.get('jail', {}).copy()
        smin['jail']['amount'] = _convert_jail_amount_to_int(smin['jail'])
        imin['jail']['amount'] = _convert_jail_amount_to_int(imin['jail'])
        return check_intermittent_available(smin, imin)

    def suspended_sentence_available(self):
        smin = self.offence_data['summary_minimum'].copy()
        imin = self.offence_data['indictable_minimum'].copy()
        smin['jail'] = smin.get('jail', {}).copy()
        imin['jail'] = imin.get('jail', {}).copy()
        smin['jail']['amount'] = _convert_jail_amount_to_int(smin['jail'])
        imin['jail']['amount'] = _convert_jail_amount_to_int(imin['jail'])
        return check_suspended_sentence_available(smin, imin)

    # Procedural sections
    def prelim_available(self):
        imax = self.offence_data['indictable_maximum'].copy()
        imax['jail'] = imax.get('jail', {}).copy()
        imax['jail']['amount'] = _convert_jail_amount_to_int(imax['jail'])
        return check_prelim_available(imax)

    def jury_trial_available(self):
        imax = self.offence_data['indictable_maximum'].copy()
        imax['jail'] = imax.get('jail', {}).copy()
        imax['jail']['amount'] = _convert_jail_amount_to_int(imax['jail'])
        return check_jury_trial_available(self.offence_data['section'], imax)

    def reverse_onus(self):
        return reverse_onus(self.ordinarily_resident)

    def section_469_offence(self):
        return check_section_469_offence(self.offence_data['section'])

    # Offence Summary: Mandatory minimum checks

    def mandatory_minimums(self):
        """
        Returns a summary of mandatory minimums for this offence for both summary and indictable modes.
        """
        smin = self.offence_data['summary_minimum']
        imin = self.offence_data['indictable_minimum']
        summary_minimums = {}
        indictable_minimums = {}
        for k in ['jail', 'fine']:
            sval = smin.get(k, {})
            ival = imin.get(k, {})
            if sval.get('amount'):
                summary_minimums[k] = sval
            if ival.get('amount'):
                indictable_minimums[k] = ival
        return {
            'summary': summary_minimums if summary_minimums else None,
            'indictable': indictable_minimums if indictable_minimums else None
        }

    # Collateral consequences and ancillary orders
    def collateral_consequences(self):
        """
        Returns IRPA inadmissibility consequences (immigration consequences).
        """
        from .ca_collateral_consequences import check_inadmissibility
        # Use citizenship_status if provided, otherwise default to 'canadian'
        citizenship_status = self.citizenship_status or 'canadian'
        section = self.offence_data['section']
        mode = self.offence_data.get('mode', 'summary')
        imax = self.offence_data['indictable_maximum']
        jail = imax.get('jail', {})
        jail_amount = jail.get('amount', 0)
        return check_inadmissibility(section, mode, jail_amount, citizenship_status)

    def ancillary_orders(self):
        """
        Returns a dictionary of ancillary orders (DNA, SOIRA, weapons prohibition).
        DNA and SOIRA logic is delegated to cc_rules_current, weapons prohibition is a dummy for now.
        """
        # For DNA and SOIRA, use the offence list and max quantum
        offence_list = self._to_offence_list()
        mode = self.offence_data.get('mode', 'summary')
        imax = self.offence_data['indictable_maximum']
        section = self.offence_data['section']
        # Dummy for weapons prohibition for now
        def dummy_weapons_prohib():
            return {'status': {'available': False, 'notes': None}, 'sections': ['cc_109'], 'notes': 'not implemented'}
        return {
            'dna_designation': check_dna_designation(offence_list, mode, imax),
            'soira': check_soira(section, mode, imax),
            'weapons_prohibition': dummy_weapons_prohib()
        }

if __name__ == "__main__":
    section = "cc_266"
    offence_analysis = OffenceAnalysis(section)
    offence_data = offence_analysis.offence_data
    print("\nOffence Summary:")
    print("Section:", offence_data["section"])
    print("Description:", offence_data["description"])
    print("Mode:", offence_analysis.offence_type())
    print("Indictable Maximum:", offence_data["indictable_maximum"])
    print("Summary Maximum:", offence_data["summary_maximum"])
    print("Mandatory minimums:", offence_analysis.mandatory_minimums())

    print("\nSentencing Options:")
    print("Discharge available:", offence_analysis.discharge_available())
    print("CSO available:", offence_analysis.cso_available())
    print("Intermittent sentence available:", offence_analysis.intermittent_available())
    print("Suspended sentence available:", offence_analysis.suspended_sentence_available())
    
    print("\nProcedural Sections:")
    print("n\Indictable proceedings:")
    print("Preliminary inquiry available:", offence_analysis.prelim_available())
    print("Jury trial available:", offence_analysis.jury_trial_available())
    print("\nBail:")
    print("Reverse onus:", offence_analysis.reverse_onus())
    print("Section 469 offence:", offence_analysis.section_469_offence())

    print("\nCollateral Consequences:")
    print(offence_analysis.collateral_consequences())
    print("\nAncillary Orders:")
    print(offence_analysis.ancillary_orders())
