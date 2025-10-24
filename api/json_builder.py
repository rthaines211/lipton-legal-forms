"""
JSON Builder Service: Rebuild latest_payload from normalized database records
"""
import json
import logging
from typing import Dict, List
from uuid import UUID

import psycopg

logger = logging.getLogger(__name__)


class JSONBuilderService:
    """Service to rebuild form JSON from normalized database records"""

    def build_json_from_db(self, cur: psycopg.Cursor, case_id: UUID) -> Dict:
        """
        Rebuild complete form JSON from database records

        This creates a fresh JSON payload that matches the original form structure,
        but reflects current database state (after edits). Used to update latest_payload.

        Args:
            cur: Database cursor (within transaction)
            case_id: UUID of the case

        Returns:
            Dict: Complete form JSON matching original structure
        """
        logger.info(f"Building JSON from database for case {case_id}")

        # Get case information
        case = self._get_case(cur, case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # Build plaintiffs with discovery
        plaintiffs = self._build_plaintiffs(cur, case_id)

        # Build defendants
        defendants = self._build_defendants(cur, case_id)

        # Build complete JSON structure
        json_payload = {
            "Form": {
                "Id": str(case_id),
                "InternalName": case["internal_name"],
                "Name": case["form_name"]
            },
            "PlaintiffDetails": plaintiffs,
            "DefendantDetails2": defendants,
            "Full_Address": {
                "StreetAddress": case["property_address"],
                "City": case["city"],
                "State": case["state"],
                "PostalCode": case["zip_code"],
                "Country": "United States",
                "CountryCode": "US"
            },
            "Filing city": case["filing_location"],
            "Filing county": case["county"]
        }

        logger.info(f"Built JSON with {len(plaintiffs)} plaintiffs and {len(defendants)} defendants")
        return json_payload

    def _get_case(self, cur: psycopg.Cursor, case_id: UUID) -> Dict | None:
        """Get case record"""
        cur.execute(
            """
            SELECT id, internal_name, form_name, property_address, city, state,
                   zip_code, county, filing_location
            FROM cases
            WHERE id = %s
            """,
            (case_id,)
        )
        return cur.fetchone()

    def _build_plaintiffs(self, cur: psycopg.Cursor, case_id: UUID) -> List[Dict]:
        """Build plaintiffs array with discovery information"""
        # Get all plaintiffs
        cur.execute(
            """
            SELECT id, party_number, first_name, last_name, full_name,
                   plaintiff_type, age_category, is_head_of_household, unit_number
            FROM parties
            WHERE case_id = %s AND party_type = 'plaintiff'
            ORDER BY party_number
            """,
            (case_id,)
        )
        plaintiffs_data = cur.fetchall()

        plaintiffs = []
        for plaintiff in plaintiffs_data:
            # Get discovery issues for this plaintiff
            discovery = self._build_discovery(cur, plaintiff["id"])

            plaintiff_obj = {
                "Id": str(plaintiff["id"]),
                "ItemNumber": plaintiff["party_number"],
                "PlaintiffItemNumberName": {
                    "First": plaintiff["first_name"],
                    "Last": plaintiff["last_name"],
                    "FirstAndLast": plaintiff["full_name"],
                    "Middle": None,
                    "MiddleInitial": None,
                    "Prefix": None,
                    "Suffix": None
                },
                "PlaintiffItemNumberType": plaintiff["plaintiff_type"],
                "PlaintiffItemNumberAgeCategory": [plaintiff["age_category"]] if plaintiff["age_category"] else [],
                "HeadOfHousehold": plaintiff["is_head_of_household"],
                "PlaintiffItemNumberDiscovery": discovery
            }
            plaintiffs.append(plaintiff_obj)

        return plaintiffs

    def _build_discovery(self, cur: psycopg.Cursor, party_id: UUID) -> Dict:
        """Build discovery object for a plaintiff"""
        # Get all issue selections for this plaintiff, grouped by category
        cur.execute(
            """
            SELECT
                ic.category_code,
                ic.category_name,
                array_agg(io.option_name ORDER BY io.display_order) as options
            FROM party_issue_selections pis
            JOIN issue_options io ON pis.issue_option_id = io.id
            JOIN issue_categories ic ON io.category_id = ic.id
            WHERE pis.party_id = %s
            GROUP BY ic.id, ic.category_code, ic.category_name
            ORDER BY ic.display_order
            """,
            (party_id,)
        )
        issue_data = cur.fetchall()

        # Get unit number
        cur.execute(
            "SELECT unit_number FROM parties WHERE id = %s",
            (party_id,)
        )
        party = cur.fetchone()
        unit_number = party["unit_number"] if party else None

        # Build discovery structure matching form format
        discovery = {
            # Boolean flags for each category
            "VerminIssue": False,
            "InsectIssues": False,
            "HVACIssues": False,
            "ElectricalIssues": False,
            "FireHazardIssues": False,
            "GovernmentEntityContacted": False,
            "AppliancesIssues": False,
            "PlumbingIssues": False,
            "CabinetsIssues": False,
            "FlooringIssues": False,
            "WindowsIssues": False,
            "DoorIssues": False,
            "StructureIssues": False,
            "CommonAreasIssues": False,
            "TrashProblems": False,
            "NuisanceIssues": False,
            "HealthHazardIssues": False,
            "SafetyIssues": False,
            "NoticesIssues": False,

            # Arrays for each category
            "Vermin": [],
            "Insects": [],
            "HVAC": [],
            "Electrical": [],
            "Fire Hazard": [],
            "Specific Government Entity Contacted": [],
            "Appliances": [],
            "Plumbing": [],
            "Cabinets": [],
            "Flooring": [],
            "Windows": [],
            "Doors": [],
            "Structure": [],
            "Common areas": [],
            "Select Trash Problems": [],
            "Nuisance": [],
            "Health hazard": [],
            "Select Safety Issues": [],
            "Select Notices Issues": [],

            "Unit": unit_number
        }

        # Map category codes to form field names
        category_map = {
            "vermin": ("VerminIssue", "Vermin"),
            "insects": ("InsectIssues", "Insects"),
            "hvac": ("HVACIssues", "HVAC"),
            "electrical": ("ElectricalIssues", "Electrical"),
            "fire_hazard": ("FireHazardIssues", "Fire Hazard"),
            "government_entities": ("GovernmentEntityContacted", "Specific Government Entity Contacted"),
            "appliances": ("AppliancesIssues", "Appliances"),
            "plumbing": ("PlumbingIssues", "Plumbing"),
            "cabinets": ("CabinetsIssues", "Cabinets"),
            "flooring": ("FlooringIssues", "Flooring"),
            "windows": ("WindowsIssues", "Windows"),
            "doors": ("DoorIssues", "Doors"),
            "structure": ("StructureIssues", "Structure"),
            "common_areas": ("CommonAreasIssues", "Common areas"),
            "trash_problems": ("TrashProblems", "Select Trash Problems"),
            "nuisance": ("NuisanceIssues", "Nuisance"),
            "health_hazard": ("HealthHazardIssues", "Health hazard"),
            "safety": ("SafetyIssues", "Select Safety Issues"),
            "notices": ("NoticesIssues", "Select Notices Issues")
        }

        # Populate based on actual selections
        for issue in issue_data:
            category_code = issue["category_code"]
            options = issue["options"]

            if category_code in category_map:
                flag_field, array_field = category_map[category_code]
                discovery[flag_field] = True
                discovery[array_field] = options

        return discovery

    def _build_defendants(self, cur: psycopg.Cursor, case_id: UUID) -> List[Dict]:
        """Build defendants array"""
        cur.execute(
            """
            SELECT id, party_number, first_name, last_name, full_name,
                   entity_type, role
            FROM parties
            WHERE case_id = %s AND party_type = 'defendant'
            ORDER BY party_number
            """,
            (case_id,)
        )
        defendants_data = cur.fetchall()

        defendants = []
        for defendant in defendants_data:
            defendant_obj = {
                "Id": str(defendant["id"]),
                "ItemNumber": defendant["party_number"],
                "DefendantItemNumberName": {
                    "First": defendant["first_name"],
                    "Last": defendant["last_name"],
                    "FirstAndLast": defendant["full_name"],
                    "Middle": None,
                    "MiddleInitial": None,
                    "Prefix": None,
                    "Suffix": None
                },
                "DefendantItemNumberType": defendant["entity_type"],
                "DefendantItemNumberManagerOwner": defendant["role"]
            }
            defendants.append(defendant_obj)

        return defendants

    def update_latest_payload(self, cur: psycopg.Cursor, case_id: UUID) -> Dict:
        """
        Rebuild and update latest_payload for a case

        Args:
            cur: Database cursor (within transaction)
            case_id: UUID of the case

        Returns:
            Dict: The new latest_payload JSON
        """
        # Build fresh JSON from database
        new_payload = self.build_json_from_db(cur, case_id)

        # Update latest_payload in database
        cur.execute(
            """
            UPDATE cases
            SET latest_payload = %s, updated_at = CURRENT_TIMESTAMP
            WHERE id = %s
            RETURNING id
            """,
            (json.dumps(new_payload), case_id)
        )

        result = cur.fetchone()
        if not result:
            raise ValueError(f"Failed to update latest_payload for case {case_id}")

        logger.info(f"Updated latest_payload for case {case_id}")
        return new_payload
