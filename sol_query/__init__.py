"""
sol_query: A comprehensive Python-based code query engine for Solidity

This package provides a powerful query interface for analyzing Solidity smart contracts,
offering both traditional and Glider-style query capabilities.
"""

__version__ = "0.1.0"

from sol_query.query.engine import SolidityQueryEngine

__all__ = ["SolidityQueryEngine"]