#!/usr/bin/env python3
"""
Tests for Schema Migration
==========================

Test coverage for schema migration functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from schema_migration import (
    SchemaMigrationEngine, MigrationType, CompatibilityLevel,
    MigrationStep, MigrationPlan, MigrationResult
)


class TestSchemaMigrationEngine(unittest.TestCase):
    """Test Schema Migration Engine"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.engine = SchemaMigrationEngine()
        
        self.old_schema = {
            "version": "1.0.0",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "name": {"type": "string"},
                "age": {"type": "string"}
            },
            "required": ["id", "name"]
        }
        
        self.new_schema = {
            "version": "2.0.0",
            "type": "object",
            "properties": {
                "id": {"type": "string"},
                "fullName": {"type": "string"},
                "age": {"type": "integer"},
                "email": {"type": "string"}
            },
            "required": ["id", "fullName", "email"]
        }
    
    def test_initialization(self):
        """Test engine initialization"""
        self.assertIsNotNone(self.engine.transform_registry)
        self.assertIn("string_to_int", self.engine.transform_registry)
    
    def test_compare_schemas_add_field(self):
        """Test detecting added fields"""
        old = {"type": "object", "properties": {"a": {"type": "string"}}}
        new = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "integer"}}}
        
        steps = self.engine.compare_schemas(old, new)
        
        add_steps = [s for s in steps if s.type == MigrationType.ADD_FIELD]
        self.assertEqual(len(add_steps), 1)
        self.assertIn("b", add_steps[0].path)
    
    def test_compare_schemas_remove_field(self):
        """Test detecting removed fields"""
        old = {"type": "object", "properties": {"a": {"type": "string"}, "b": {"type": "integer"}}}
        new = {"type": "object", "properties": {"a": {"type": "string"}}}
        
        steps = self.engine.compare_schemas(old, new)
        
        remove_steps = [s for s in steps if s.type == MigrationType.REMOVE_FIELD]
        self.assertEqual(len(remove_steps), 1)
        self.assertIn("b", remove_steps[0].path)
    
    def test_compare_schemas_change_type(self):
        """Test detecting type changes"""
        old = {"type": "object", "properties": {"age": {"type": "string"}}}
        new = {"type": "object", "properties": {"age": {"type": "integer"}}}
        
        steps = self.engine.compare_schemas(old, new)
        
        change_steps = [s for s in steps if s.type == MigrationType.CHANGE_TYPE]
        self.assertEqual(len(change_steps), 1)
        self.assertEqual(change_steps[0].old_value, "string")
        self.assertEqual(change_steps[0].new_value, "integer")
    
    def test_create_migration_plan(self):
        """Test migration plan creation"""
        plan = self.engine.create_migration_plan(
            self.old_schema, self.new_schema, "1.0.0", "2.0.0"
        )
        
        self.assertIsInstance(plan, MigrationPlan)
        self.assertEqual(plan.from_version, "1.0.0")
        self.assertEqual(plan.to_version, "2.0.0")
        self.assertTrue(len(plan.steps) > 0)
        self.assertIsNotNone(plan.compatibility)
    
    def test_calculate_compatibility_full(self):
        """Test full compatibility"""
        steps = []
        compat = self.engine._calculate_compatibility(steps)
        self.assertEqual(compat, CompatibilityLevel.FULL)
    
    def test_calculate_compatibility_backward(self):
        """Test backward compatibility"""
        steps = [
            MigrationStep(type=MigrationType.ADD_FIELD, path="properties.newField")
        ]
        compat = self.engine._calculate_compatibility(steps)
        self.assertEqual(compat, CompatibilityLevel.BACKWARD)
    
    def test_calculate_compatibility_none(self):
        """Test no compatibility"""
        steps = [
            MigrationStep(type=MigrationType.REMOVE_FIELD, path="properties.oldField"),
            MigrationStep(type=MigrationType.ADD_FIELD, path="properties.newField")
        ]
        compat = self.engine._calculate_compatibility(steps)
        self.assertEqual(compat, CompatibilityLevel.NONE)
    
    def test_migrate_data_add_field(self):
        """Test data migration with added field"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[
                MigrationStep(
                    type=MigrationType.ADD_FIELD,
                    path="properties.email",
                    new_value={"type": "string", "default": "unknown@example.com"},
                    description="Add email field"
                )
            ],
            compatibility=CompatibilityLevel.BACKWARD,
            estimated_impact=100
        )
        
        data = [{"id": "1", "name": "Alice"}]
        result = self.engine.migrate_data(data, plan, dry_run=False)
        
        self.assertIsInstance(result, MigrationResult)
        self.assertEqual(result.migrated_count, 1)
        self.assertEqual(result.failed_count, 0)
        self.assertEqual(data[0]["email"], "unknown@example.com")
    
    def test_migrate_data_remove_field(self):
        """Test data migration with removed field"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[
                MigrationStep(
                    type=MigrationType.REMOVE_FIELD,
                    path="properties.oldField",
                    description="Remove old field"
                )
            ],
            compatibility=CompatibilityLevel.FORWARD,
            estimated_impact=100
        )
        
        data = [{"id": "1", "oldField": "value"}]
        result = self.engine.migrate_data(data, plan, dry_run=False)
        
        self.assertEqual(result.migrated_count, 1)
        self.assertNotIn("oldField", data[0])
    
    def test_generate_migration_script_python(self):
        """Test Python script generation"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[],
            compatibility=CompatibilityLevel.FULL,
            estimated_impact=100
        )
        
        script = self.engine.generate_migration_script(plan, "python")
        
        self.assertIn("#!/usr/bin/env python3", script)
        self.assertIn("def migrate(data):", script)
    
    def test_generate_migration_script_javascript(self):
        """Test JavaScript script generation"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[],
            compatibility=CompatibilityLevel.FULL,
            estimated_impact=100
        )
        
        script = self.engine.generate_migration_script(plan, "javascript")
        
        self.assertIn("function migrate(data)", script)
        self.assertIn("module.exports", script)
    
    def test_validate_migration_success(self):
        """Test successful migration validation"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[],
            compatibility=CompatibilityLevel.FULL,
            estimated_impact=100
        )
        
        old_data = [{"id": "1"}]
        new_data = [{"id": "1"}]
        
        valid, issues = self.engine.validate_migration(old_data, new_data, plan)
        
        self.assertTrue(valid)
        self.assertEqual(len(issues), 0)
    
    def test_validate_migration_count_mismatch(self):
        """Test migration validation with count mismatch"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[],
            compatibility=CompatibilityLevel.FULL,
            estimated_impact=100
        )
        
        old_data = [{"id": "1"}, {"id": "2"}]
        new_data = [{"id": "1"}]
        
        valid, issues = self.engine.validate_migration(old_data, new_data, plan)
        
        self.assertFalse(valid)
        self.assertTrue(any("count mismatch" in i.lower() for i in issues))


