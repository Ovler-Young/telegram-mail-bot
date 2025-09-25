"""
HTML encoding detection and insertion utilities.

This module provides functionality to detect if HTML content already has encoding information
and insert UTF-8 encoding hints when missing.
"""

import re
from typing import Optional


def has_encoding_hint(html_content: str) -> bool:
    """
    Check if HTML content already has encoding information.

    Detects the following encoding patterns (case-insensitive):
    - <meta charset="utf-8"> (HTML5 format)
    - <meta http-equiv="Content-Type" content="text/html; charset=utf-8"> (HTML4 format)
    - XML declaration with encoding attribute

    Args:
        html_content: The HTML content to check

    Returns:
        True if encoding hint is found, False otherwise
    """
    if not html_content or not isinstance(html_content, str):
        return False

    # Convert to lowercase for case-insensitive matching
    content_lower = html_content.lower()

    # Check for HTML5 meta charset tag
    html5_pattern = r'<meta\s+charset\s*=\s*["\']?utf-?8["\']?\s*/?>'
    if re.search(html5_pattern, content_lower):
        return True

    # Check for HTML4 meta http-equiv tag with charset
    # Use separate patterns to avoid character class issues
    if ('http-equiv' in content_lower and 'content-type' in content_lower and
            'charset' in content_lower):
        # Try both attribute orders: http-equiv first, then content first
        html4_pattern1 = (r'<meta[^>]*http-equiv[^>]*content-type[^>]*'
                          r'charset[^>]*utf-?8[^>]*/?>')
        html4_pattern2 = (r'<meta[^>]*content[^>]*charset[^>]*utf-?8[^>]*'
                          r'http-equiv[^>]*content-type[^>]*/?>')
        if (re.search(html4_pattern1, content_lower) or
                re.search(html4_pattern2, content_lower)):
            return True

    # Check for XML declaration with encoding
    xml_pattern = r'<\?xml[^>]*encoding\s*=\s*["\']utf-?8["\'][^>]*\?>'
    if re.search(xml_pattern, content_lower):
        return True

    return False


def add_encoding_hint(html_content: str) -> str:
    """
    Add UTF-8 encoding hint to HTML content if not already present.

    The function will:
    1. Check if encoding hint already exists (if so, return unchanged)
    2. Look for <head> section and insert <meta charset="utf-8"> early in it
    3. If no <head> section exists, create one with the meta tag
    4. Handle edge cases like malformed HTML

    Args:
        html_content: The HTML content to process

    Returns:
        HTML content with UTF-8 encoding hint added if it was missing
    """
    if not html_content or not isinstance(html_content, str):
        return html_content

    # Check if encoding hint already exists
    if has_encoding_hint(html_content):
        return html_content

    # Define the UTF-8 meta tag to insert
    utf8_meta_tag = '<meta charset="utf-8">'

    # Case 1: Look for existing <head> tag (case-insensitive)
    head_pattern = r'(<head[^>]*>)'
    head_match = re.search(head_pattern, html_content, re.IGNORECASE)

    if head_match:
        # Insert meta charset right after the opening <head> tag
        insertion_point = head_match.end()

        # Insert with proper whitespace
        new_content = (
            html_content[:insertion_point] +
            '\n    ' + utf8_meta_tag +
            html_content[insertion_point:]
        )
        return new_content

    # Case 2: Look for <html> tag and create <head> section
    html_pattern = r'(<html[^>]*>)'
    html_match = re.search(html_pattern, html_content, re.IGNORECASE)

    if html_match:
        # Insert head section right after opening <html> tag
        insertion_point = html_match.end()
        head_section = f'\n<head>\n    {utf8_meta_tag}\n</head>'

        new_content = (
            html_content[:insertion_point] +
            head_section +
            html_content[insertion_point:]
        )
        return new_content

    # Case 3: No proper HTML structure, check if it looks like HTML content
    if re.search(r'<[^>]+>', html_content):
        # Looks like HTML but malformed - prepend a basic head section
        head_section = f'<head>\n    {utf8_meta_tag}\n</head>\n'
        return head_section + html_content

    # Case 4: Doesn't look like HTML content, return unchanged
    return html_content


def ensure_html_encoding(html_content: Optional[str]) -> Optional[str]:
    """
    Convenience function to ensure HTML content has UTF-8 encoding hint.

    This is the main function that should be used by the Email class.
    It handles None values gracefully and only modifies HTML when necessary.

    Args:
        html_content: The HTML content to process (can be None)

    Returns:
        HTML content with UTF-8 encoding hint, or None if input was None
    """
    if html_content is None:
        return None

    if not isinstance(html_content, str):
        return html_content

    return add_encoding_hint(html_content)
