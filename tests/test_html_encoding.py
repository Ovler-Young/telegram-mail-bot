"""
Tests for HTML encoding detection and insertion functionality.
"""

import unittest
import sys
import os

# Add the parent directory to the path so we can import utils
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.html_encoding import has_encoding_hint, add_encoding_hint, ensure_html_encoding


class TestHtmlEncodingDetection(unittest.TestCase):
    """Test cases for HTML encoding detection."""
    
    def test_has_encoding_hint_html5_format(self):
        """Test detection of HTML5 meta charset tag."""
        # Standard HTML5 format
        html = '<html><head><meta charset="utf-8"></head><body>content</body></html>'
        self.assertTrue(has_encoding_hint(html))
        
        # With quotes
        html = '<html><head><meta charset="UTF-8"></head><body>content</body></html>'
        self.assertTrue(has_encoding_hint(html))
        
        # Self-closing
        html = '<html><head><meta charset="utf-8" /></head><body>content</body></html>'
        self.assertTrue(has_encoding_hint(html))
        
        # Case insensitive
        html = '<HTML><HEAD><META CHARSET="UTF-8"></HEAD><BODY>content</BODY></HTML>'
        self.assertTrue(has_encoding_hint(html))
        
        # With additional attributes
        html = '<head><meta name="viewport" content="width=device-width"><meta charset="utf-8"><title>Test</title></head>'
        self.assertTrue(has_encoding_hint(html))
    
    def test_has_encoding_hint_html4_format(self):
        """Test detection of HTML4 meta http-equiv tag."""
        # Standard HTML4 format
        html = '<html><head><meta http-equiv="Content-Type" content="text/html; charset=utf-8"></head></html>'
        self.assertTrue(has_encoding_hint(html))
        
        # Case insensitive
        html = '<HTML><HEAD><META HTTP-EQUIV="content-type" CONTENT="text/html; charset=UTF-8"></HEAD></HTML>'
        self.assertTrue(has_encoding_hint(html))
        
        # Different order
        html = '<head><meta content="text/html; charset=utf-8" http-equiv="Content-Type"></head>'
        self.assertTrue(has_encoding_hint(html))
    
    def test_has_encoding_hint_xml_declaration(self):
        """Test detection of XML declaration with encoding."""
        html = '<?xml version="1.0" encoding="utf-8"?><html><head></head></html>'
        self.assertTrue(has_encoding_hint(html))
        
        # Case insensitive
        html = '<?XML VERSION="1.0" ENCODING="UTF-8"?><html><head></head></html>'
        self.assertTrue(has_encoding_hint(html))
    
    def test_has_encoding_hint_no_encoding(self):
        """Test detection when no encoding hint is present."""
        # No meta tags
        html = '<html><head><title>Test</title></head><body>content</body></html>'
        self.assertFalse(has_encoding_hint(html))
        
        # Meta tags but no charset
        html = '<html><head><meta name="viewport" content="width=device-width"><title>Test</title></head></html>'
        self.assertFalse(has_encoding_hint(html))
        
        # Different charset
        html = '<html><head><meta charset="iso-8859-1"></head></html>'
        self.assertFalse(has_encoding_hint(html))
    
    def test_has_encoding_hint_edge_cases(self):
        """Test edge cases for encoding detection."""
        # Empty string
        self.assertFalse(has_encoding_hint(''))
        
        # None input
        self.assertFalse(has_encoding_hint(None))
        
        # Non-string input
        self.assertFalse(has_encoding_hint(123))
        
        # Plain text
        self.assertFalse(has_encoding_hint('Just plain text without HTML'))