class TestMigrationStep(unittest.TestCase):
    """Test MigrationStep dataclass"""
    
    def test_step_creation(self):
        """Test creating a migration step"""
        step = MigrationStep(
            type=MigrationType.ADD_FIELD,
            path="properties.email",
            new_value={"type": "string"},
            description="Add email field"
        )
        
        self.assertEqual(step.type, MigrationType.ADD_FIELD)
        self.assertEqual(step.path, "properties.email")


class TestMigrationPlan(unittest.TestCase):
    """Test MigrationPlan dataclass"""
    
    def test_plan_creation(self):
        """Test creating a migration plan"""
        plan = MigrationPlan(
            from_version="1.0.0",
            to_version="2.0.0",
            steps=[],
            compatibility=CompatibilityLevel.BACKWARD,
            estimated_impact=1000
        )
        
        self.assertEqual(plan.from_version, "1.0.0")
        self.assertEqual(plan.to_version, "2.0.0")
        self.assertEqual(plan.compatibility, CompatibilityLevel.BACKWARD)


class TestMigrationResult(unittest.TestCase):
    """Test MigrationResult dataclass"""
    
    def test_result_creation(self):
        """Test creating a migration result"""
        result = MigrationResult(
            success=True,
            migrated_count=100,
            failed_count=0,
            errors=[],
            warnings=[],
            duration_ms=150.5
        )
        
        self.assertTrue(result.success)
        self.assertEqual(result.migrated_count, 100)
        self.assertEqual(result.duration_ms, 150.5)


if __name__ == "__main__":
    unittest.main()
