#!/usr/bin/env python3
"""
Tests for Documentation Generator
==================================

Test coverage for documentation generation functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from documentation_generator import (
    DocumentationGenerator, DocSection, APIDoc
)


class TestDocumentationGenerator(unittest.TestCase):
    """Test Documentation Generator"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.generator = DocumentationGenerator()
        
        self.test_schema = {
            "$schema": "https://json-schema.org/draft/2025-01/schema",
            "$id": "user",
            "title": "User Schema",
            "description": "User profile schema",
            "type": "object",
            "properties": {
                "id": {
                    "type": "string",
                    "description": "User ID"
                },
                "name": {
                    "type": "string",
                    "minLength": 1,
                    "maxLength": 100,
                    "description": "User name"
                },
                "email": {
                    "type": "string",
                    "format": "email",
                    "description": "Email address"
                }
            },
            "required": ["id", "name"],
            "examples": [
                {"id": "user-1", "name": "Alice", "email": "alice@example.com"}
            ]
        }
    
    def test_initialization(self):
        """Test generator initialization"""
        self.assertIsNotNone(self.generator.templates)
        self.assertIn("schema_doc", self.generator.templates)
        self.assertIn("api_doc", self.generator.templates)
        self.assertIn("changelog", self.generator.templates)
    
    def test_generate_schema_doc(self):
        """Test schema document generation"""
        doc = self.generator.generate_schema_doc(self.test_schema)
        
        self.assertIn("# User Schema", doc)
        self.assertIn("## 概述", doc)
        self.assertIn("## Schema定义", doc)
        self.assertIn("## 属性说明", doc)
        self.assertIn("id", doc)
        self.assertIn("name", doc)
        self.assertIn("email", doc)
    
    def test_generate_properties_table(self):
        """Test properties table generation"""
        table = self.generator._generate_properties_table(self.test_schema)
        
        self.assertIn("| 属性名 |", table)
        self.assertIn("| 类型 |", table)
        self.assertIn("| 必需 |", table)
        self.assertIn("| id |", table)
        self.assertIn("| name |", table)
        self.assertIn("| email |", table)
    
    def test_generate_valid_examples(self):
        """Test valid example generation"""
        examples = self.generator._generate_valid_examples(self.test_schema)
        
        self.assertIsInstance(examples, list)
        self.assertTrue(len(examples) > 0)
        
        first_example = examples[0]
        self.assertIn("id", first_example)
        self.assertIn("name", first_example)
    
    def test_generate_example_from_schema_object(self):
        """Test example generation for object schema"""
        example = self.generator._generate_example_from_schema(self.test_schema)
        
        self.assertIsInstance(example, dict)
        self.assertIn("id", example)
        self.assertIn("name", example)
    
    def test_generate_example_from_schema_string(self):
        """Test example generation for string schema"""
        string_schema = {"type": "string", "format": "email"}
        example = self.generator._generate_example_from_schema(string_schema)
        
        self.assertIsInstance(example, str)
        self.assertIn("@", example)  # Email format
    
    def test_generate_example_from_schema_integer(self):
        """Test example generation for integer schema"""
        int_schema = {"type": "integer", "minimum": 10}
        example = self.generator._generate_example_from_schema(int_schema)
        
        self.assertIsInstance(example, int)
        self.assertGreaterEqual(example, 10)
    
    def test_infer_usage_scenarios(self):
        """Test usage scenario inference"""
        scenarios = self.generator._infer_usage_scenarios(self.test_schema)
        
        self.assertIsInstance(scenarios, str)
        # User schema should suggest user management scenario
        self.assertIn("用户", scenarios)
    
    def test_find_related_schemas(self):
        """Test related schema finding"""
        schema_with_ref = {
            "type": "object",
            "properties": {
                "user": {"$ref": "#/definitions/User"}
            }
        }
        
        related = self.generator._find_related_schemas(schema_with_ref)
        self.assertIn("#/definitions/User", related)
    
    def test_generate_api_doc(self):
        """Test API document generation"""
        api_spec = {
            "title": "Get User API",
            "endpoint": "/api/users/{id}",
            "method": "GET",
            "description": "Get user by ID",
            "parameters": [
                {
                    "name": "id",
                    "in": "path",
                    "required": True,
                    "schema": {"type": "string"},
                    "description": "User ID"
                }
            ],
            "requestSchema": {},
            "responseSchema": self.test_schema,
            "baseUrl": "https://api.example.com",
            "examples": {
                "response": {"id": "1", "name": "Alice"}
            }
        }
        
        doc = self.generator.generate_api_doc(api_spec)
        
        self.assertIn("GET /api/users/{id}", doc)
        self.assertIn("请求参数", doc)
        self.assertIn("响应", doc)
    
    def test_generate_params_table(self):
        """Test parameters table generation"""
        params = [
            {
                "name": "id",
                "in": "path",
                "required": True,
                "schema": {"type": "string"},
                "description": "User ID"
            },
            {
                "name": "include",
                "in": "query",
                "required": False,
                "schema": {"type": "string"},
                "description": "Include additional data"
            }
        ]
        
        table = self.generator._generate_params_table(params)
        
        self.assertIn("| 参数名 |", table)
        self.assertIn("| id |", table)
        self.assertIn("| include |", table)
        self.assertIn("✓", table)  # Required marker
    
    def test_generate_curl_example(self):
        """Test cURL example generation"""
        api_spec = {
            "method": "POST",
            "endpoint": "/api/users",
            "baseUrl": "https://api.example.com",
            "examples": {
                "request": {"name": "Alice", "email": "alice@example.com"}
            }
        }
        
        curl = self.generator._generate_curl_example(api_spec)
        
        self.assertIn("curl -X POST", curl)
        self.assertIn("https://api.example.com/api/users", curl)
        self.assertIn("Content-Type: application/json", curl)
    
    def test_generate_changelog(self):
        """Test changelog generation"""
        versions = [
            {
                "version": "2.0.0",
                "date": "2025-01-15",
                "changes": [
                    {"type": "added", "description": "New feature"},
                    {"type": "fixed", "description": "Bug fix"}
                ]
            },
            {
                "version": "1.0.0",
                "date": "2024-12-01",
                "changes": [
                    {"type": "added", "description": "Initial release"}
                ]
            }
        ]
        
        changelog = self.generator.generate_changelog(versions)
        
        self.assertIn("## 版本历史", changelog)
        self.assertIn("2.0.0", changelog)
        self.assertIn("1.0.0", changelog)
        self.assertIn("Initial release", changelog)
    
    def test_export_to_html(self):
        """Test HTML export"""
        markdown = "# Title\n\nContent here"
        html = self.generator.export_to_html(markdown, "Test Doc")
        
        self.assertIn("<!DOCTYPE html>", html)
        self.assertIn("<title>Test Doc</title>", html)
        self.assertIn("<style>", html)


class TestDocSection(unittest.TestCase):
    """Test DocSection dataclass"""
    
    def test_section_creation(self):
        """Test creating a document section"""
        section = DocSection(
            title="Overview",
            content="This is the overview",
            level=1
        )
        
        self.assertEqual(section.title, "Overview")
        self.assertEqual(section.level, 1)
        self.assertEqual(len(section.subsections), 0)


class TestAPIDoc(unittest.TestCase):
    """Test APIDoc dataclass"""
    
    def test_api_doc_creation(self):
        """Test creating API documentation"""
        doc = APIDoc(
            endpoint="/api/users",
            method="GET",
            summary="Get users",
            description="Retrieve a list of users",
            parameters=[],
            request_schema=None,
            response_schema={"type": "array"},
            examples={}
        )
        
        self.assertEqual(doc.endpoint, "/api/users")
        self.assertEqual(doc.method, "GET")


if __name__ == "__main__":
    unittest.main()
