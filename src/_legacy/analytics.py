"""
Analytics module for criminal code offence analysis.

This module provides tools for analyzing criminal code offences and sentencing patterns,
with capabilities to handle different types of punishments and standardized time units.
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
from typing import Dict, List, Optional, Union
from utils import parse_quantum, convert_quantum_to_days, ParsedQuantum

class SentenceAnalyzer:
    def __init__(self, data_dir: str):
        self.data_dir = Path(data_dir)
        self.offences_data = None
        self.sentencing_data = None
        
    def load_data(self):
        """Load all CSV files from the data directory"""
        # Load Criminal Code offences
        self.cc_offences = pd.read_csv(self.data_dir / 'cc-offences-2024-09-16.csv')
        
        # Load sentencing data from different jurisdictions
        sentencing_files = list(self.data_dir.glob('sentencing-data/*.csv'))
        self.sentencing_data = pd.concat([
            pd.read_csv(f) for f in sentencing_files
        ], ignore_index=True)
    
    def basic_offence_statistics(self) -> Dict[str, Dict[str, Union[int, float]]]:
        """
        Calculate basic statistics about offences, including sentence types and durations.
        All time-based measurements are converted to days for consistency.
        
        Returns:
            Dict containing statistics for different punishment types and their frequencies
        """
        if self.cc_offences is None:
            raise ValueError("Data not loaded. Call load_data() first.")
            
        stats = {
            'jail': {'count': 0, 'avg_duration': 0.0, 'min_duration': float('inf'), 'max_duration': 0.0},
            'probation': {'count': 0, 'avg_duration': 0.0, 'min_duration': float('inf'), 'max_duration': 0.0},
            'cso': {'count': 0, 'avg_duration': 0.0, 'min_duration': float('inf'), 'max_duration': 0.0},
            'fine': {'count': 0, 'avg_amount': 0.0, 'min_amount': float('inf'), 'max_amount': 0.0}
        }
        
        # Process maximum indictable sentences
        for _, row in self.cc_offences.iterrows():
            if pd.notna(row['maximum_indictable']):
                quantum = parse_quantum(str(row['maximum_indictable']))
                
                # Handle jail time
                if quantum['jail']['amount'] != 0:
                    converted = convert_quantum_to_days(quantum)
                    if converted:
                        days = converted['jail']['amount']
                        stats['jail']['count'] += 1
                        stats['jail']['avg_duration'] += days
                        stats['jail']['min_duration'] = min(stats['jail']['min_duration'], days)
                        stats['jail']['max_duration'] = max(stats['jail']['max_duration'], days)
                
                # Handle fines
                if quantum['fine']['amount'] != 0:
                    amount = float(quantum['fine']['amount'])
                    stats['fine']['count'] += 1
                    stats['fine']['avg_amount'] += amount
                    stats['fine']['min_amount'] = min(stats['fine']['min_amount'], amount)
                    stats['fine']['max_amount'] = max(stats['fine']['max_amount'], amount)
        
        # Calculate averages
        for category in stats:
            if stats[category]['count'] > 0:
                if category == 'fine':
                    stats[category]['avg_amount'] /= stats[category]['count']
                    if stats[category]['min_amount'] == float('inf'):
                        stats[category]['min_amount'] = 0
                else:
                    stats[category]['avg_duration'] /= stats[category]['count']
                    if stats[category]['min_duration'] == float('inf'):
                        stats[category]['min_duration'] = 0
        
        return stats
    
    def analyze_sentence_distribution(self) -> pd.DataFrame:
        """
        Analyze the distribution of sentence types and durations from actual sentencing data.
        All durations are converted to days for consistency.
        
        Returns:
            DataFrame with sentence distribution statistics
        """
        if self.sentencing_data is None:
            raise ValueError("Data not loaded. Call load_data() first.")
        
        results = []
        for _, row in self.sentencing_data.iterrows():
            if pd.notna(row['jail']):
                quantum = parse_quantum(str(row['jail']))
                converted = convert_quantum_to_days(quantum)
                if converted:
                    results.append({
                        'offence': row['offence'],
                        'type': 'jail',
                        'duration_days': converted['jail']['amount'],
                        'jurisdiction': row['uid'][:2]
                    })
        
        return pd.DataFrame(results)
    
    def plot_sentence_distribution(self):
        """Create visualizations of sentence distributions"""
        distribution_data = self.analyze_sentence_distribution()
        
        # Create box plot of sentence lengths by offence type
        plt.figure(figsize=(15, 8))
        sns.boxplot(data=distribution_data, x='offence', y='duration_days')
        plt.xticks(rotation=45)
        plt.title('Distribution of Sentence Lengths by Offence (in days)')
        plt.tight_layout()
        
        return plt
