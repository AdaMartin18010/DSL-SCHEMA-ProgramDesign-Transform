#!/usr/bin/env python3
"""
Tests for Schema Comparator
===========================

Test coverage for schema comparison functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from schema_comparator import (
    SchemaComparator, DifferenceType, ImpactLevel, Difference, ComparisonReport
)


class TestSchemaComparator(unittest.TestCase):
    """Test Schema Comparator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.comparator = SchemaComparator()
        
        self.schema_a = {
            "$id": "schema-a",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "integer"}
            },
            "required": ["id", "name"]
        }
        
        self.schema_b = {
            "$id": "schema-b",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "fullName": {"type": "string"},
                "age": {"type": "integer", "minimum": 0},
                "email": {"type": "string"}
            },
            "required": ["id", "fullName", "email"]
        }
    
    def test_initialization(self):
        """Test comparator initialization"""
        self.assertIsNotNone(self.comparator.impact_rules)
        self.assertIn("required_removed", self.comparator.impact_rules)
    
    def test_compare_basic(self):
        """Test basic comparison"""
        report = self.comparator.compare(self.schema_a, self.schema_b, "A", "B")
        
        self.assertIsInstance(report, ComparisonReport)
        self.assertEqual(report.schema_a_name, "A")
        self.assertEqual(report.schema_b_name, "B")
        self.assertTrue(len(report.differences) > 0)
    
    def test_compare_identical_schemas(self):
        """Test comparing identical schemas"""
        report = self.comparator.compare(self.schema_a, self.schema_a, "A", "A")
        
        # Identical schemas should have high similarity
        self.assertEqual(report.similarity_score, 1.0)
        self.assertEqual(len(report.differences), 0)
    
    def test_detect_added_property(self):
        """Test detecting added properties"""
        old = {"type": "object", "properties": {"a": {"type": "string"}}}
        new = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "integer"}}}
        
        report = self.comparator.compare(old, new)
        
        added = [d for d in report.differences if d.type == DifferenceType.ADDED]
        self.assertTrue(any("b" in d.path for d in added))
    
    def test_detect_removed_property(self):
        """Test detecting removed properties"""
        old = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "integer"}}}
        new = {"type": "object", "properties": {"a": {"type": "string"}}}
        
        report = self.comparator.compare(old, new)
        
        removed = [d for d in report.differences if d.type == DifferenceType.REMOVED]
        self.assertTrue(any("b" in d.path for d in removed))
    
    def test_detect_type_change(self):
        """Test detecting type changes"""
        old = {"type": "object", "properties": {"age": {"type": "string"}}}
        new = {"type": "object", "properties": {"age": {"type": "integer"}}}
        
        report = self.comparator.compare(old, new)
        
        type_changes = [d for d in report.differences if d.type == DifferenceType.TYPE_CHANGED]
        self.assertEqual(len(type_changes), 1)
        self.assertEqual(type_changes[0].old_value, "string")
        self.assertEqual(type_changes[0].new_value, "integer")
    
    def test_detect_constraint_change(self):
        """Test detecting constraint changes"""
        old = {"type": "object", "properties": {"age": {"type": "integer"}}}
        new = {"type": "object", "properties": {"age": {"type": "integer", "minimum": 0}}}
        
        report = self.comparator.compare(old, new)
        
        constraint_changes = [d for d in report.differences if d.type == DifferenceType.CONSTRAINT_CHANGED]
        self.assertEqual(len(constraint_changes), 1)
    
    def test_breaking_changes_detection(self):
        """Test breaking changes detection"""
        old = {"type": "object", "properties": {"field": {"type": "string"}}, "required": ["field"]}
        new = {"type": "object", "properties": {}}  # Removed required field
        
        report = self.comparator.compare(old, new)
        
        self.assertTrue(len(report.breaking_changes) > 0)
        self.assertTrue(all(d.impact == ImpactLevel.BREAKING for d in report.breaking_changes))
    
    def test_calculate_similarity(self):
        """Test similarity calculation"""
        a = {"type": "string"}
        b = {"type": "string"}
        c = {"type": "integer"}
        
        sim_ab = self.comparator._calculate_similarity(a, b)
        sim_ac = self.comparator._calculate_similarity(a, c)
        
        self.assertEqual(sim_ab, 1.0)
        self.assertLess(sim_ac, 1.0)
    
    def test_calculate_structural_similarity(self):
        """Test structural similarity calculation"""
        a = {"type": "object", "properties": {"x": {}, "y": {}}}
        b = {"type": "object", "properties": {"x": {}, "z": {}}}
        
        sim = self.comparator._calculate_structural_similarity(a, b)
        
        # Should be around 0.33 (1 common out of 3 total unique paths)
        self.assertGreater(sim, 0)
        self.assertLess(sim, 1.0)
    
    def test_get_all_paths(self):
        """Test getting all paths from schema"""
        schema = {
            "type": "object",
            "properties": {
                "a": {"type": "string"},
                "b": {"type": "object", "properties": {"c": {}}}
            }
        }
        
        paths = self.comparator._get_all_paths(schema)
        
        self.assertIn("type", paths)
        self.assertIn("properties", paths)
        self.assertIn("properties.a", paths)
        self.assertIn("properties.b", paths)
        self.assertIn("properties.b.properties", paths)
    
    def test_assess_impact(self):
        """Test impact assessment"""
        impact = self.comparator._assess_impact("properties.test", None, {"type": "string"})
        self.assertEqual(impact, ImpactLevel.MINOR)
        
        impact = self.comparator._assess_impact("properties.test", {"type": "string"}, None)
        self.assertEqual(impact, ImpactLevel.BREAKING)
    
    def test_generate_recommendations(self):
        """Test recommendations generation"""
        differences = [
            Difference(
                type=DifferenceType.REMOVED,
                path="properties.field",
                impact=ImpactLevel.BREAKING,
                description="Removed field"
            )
        ]
        
        recommendations = self.comparator._generate_recommendations(differences)
        
        self.assertTrue(len(recommendations) > 0)
        self.assertTrue(any("breaking" in r.lower() for r in recommendations))
    
    def test_merge_union(self):
        """Test union merge strategy"""
        a = {"properties": {"x": {"type": "string"}}}
        b = {"properties": {"y": {"type": "integer"}}}
        
        merged = self.comparator._merge_union(a, b)
        
        self.assertIn("x", merged["properties"])
        self.assertIn("y", merged["properties"])
    
    def test_merge_intersection(self):
        """Test intersection merge strategy"""
        a = {"properties": {"x": {"type": "string"}, "y": {"type": "integer"}}}
        b = {"properties": {"x": {"type": "string"}, "z": {"type": "boolean"}}}
        
        merged = self.comparator._merge_intersection(a, b)
        
        self.assertIn("x", merged["properties"])
        self.assertNotIn("y", merged["properties"])
        self.assertNotIn("z", merged["properties"])
    
    def test_merge_prefer_a(self):
        """Test prefer A merge strategy"""
        a = {"type": "string"}
        b = {"type": "integer"}
        
        merged = self.comparator._merge_prefer_a(a, b)
        
        self.assertEqual(merged["type"], "string")
    
    def test_merge_prefer_b(self):
        """Test prefer B merge strategy"""
        a = {"type": "string"}
        b = {"type": "integer"}
        
        merged = self.comparator._merge_prefer_b(a, b)
        
        self.assertEqual(merged["type"], "integer")


class TestDifference(unittest.TestCase):
    """Test Difference dataclass"""
    
    def test_difference_creation(self):
        """Test creating a difference"""
        diff = Difference(
            type=DifferenceType.ADDED,
            path="properties.newField",
            new_value={"type": "string"},
            description="Added new field",
            impact=ImpactLevel.MINOR
        )
        
        self.assertEqual(diff.type, DifferenceType.ADDED)
        self.assertEqual(diff.path, "properties.newField")
        self.assertEqual(diff.impact, ImpactLevel.MINOR)


class TestComparisonReport(unittest.TestCase):
    """Test ComparisonReport dataclass"""
    
    def test_report_creation(self):
        """Test creating a comparison report"""
        report = ComparisonReport(
            schema_a_name="Schema A",
            schema_b_name="Schema B",
            differences=[],
            similarity_score=0.85,
            structural_similarity=0.9,
            semantic_similarity=0.8,
            breaking_changes=[],
            recommendations=["No changes needed"]
        )
        
        self.assertEqual(report.schema_a_name, "Schema A")
        self.assertEqual(report.similarity_score, 0.85)
        self.assertEqual(len(report.recommendations), 1)


if __name__ == "__main__":
    unittest.main()
