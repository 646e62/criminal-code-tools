"""
Tests for data ingestion functionality.
"""
import os
from django.test import TestCase, override_settings
from django.core.management import call_command
from io import StringIO
from apps.data_processing.models import CaseMetadata
from apps.data_processing.ingestion.case_metadata import CaseMetadataIngester

@override_settings(CANLII_API_KEY='cgp2ghZSsI5hxraQKS3fe7aNdyzO1aF81HV9syS2')
class CaseMetadataIngestionTests(TestCase):
    def setUp(self):
        os.environ['CANLII_API_KEY'] = 'cgp2ghZSsI5hxraQKS3fe7aNdyzO1aF81HV9syS2'
        self.ingester = CaseMetadataIngester()
        self.sample_citation = "R v Sutherland, 2022 MBCA 23"

    def test_parse_citation(self):
        """Test parsing a citation."""
        metadata = self.ingester.parse_citation(self.sample_citation)
        
        self.assertIsNotNone(metadata)
        self.assertEqual(metadata['year'], '2022')
        self.assertEqual(metadata['court'], 'mbca')
        self.assertIn('case_id', metadata)
        self.assertIn('style_of_cause', metadata)

    def test_ingest_citation(self):
        """Test ingesting a single citation."""
        case = self.ingester.ingest_citation(self.sample_citation)
        
        self.assertIsInstance(case, CaseMetadata)
        self.assertEqual(case.citation, self.sample_citation)
        self.assertEqual(case.year, '2022')
        self.assertEqual(case.court, 'mbca')

    def test_ingest_citations(self):
        """Test ingesting multiple citations."""
        citations = [
            "R v Sutherland, 2022 MBCA 23",
            "R v Currie, 2021 NBCA 3"
        ]
        
        cases = self.ingester.ingest_citations(citations)
        
        self.assertEqual(len(cases), 2)
        self.assertTrue(all(isinstance(case, CaseMetadata) for case in cases))

@override_settings(CANLII_API_KEY='cgp2ghZSsI5hxraQKS3fe7aNdyzO1aF81HV9syS2')
class IngestCasesCommandTests(TestCase):
    def setUp(self):
        os.environ['CANLII_API_KEY'] = 'cgp2ghZSsI5hxraQKS3fe7aNdyzO1aF81HV9syS2'

    def test_command_citations_argument(self):
        """Test the management command with --citations argument."""
        out = StringIO()
        call_command(
            'ingest_cases',
            '--citations',
            'R v Sutherland, 2022 MBCA 23',
            'R v Currie, 2021 NBCA 3',
            stdout=out
        )
        
        self.assertIn('Successfully ingested', out.getvalue())
        self.assertEqual(CaseMetadata.objects.count(), 2)