class TestHtmlEncodingInsertion(unittest.TestCase):
    """Test cases for HTML encoding insertion."""
    
    def test_add_encoding_hint_with_head_section(self):
        """Test adding encoding hint to HTML with existing head section."""
        html = '<html><head><title>Test</title></head><body>content</body></html>'
        result = add_encoding_hint(html)
        
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('<head>', result)
        self.assertIn('<title>Test</title>', result)
        # Should be inserted right after <head>
        self.assertTrue(result.find('<meta charset="utf-8">') < result.find('<title>Test</title>'))
    
    def test_add_encoding_hint_create_head_section(self):
        """Test adding encoding hint by creating head section."""
        html = '<html><body>content</body></html>'
        result = add_encoding_hint(html)
        
        self.assertIn('<head>', result)
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('</head>', result)
        self.assertIn('<body>content</body>', result)
    
    def test_add_encoding_hint_malformed_html(self):
        """Test adding encoding hint to malformed HTML."""
        # HTML-like content without proper structure
        html = '<div>Some content</div><p>More content</p>'
        result = add_encoding_hint(html)
        
        self.assertIn('<head>', result)
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('</head>', result)
        self.assertIn('<div>Some content</div>', result)
    
    def test_add_encoding_hint_already_has_encoding(self):
        """Test that content with existing encoding is not modified."""
        html = '<html><head><meta charset="utf-8"><title>Test</title></head><body>content</body></html>'
        result = add_encoding_hint(html)
        
        # Should be unchanged
        self.assertEqual(html, result)
    
    def test_add_encoding_hint_case_insensitive_head(self):
        """Test adding encoding hint with case-insensitive head tags."""
        html = '<HTML><HEAD><TITLE>Test</TITLE></HEAD><BODY>content</BODY></HTML>'
        result = add_encoding_hint(html)
        
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('<HEAD>', result)
    
    def test_add_encoding_hint_head_with_attributes(self):
        """Test adding encoding hint to head tag with attributes."""
        html = '<html><head lang="en"><title>Test</title></head><body>content</body></html>'
        result = add_encoding_hint(html)
        
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('<head lang="en">', result)
    
    def test_add_encoding_hint_non_html_content(self):
        """Test that non-HTML content is not modified."""
        text = 'Just plain text without any HTML tags'
        result = add_encoding_hint(text)
        
        # Should be unchanged
        self.assertEqual(text, result)
    
    def test_add_encoding_hint_edge_cases(self):
        """Test edge cases for encoding insertion."""
        # Empty string
        self.assertEqual('', add_encoding_hint(''))
        
        # None input
        self.assertIsNone(add_encoding_hint(None))
        
        # Non-string input
        self.assertEqual(123, add_encoding_hint(123))


class TestEnsureHtmlEncoding(unittest.TestCase):
    """Test cases for the main ensure_html_encoding function."""
    
    def test_ensure_html_encoding_none_input(self):
        """Test handling of None input."""
        result = ensure_html_encoding(None)
        self.assertIsNone(result)
    
    def test_ensure_html_encoding_valid_html(self):
        """Test processing of valid HTML."""
        html = '<html><head><title>Test</title></head><body>content</body></html>'
        result = ensure_html_encoding(html)
        
        self.assertIsNotNone(result)
        self.assertIn('<meta charset="utf-8">', result)
    
    def test_ensure_html_encoding_already_encoded(self):
        """Test that already encoded HTML is not modified."""
        html = '<html><head><meta charset="utf-8"><title>Test</title></head><body>content</body></html>'
        result = ensure_html_encoding(html)
        
        self.assertEqual(html, result)
    
    def test_ensure_html_encoding_non_string(self):
        """Test handling of non-string input."""
        result = ensure_html_encoding(123)
        self.assertEqual(123, result)


class TestIntegrationScenarios(unittest.TestCase):
    """Integration test scenarios for real-world HTML content."""
    
    def test_complete_html_document(self):
        """Test with a complete HTML document."""
        html = '''<!DOCTYPE html>
<html lang="en">
<head>
    <title>Test Email</title>
    <style>body { font-family: Arial; }</style>
</head>
<body>
    <h1>Welcome</h1>
    <p>This is an email with HTML content.</p>
</body>
</html>'''
        
        result = ensure_html_encoding(html)
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('<title>Test Email</title>', result)
        # Meta tag should come before title
        self.assertTrue(result.find('<meta charset="utf-8">') < result.find('<title>Test Email</title>'))
    
    def test_email_html_fragment(self):
        """Test with HTML fragment typical in emails."""
        html = '''<div style="font-family: Arial, sans-serif;">
    <h2>Newsletter Update</h2>
    <p>Hello subscriber!</p>
    <p>Here's your weekly update with special characters: café, naïve, résumé</p>
    <a href="https://example.com">Visit our website</a>
</div>'''
        
        result = ensure_html_encoding(html)
        self.assertIn('<head>', result)
        self.assertIn('<meta charset="utf-8">', result)
        self.assertIn('café, naïve, résumé', result)
    
    def test_html_with_existing_html5_encoding(self):
        """Test HTML that already has HTML5 encoding."""
        html = '''<!DOCTYPE html>
<html>
<head>
    <meta charset="utf-8">
    <title>Already Encoded</title>
</head>
<body>
    <p>This content already has UTF-8 encoding specified.</p>
</body>
</html>'''
        
        result = ensure_html_encoding(html)
        # Should be unchanged
        self.assertEqual(html, result)
    
    def test_html_with_existing_html4_encoding(self):
        """Test HTML that already has HTML4 encoding."""
        html = '''<!DOCTYPE html PUBLIC "-//W3C//DTD HTML 4.01//EN">
<html>
<head>
    <meta http-equiv="Content-Type" content="text/html; charset=utf-8">
    <title>HTML4 Style</title>
</head>
<body>
    <p>This uses HTML4 style encoding declaration.</p>
</body>
</html>'''
        
        result = ensure_html_encoding(html)
        # Should be unchanged
        self.assertEqual(html, result)


if __name__ == '__main__':
    unittest.main()