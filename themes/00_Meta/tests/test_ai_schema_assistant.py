#!/usr/bin/env python3
"""
Tests for AI Schema Assistant
=============================

Test coverage for AI-assisted schema design functionality.

Version: 2.3.0
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "Tools"))

from ai_schema_assistant import AISchemaAssistant, AISuggestion


class TestAISchemaAssistant(unittest.TestCase):
    """Test AI Schema Assistant"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.assistant = AISchemaAssistant()
    
    def test_initialization(self):
        """Test assistant initialization"""
        self.assertIsNotNone(self.assistant.pattern_library)
        self.assertIsNotNone(self.assistant.best_practices)
        self.assertIn("user", self.assistant.pattern_library)
        self.assertIn("product", self.assistant.pattern_library)
    
    def test_generate_from_description_user(self):
        """Test generating schema from user description"""
        description = "用户资料，包含姓名、邮箱和年龄"
        suggestion = self.assistant.generate_from_description(description)
        
        self.assertIsInstance(suggestion, AISuggestion)
        self.assertEqual(suggestion.type, "generation")
        self.assertGreater(suggestion.confidence, 0)
        self.assertIsNotNone(suggestion.suggested_code)
        self.assertIn("properties", suggestion.suggested_code)
    
    def test_generate_from_description_product(self):
        """Test generating schema from product description"""
        description = "产品信息，包含名称和价格"
        suggestion = self.assistant.generate_from_description(description)
        
        self.assertIsInstance(suggestion, AISuggestion)
        self.assertIn("properties", suggestion.suggested_code)
    
    def test_suggest_optimizations(self):
        """Test schema optimization suggestions"""
        schema = {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "age": {"type": "integer"}
            }
        }
        
        suggestions = self.assistant.suggest_optimizations(schema)
        self.assertIsInstance(suggestions, list)
        # Should suggest adding constraints, descriptions, etc.
        self.assertTrue(len(suggestions) > 0)
    
    def test_diagnose_errors_circular_ref(self):
        """Test diagnosing circular reference errors"""
        errors = ["Circular reference detected at path $.user.friends"]
        suggestions = self.assistant.diagnose_errors({}, errors)
        
        self.assertTrue(len(suggestions) > 0)
        self.assertEqual(suggestions[0].type, "fix")
    
    def test_diagnose_errors_invalid_type(self):
        """Test diagnosing invalid type errors"""
        errors = ["Invalid type: 'interger' (should be 'integer')"]
        suggestions = self.assistant.diagnose_errors({}, errors)
        
        self.assertTrue(len(suggestions) > 0)
    
    def test_smart_completion_type(self):
        """Test smart completion for missing type"""
        schema = {"properties": {}}
        suggestion = self.assistant.smart_completion(schema, "properties")
        
        self.assertEqual(suggestion.type, "completion")
    
    def test_chat_generation(self):
        """Test chat response for generation request"""
        response = self.assistant.chat("如何生成Schema")
        self.assertIn("生成", response)
        self.assertIn("描述", response)
    
    def test_chat_optimization(self):
        """Test chat response for optimization request"""
        response = self.assistant.chat("如何优化Schema")
        self.assertIn("优化", response)
    
    def test_chat_error(self):
        """Test chat response for error request"""
        response = self.assistant.chat("遇到错误")
        self.assertIn("错误", response)
    
    def test_extract_entities(self):
        """Test entity extraction"""
        description = "用户地址信息，包含街道和城市"
        entities = self.assistant._extract_entities(description)
        self.assertIn("user", [e.lower() for e in entities] or [])
        self.assertIn("address", [e.lower() for e in entities] or [])


class TestAISuggestion(unittest.TestCase):
    """Test AISuggestion dataclass"""
    
    def test_suggestion_creation(self):
        """Test creating an AI suggestion"""
        suggestion = AISuggestion(
            type="optimization",
            message="Add constraints",
            confidence=0.85,
            suggested_code={"type": "string"},
            explanation="Strings should have length constraints"
        )
        
        self.assertEqual(suggestion.type, "optimization")
        self.assertEqual(suggestion.confidence, 0.85)
        self.assertIsNotNone(suggestion.suggested_code)


if __name__ == "__main__":
    unittest.main()
