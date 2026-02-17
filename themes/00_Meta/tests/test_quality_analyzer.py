#!/usr/bin/env python3
"""
Tests for Quality Analyzer
==========================

Test coverage for schema quality analysis functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from quality_analyzer import (
    QualityAnalyzer, QualityCategory, Severity, QualityIssue, QualityReport
)


class TestQualityAnalyzer(unittest.TestCase):
    """Test Quality Analyzer"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = QualityAnalyzer()
    
    def test_initialization(self):
        """Test analyzer initialization"""
        self.assertIsNotNone(self.analyzer.rules)
        self.assertTrue(len(self.analyzer.rules) > 0)
    
    def test_analyze_perfect_schema(self):
        """Test analyzing a high-quality schema"""
        schema = {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "$id": "test-schema",
            "title": "Test Schema",
            "description": "A well-documented test schema",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "Unique identifier",
                    "minLength": 1,
                    "maxLength": 100
                },
                "name": {
                    "type": "string",
                    "description": "Name field",
                    "minLength": 1,
                    "maxLength": 255
                },
                "count": {
                    "type": "integer",
                    "description": "Count value",
                    "minimum": 0,
                    "maximum": 1000
                }
            },
            "required": ["id", "name"],
            "additionalProperties": False
        }
        
        report = self.analyzer.analyze(schema)
        
        self.assertIsInstance(report, QualityReport)
        self.assertGreater(report.overall_score, 70)
        self.assertIsInstance(report.category_scores, dict)
    
    def test_analyze_poor_schema(self):
        """Test analyzing a low-quality schema"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "value": {"type": "integer"}
            }
        }
        
        report = self.analyzer.analyze(schema)
        
        # Should have issues due to missing descriptions, constraints, etc.
        self.assertTrue(report.total_issues > 0)
    
    def test_detect_circular_refs(self):
        """Test circular reference detection"""
        # This schema doesn't actually have circular refs
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        has_circular = self.analyzer._has_circular_refs(schema)
        self.assertFalse(has_circular)
    
    def test_count_depth(self):
        """Test depth counting"""
        schema = {
            "type": "object",
            "properties": {
                "level1": {
                    "type": "object",
                    "properties": {
                        "level2": {
                            "type": "object",
                            "properties": {
                                "level3": {"type": "string"}
                            }
                        }
                    }
                }
            }
        }
        
        depth = self.analyzer._count_depth(schema)
        self.assertGreaterEqual(depth, 3)
    
    def test_has_field_descriptions(self):
        """Test field description checking"""
        schema_with_desc = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "description": "Name field"}
            }
        }
        
        schema_without_desc = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        self.assertTrue(self.analyzer._has_field_descriptions(schema_with_desc))
        self.assertFalse(self.analyzer._has_field_descriptions(schema_without_desc))
    
    def test_has_string_constraints(self):
        """Test string constraint checking"""
        schema_with_constraints = {
            "type": "object",
            "properties": {
                "name": {"type": "string", "minLength": 1, "maxLength": 100}
            }
        }
        
        schema_without_constraints = {
            "type": "object",
            "properties": {
                "name": {"type": "string"}
            }
        }
        
        self.assertTrue(self.analyzer._has_string_constraints(schema_with_constraints))
        self.assertFalse(self.analyzer._has_string_constraints(schema_without_constraints))
    
    def test_has_number_constraints(self):
        """Test number constraint checking"""
        schema_with_constraints = {
            "type": "object",
            "properties": {
                "age": {"type": "integer", "minimum": 0, "maximum": 150}
            }
        }
        
        schema_without_constraints = {
            "type": "object",
            "properties": {
                "age": {"type": "integer"}
            }
        }
        
        self.assertTrue(self.analyzer._has_number_constraints(schema_with_constraints))
        self.assertFalse(self.analyzer._has_number_constraints(schema_without_constraints))
    
    def test_count_properties(self):
        """Test property counting"""
        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "integer"},
                "c": {"type": "boolean"}
            }
        }
        
        count = self.analyzer._count_properties(schema)
        self.assertEqual(count, 3)
    
    def test_has_sensitive_fields(self):
        """Test sensitive field detection"""
        schema_with_sensitive = {
            "type": "object",
            "properties": {
                "password": {"type": "string"}
            }
        }
        
        schema_without_sensitive = {
            "type": "object",
            "properties": {
                "username": {"type": "string"}
            }
        }
        
        self.assertTrue(self.analyzer._has_sensitive_fields(schema_with_sensitive))
        self.assertFalse(self.analyzer._has_sensitive_fields(schema_without_sensitive))


class TestQualityIssue(unittest.TestCase):
    """Test QualityIssue dataclass"""
    
    def test_issue_creation(self):
        """Test creating a quality issue"""
        issue = QualityIssue(
            category=QualityCategory.STRUCTURE,
            severity=Severity.HIGH,
            message="Missing required field",
            path="$.properties.name",
            suggestion="Add the field to required list",
            rule_id="STRUCT-001"
        )
        
        self.assertEqual(issue.category, QualityCategory.STRUCTURE)
        self.assertEqual(issue.severity, Severity.HIGH)
        self.assertEqual(issue.rule_id, "STRUCT-001")


class TestQualityReport(unittest.TestCase):
    """Test QualityReport dataclass"""
    
    def test_report_creation(self):
        """Test creating a quality report"""
        report = QualityReport(
            overall_score=85.5,
            total_issues=3,
            category_scores={},
            critical_issues=[],
            recommendations=["Add descriptions", "Add constraints"]
        )
        
        self.assertEqual(report.overall_score, 85.5)
        self.assertEqual(report.total_issues, 3)
        self.assertEqual(len(report.recommendations), 2)


if __name__ == "__main__":
    unittest.main()
