"""
Management command for ingesting case metadata from various sources.
"""
import sys
from typing import List, TextIO
from django.core.management.base import BaseCommand, CommandError
from apps.data_processing.ingestion.case_metadata import CaseMetadataIngester

class Command(BaseCommand):
    help = 'Ingest case metadata from citations'

    def add_arguments(self, parser):
        parser.add_argument(
            '--citations',
            nargs='+',
            type=str,
            help='List of citations to ingest',
        )
        parser.add_argument(
            '--file',
            type=str,
            help='File containing citations (one per line)',
        )

    def _read_citations_from_file(self, file_path: str) -> List[str]:
        """Read citations from a file, one per line."""
        try:
            with open(file_path, 'r') as f:
                return [line.strip() for line in f if line.strip()]
        except Exception as e:
            raise CommandError(f'Error reading file {file_path}: {str(e)}')

    def _process_citations(self, citations: List[str], stdout: TextIO):
        """Process a list of citations and output results."""
        ingester = CaseMetadataIngester()
        total = len(citations)
        
        for i, citation in enumerate(citations, 1):
            try:
                case = ingester.ingest_citation(citation)
                self.stdout.write(
                    self.style.SUCCESS(
                        f'[{i}/{total}] Successfully ingested: {case.citation}'
                    )
                )
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(
                        f'[{i}/{total}] Error ingesting citation "{citation}": {str(e)}'
                    )
                )

    def handle(self, *args, **options):
        citations = []
        
        if options['citations']:
            citations.extend(options['citations'])
        
        if options['file']:
            citations.extend(self._read_citations_from_file(options['file']))
        
        if not citations:
            raise CommandError(
                'Please provide citations using --citations or --file'
            )

        self.stdout.write(f'Processing {len(citations)} citations...\n')
        self._process_citations(citations, self.stdout)
        self.stdout.write(self.style.SUCCESS('\nDone!'))
