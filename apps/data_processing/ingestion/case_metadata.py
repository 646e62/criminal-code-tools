"""
Module for ingesting case metadata using legal-citation-parser.
"""
import os
from typing import Dict, Any, Optional, List
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


class CaseMetadataIngester:
    """Class for ingesting and processing case metadata."""

    def __init__(self):
        """Initialize with API key from environment."""
        self.api_key = os.getenv('CANLII_API_KEY')
        if not self.api_key:
            raise ValueError("CANLII_API_KEY environment variable is required")

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
            # Parse the citation with metadata and URL verification
            parsed = parse_citation(
                citation_text,
                citation_type="canlii",
                metadata=True,
                verify_url=True
            )
            
            if not parsed:
                raise InvalidCitationError(f"Could not parse citation: {citation_text}")
            
            if not parsed.get('uid') or not parsed.get('court'):
                raise InvalidCitationError(f"Missing required fields in citation: {citation_text}")
            
            # Get metadata from CanLII API
            metadata = CanLIIAPI.api_call(
                case_id=parsed['uid'],
                database_id=parsed['court'],
                decision_metadata=True
            )
            
            if not metadata:
                raise CaseNotFoundError(f"Case not found in CanLII: {citation_text}")
            
            if metadata.get('error'):
                raise CaseNotFoundError(f"CanLII API error: {metadata['error']}")
            
            parsed.update(metadata)
            
            now = timezone.now()
            
            return {
                'case_id': parsed.get('uid'),
                'style_of_cause': parsed.get('style_of_cause'),
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
                'cited_cases': parsed.get('cited_cases', []),
                'citing_cases': parsed.get('citing_cases', []),
                'source_url': parsed.get('long_url'),
                'short_url': parsed.get('short_url'),
                'created_at': now,
                'updated_at': now,
            }
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

    def ingest_citation(self, citation_text: str) -> CaseMetadata:
        """
        Ingest a citation and create or update a CaseMetadata instance.
        
        Args:
            citation_text: The legal citation text to ingest.
            
        Returns:
            Created or updated CaseMetadata instance.
            
        Raises:
            InvalidCitationError: If the citation cannot be parsed.
            CaseNotFoundError: If the case cannot be found in CanLII.
            CaseIngestionError: For other ingestion errors.
        """
        metadata = self.parse_citation(citation_text)
        case_id = metadata.pop('case_id')
        
        # Try to find existing case or create new one
        case, created = CaseMetadata.objects.update_or_create(
            case_id=case_id,
            defaults=metadata
        )
        
        return case

    def ingest_citations(self, citation_texts: List[str]) -> List[CaseMetadata]:
        """
        Ingest multiple citations.
        
        Args:
            citation_texts: List of citation texts to ingest.
            
        Returns:
            List of created or updated CaseMetadata instances.
        """
        return [self.ingest_citation(citation) for citation in citation_texts]
