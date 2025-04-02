"""
Module for ingesting case metadata using legal-citation-parser.
"""
import os
import time
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime
from django.utils import timezone
from legal_citation_parser import parse_citation
from legal_citation_parser.utils import CanLIIAPI
from apps.data_processing.models import CaseMetadata


class CaseIngestionError(Exception):
    """Base exception for case ingestion errors."""
    pass


class CaseNotFoundError(CaseIngestionError):
    """Exception raised when a case cannot be found."""
    pass


class InvalidCitationError(CaseIngestionError):
    """Exception raised when a citation cannot be parsed."""
    pass


class CaseAlreadyExistsError(CaseIngestionError):
    """Exception raised when attempting to ingest a case that already exists."""
    pass


class CaseMetadataIngester:
    """Class for ingesting and processing case metadata."""

    def __init__(self):
        """Initialize with API key from environment."""
        self.api_key = os.getenv('CANLII_API_KEY')
        if not self.api_key:
            raise ValueError("CANLII_API_KEY environment variable is required")
        # Set the API key for the static CanLIIAPI class
        CanLIIAPI.api_key = self.api_key

    def check_case_exists(self, citation_text: str) -> Optional[CaseMetadata]:
        """
        Check if a case with the given citation already exists.
        
        Args:
            citation_text: The citation text to check.
            
        Returns:
            The existing CaseMetadata instance if found, None otherwise.
        """
        try:
            # Try to find by exact citation first
            return CaseMetadata.objects.get(citation=citation_text)
        except CaseMetadata.DoesNotExist:
            # If not found by citation, parse it to get the case_id and try that
            try:
                parsed = parse_citation(
                    citation_text,
                    citation_type="canlii",
                    metadata=True,
                    verify_url=True
                )
                if parsed and parsed.get('uid'):
                    try:
                        return CaseMetadata.objects.get(case_id=parsed['uid'])
                    except CaseMetadata.DoesNotExist:
                        return None
            except Exception:
                return None
        return None

    def format_cited_cases(self, cited_cases_data: Dict) -> List[Dict[str, str]]:
        """
        Format cited cases data from the parser into our standard format.
        
        Args:
            cited_cases_data: The cited_cases data from the parser.
            
        Returns:
            List of dictionaries containing citation information.
            Each dictionary contains 'citation', 'case_id', and 'title' keys.
        """
        formatted_cases = []
        if cited_cases_data and 'citedCases' in cited_cases_data:
            for cite in cited_cases_data['citedCases']:
                if isinstance(cite, dict):
                    case_id = cite.get('caseId', {}).get('en', '')
                    citation = cite.get('citation', '')
                    title = cite.get('title', '')
                    if case_id and citation:
                        formatted_cases.append({
                            'citation': citation,
                            'case_id': case_id,
                            'title': title
                        })
        return formatted_cases

    def parse_citation(self, citation_text: str) -> Dict[str, Any]:
        """
        Parse a legal citation and extract metadata.
        
        Args:
            citation_text: The legal citation text to parse.
            
        Returns:
            Dictionary containing parsed metadata.
            
        Raises:
            InvalidCitationError: If the citation cannot be parsed.
            CaseNotFoundError: If the case cannot be found in CanLII.
        """
        try:
            # Parse the citation with metadata and cited cases
            parsed = parse_citation(
                citation_text,
                citation_type="canlii",
                metadata=True,
                verify_url=True,
                cited=True  # Get cited cases
            )
            
            if not parsed:
                raise InvalidCitationError(f"Could not parse citation: {citation_text}")
            
            if not parsed.get('uid') or not parsed.get('court'):
                raise InvalidCitationError(f"Missing required fields in citation: {citation_text}")
            
            # Format cited cases
            cited_cases = self.format_cited_cases(parsed.get('cited_cases', {}))
            
            # Get metadata from CanLII API
            metadata = CanLIIAPI.api_call(
                case_id=parsed['uid'],
                database_id=parsed['court'],
                decision_metadata=True
            )
            
            # Add metadata from CanLII API
            parsed.update(metadata)
            
            # Format the metadata for our model
            now = timezone.now()
            result = {
                'case_id': parsed['uid'],
                'style_of_cause': parsed.get('style_of_cause', ''),
                'citation': citation_text,
                'citation_type': CaseMetadata.CitationType.CANLII,
                'year': parsed.get('year'),
                'court': parsed.get('court'),
                'jurisdiction': parsed.get('jurisdiction'),
                'court_level': parsed.get('court_level'),
                'court_name': parsed.get('court_name'),
                'decision_number': parsed.get('decision_number'),
                'docket_number': parsed.get('docket_number'),
                'official_reporter_citation': parsed.get('official_reporter_citation'),
                'decision_date': timezone.make_aware(self._parse_date(parsed.get('decision_date'))) if self._parse_date(parsed.get('decision_date')) else None,
                'language': parsed.get('language', 'en'),  # Default to English
                'keywords': parsed.get('keywords', []),
                'categories': parsed.get('categories', []),
                'cited_cases': cited_cases,
                'citing_cases': parsed.get('citing_cases', []),
                'source_url': parsed.get('long_url'),
                'short_url': parsed.get('short_url'),
                'created_at': now,
                'updated_at': now,
            }
            return result
            
        except Exception as e:
            if isinstance(e, CaseIngestionError):
                raise
            raise CaseIngestionError(f"Error processing citation: {str(e)}")

    def _parse_date(self, date_str: Optional[str]) -> Optional[datetime]:
        """
        Parse a date string into a datetime object.
        
        Args:
            date_str: Date string to parse.
            
        Returns:
            Datetime object or None if parsing fails.
        """
        if not date_str:
            return None
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            try:
                return datetime.strptime(date_str, '%Y-%m')
            except ValueError:
                try:
                    return datetime.strptime(date_str, '%Y')
                except ValueError:
                    return None

    def ingest_citation(self, citation_text: str, force: bool = False) -> Tuple[CaseMetadata, bool]:
        """
        Ingest a citation and create or update a CaseMetadata instance.
        
        Args:
            citation_text: The legal citation text to ingest.
            force: If True, update existing cases. If False, raise CaseAlreadyExistsError.
            
        Returns:
            Tuple of (CaseMetadata instance, bool indicating if case was created).
            
        Raises:
            InvalidCitationError: If the citation cannot be parsed.
            CaseNotFoundError: If the case cannot be found in CanLII.
            CaseAlreadyExistsError: If the case exists and force=False.
            CaseIngestionError: For other ingestion errors.
        """
        # Check if case already exists
        existing_case = self.check_case_exists(citation_text)
        if existing_case and not force:
            raise CaseAlreadyExistsError(f"Case already exists: {citation_text}")

        # Parse the citation and get metadata
        metadata = self.parse_citation(citation_text)
        
        # Get case_id from metadata
        case_id = metadata.pop('case_id')
        
        # Try to find existing case or create new one
        try:
            case, created = CaseMetadata.objects.update_or_create(
                case_id=case_id,
                defaults=metadata
            )
            return case, created
        except Exception as e:
            raise CaseIngestionError(f"Error saving case metadata: {str(e)}")

    def ingest_citations(self, citation_texts: List[str], force: bool = False) -> List[Tuple[CaseMetadata, bool]]:
        """
        Ingest multiple citations.
        
        Args:
            citation_texts: List of citation texts to ingest.
            force: If True, update existing cases. If False, raise CaseAlreadyExistsError.
            
        Returns:
            List of tuples (CaseMetadata instance, bool indicating if case was created).
        """
        return [self.ingest_citation(citation, force=force) for citation in citation_texts]
