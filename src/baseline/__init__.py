"""
Baseline calculation module

This module provides functionality for calculating statistical baselines
from historical data and storing them in BigQuery for anomaly detection.

Components:
- BaselineCalculator: Main calculator for statistical baselines
- AIBaselineOptimizer: AI-driven baseline method optimizer
"""

from .calculator import BaselineCalculator
from .ai_optimizer import AIBaselineOptimizer

__all__ = ['BaselineCalculator', 'AIBaselineOptimizer']

__version__ = '1.0.0'