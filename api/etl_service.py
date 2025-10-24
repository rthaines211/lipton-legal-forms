"""
ETL Service: Transform form JSON into normalized database records
"""
import json
import logging
from typing import Dict, List, Tuple
from uuid import UUID
from datetime import datetime

import psycopg
from psycopg.rows import dict_row

from api.models import FormSubmission, PlaintiffDetail, DefendantDetail
from api.database import get_db_connection

logger = logging.getLogger(__name__)


class FormETLService:
    """Service to handle ETL from form JSON to PostgreSQL"""

    def __init__(self):
        self.issue_category_cache: Dict[str, UUID] = {}
        self.issue_option_cache: Dict[Tuple[str, str], UUID] = {}

    def ingest_form_submission(self, form_data: FormSubmission) -> Dict:
        """
        Main ETL entry point: Ingest form submission and store in database

        Args:
            form_data: Validated form submission

        Returns:
            Dict with case_id and counts

        Raises:
            Exception: If transaction fails (rolled back automatically)
        """
        with get_db_connection() as conn:
            # Use a single transaction for all operations
            with conn.cursor() as cur:
                try:
                    # Step 1: Insert case
                    case_id = self._insert_case(cur, form_data)
                    logger.info(f"Created case: {case_id}")

                    # Step 2: Insert plaintiffs
                    plaintiff_count = self._insert_plaintiffs(cur, case_id, form_data.PlaintiffDetails)
                    logger.info(f"Inserted {plaintiff_count} plaintiffs")

                    # Step 3: Insert defendants
                    defendant_count = self._insert_defendants(cur, case_id, form_data.DefendantDetails2)
                    logger.info(f"Inserted {defendant_count} defendants")

                    # Step 4: Insert plaintiff issues
                    issue_count = self._insert_plaintiff_issues(cur, case_id, form_data.PlaintiffDetails)
                    logger.info(f"Inserted {issue_count} issue selections")

                    # Commit happens automatically when context exits successfully
                    return {
                        "case_id": case_id,
                        "plaintiff_count": plaintiff_count,
                        "defendant_count": defendant_count,
                        "issue_count": issue_count,
                        "created_at": datetime.now()
                    }

                except Exception as e:
                    logger.error(f"ETL transaction failed: {e}")
                    # Rollback happens automatically via context manager
                    raise

    def _insert_case(self, cur: psycopg.Cursor, form_data: FormSubmission) -> UUID:
        """
        Insert case record with address and filing information

        Args:
            cur: Database cursor
            form_data: Form submission data

        Returns:
            UUID: Created case ID
        """
        # Extract address information
        address = form_data.Full_Address
        street_address = address.StreetAddress if address else None
        city = address.City if address else form_data.Filing_city or "Unknown"
        state = address.State if address else "CA"  # Default to CA if not provided
        postal_code = address.PostalCode if address else "00000"

        # Convert entire form to JSON for storage
        raw_payload = form_data.model_dump(by_alias=True, exclude_none=False)

        query = """
            INSERT INTO cases (
                property_address,
                city,
                state,
                zip_code,
                county,
                filing_location,
                internal_name,
                form_name,
                raw_payload,
                latest_payload
            ) VALUES (
                %(property_address)s,
                %(city)s,
                %(state)s,
                %(zip_code)s,
                %(county)s,
                %(filing_location)s,
                %(internal_name)s,
                %(form_name)s,
                %(raw_payload)s,
                %(latest_payload)s
            )
            RETURNING id
        """

        params = {
            "property_address": street_address or "Address Not Provided",
            "city": city,
            "state": state[:2] if state else "CA",  # Ensure 2-char state code
            "zip_code": postal_code,
            "county": form_data.Filing_county,
            "filing_location": form_data.Filing_city,
            "internal_name": form_data.Form.get("InternalName") if form_data.Form else None,
            "form_name": form_data.Form.get("Name") if form_data.Form else "Legal Form Submission",
            "raw_payload": json.dumps(raw_payload),
            "latest_payload": json.dumps(raw_payload)
        }

        cur.execute(query, params)
        result = cur.fetchone()
        return result["id"]

    def _insert_plaintiffs(self, cur: psycopg.Cursor, case_id: UUID, plaintiffs: List[PlaintiffDetail]) -> int:
        """
        Insert plaintiff records

        Args:
            cur: Database cursor
            case_id: Case UUID
            plaintiffs: List of plaintiff details

        Returns:
            int: Number of plaintiffs inserted
        """
        query = """
            INSERT INTO parties (
                case_id,
                party_type,
                party_number,
                first_name,
                last_name,
                full_name,
                plaintiff_type,
                age_category,
                is_head_of_household,
                unit_number
            ) VALUES (
                %(case_id)s,
                'plaintiff',
                %(party_number)s,
                %(first_name)s,
                %(last_name)s,
                %(full_name)s,
                %(plaintiff_type)s,
                %(age_category)s,
                %(is_head_of_household)s,
                %(unit_number)s
            )
            RETURNING id
        """

        count = 0
        for plaintiff in plaintiffs:
            name = plaintiff.PlaintiffItemNumberName
            discovery = plaintiff.PlaintiffItemNumberDiscovery

            age_category = plaintiff.PlaintiffItemNumberAgeCategory[0] if plaintiff.PlaintiffItemNumberAgeCategory else None
            unit_number = discovery.Unit if discovery else None

            params = {
                "case_id": case_id,
                "party_number": plaintiff.ItemNumber,
                "first_name": name.First,
                "last_name": name.Last,
                "full_name": name.FirstAndLast or f"{name.First} {name.Last}",
                "plaintiff_type": plaintiff.PlaintiffItemNumberType,
                "age_category": age_category,
                "is_head_of_household": plaintiff.HeadOfHousehold,
                "unit_number": unit_number
            }

            cur.execute(query, params)
            count += 1

        return count

    def _insert_defendants(self, cur: psycopg.Cursor, case_id: UUID, defendants: List[DefendantDetail]) -> int:
        """
        Insert defendant records

        Args:
            cur: Database cursor
            case_id: Case UUID
            defendants: List of defendant details

        Returns:
            int: Number of defendants inserted
        """
        query = """
            INSERT INTO parties (
                case_id,
                party_type,
                party_number,
                first_name,
                last_name,
                full_name,
                entity_type,
                role
            ) VALUES (
                %(case_id)s,
                'defendant',
                %(party_number)s,
                %(first_name)s,
                %(last_name)s,
                %(full_name)s,
                %(entity_type)s,
                %(role)s
            )
            RETURNING id
        """

        count = 0
        for defendant in defendants:
            name = defendant.DefendantItemNumberName

            params = {
                "case_id": case_id,
                "party_number": defendant.ItemNumber,
                "first_name": name.First,
                "last_name": name.Last,
                "full_name": name.FirstAndLast or f"{name.First or ''} {name.Last or ''}".strip() or "Unknown",
                "entity_type": defendant.DefendantItemNumberType,
                "role": defendant.DefendantItemNumberManagerOwner
            }

            cur.execute(query, params)
            count += 1

        return count

    def _insert_plaintiff_issues(self, cur: psycopg.Cursor, case_id: UUID, plaintiffs: List[PlaintiffDetail]) -> int:
        """
        Insert plaintiff issue selections

        Args:
            cur: Database cursor
            case_id: Case UUID
            plaintiffs: List of plaintiff details

        Returns:
            int: Number of issue selections inserted
        """
        # Load issue category and option mappings
        self._load_issue_cache(cur)

        count = 0

        for plaintiff in plaintiffs:
            if not plaintiff.PlaintiffItemNumberDiscovery:
                continue

            # Get plaintiff party_id
            cur.execute(
                """
                SELECT id FROM parties
                WHERE case_id = %s AND party_type = 'plaintiff' AND party_number = %s
                """,
                (case_id, plaintiff.ItemNumber)
            )
            party_result = cur.fetchone()
            if not party_result:
                logger.warning(f"Plaintiff #{plaintiff.ItemNumber} not found for case {case_id}")
                continue

            party_id = party_result["id"]
            discovery = plaintiff.PlaintiffItemNumberDiscovery

            # Map discovery arrays to issue selections
            issue_mappings = [
                ("vermin", discovery.Vermin or []),
                ("insects", discovery.Insects or []),
                ("hvac", discovery.HVAC or []),
                ("electrical", discovery.Electrical or []),
                ("fire_hazard", discovery.FireHazard or []),
                ("government_entities", discovery.GovernmentEntities or []),
                ("appliances", discovery.Appliances or []),
                ("plumbing", discovery.Plumbing or []),
                ("cabinets", discovery.Cabinets or []),
                ("flooring", discovery.Flooring or []),
                ("windows", discovery.Windows or []),
                ("doors", discovery.Doors or []),
                ("structure", discovery.Structure or []),
                ("common_areas", discovery.CommonAreas or []),
                ("trash_problems", discovery.TrashProblemsSelect or []),
                ("nuisance", discovery.Nuisance or []),
                ("health_hazard", discovery.HealthHazard or []),
                ("safety", discovery.Safety or []),
                ("notices", discovery.Notices or [])
            ]

            for category_code, options in issue_mappings:
                for option_name in options:
                    issue_option_id = self._get_issue_option_id(cur, category_code, option_name)

                    if issue_option_id:
                        cur.execute(
                            """
                            INSERT INTO party_issue_selections (party_id, issue_option_id)
                            VALUES (%s, %s)
                            ON CONFLICT (party_id, issue_option_id) DO NOTHING
                            """,
                            (party_id, issue_option_id)
                        )
                        count += 1
                    else:
                        logger.warning(f"Issue option not found: {category_code} -> {option_name}")

        return count

    def _load_issue_cache(self, cur: psycopg.Cursor):
        """Load issue categories and options into cache"""
        if not self.issue_category_cache:
            cur.execute("SELECT id, category_code FROM issue_categories")
            for row in cur.fetchall():
                self.issue_category_cache[row["category_code"]] = row["id"]

        if not self.issue_option_cache:
            cur.execute("""
                SELECT io.id, ic.category_code, io.option_name
                FROM issue_options io
                JOIN issue_categories ic ON io.category_id = ic.id
            """)
            for row in cur.fetchall():
                key = (row["category_code"], row["option_name"])
                self.issue_option_cache[key] = row["id"]

    def _get_issue_option_id(self, cur: psycopg.Cursor, category_code: str, option_name: str) -> UUID | None:
        """Get issue option ID from cache"""
        return self.issue_option_cache.get((category_code, option_name))
