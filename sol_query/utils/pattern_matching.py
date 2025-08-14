"""Pattern matching utilities for flexible querying."""

import re
import fnmatch
from typing import Union, List, Pattern, Any


class PatternMatcher:
    """Utility class for various types of pattern matching."""
    
    def __init__(self):
        """Initialize pattern matcher."""
        # Cache compiled regex patterns for performance
        self._regex_cache = {}
    
    def matches_name_pattern(self, name: str, pattern: Union[str, List[str], Pattern]) -> bool:
        """
        Check if a name matches a pattern.
        
        Supports:
        - Exact string matching
        - Unix shell-style wildcards (*, ?)
        - Regular expressions (Pattern objects)
        - Lists of any of the above (OR logic)
        
        Args:
            name: The name to test
            pattern: Pattern to match against
            
        Returns:
            True if name matches the pattern
        """
        if pattern is None:
            return True
        
        # Handle lists of patterns (OR logic)
        if isinstance(pattern, list):
            return any(self.matches_name_pattern(name, p) for p in pattern)
        
        # Handle regex Pattern objects
        if hasattr(pattern, 'search'):
            return bool(pattern.search(name))
        
        # Handle string patterns
        if isinstance(pattern, str):
            # Check for exact match first
            if pattern == name:
                return True
            
            # Check for shell-style wildcards
            if '*' in pattern or '?' in pattern or '[' in pattern:
                return fnmatch.fnmatch(name, pattern)
            
            # Check if it looks like a regex (contains regex metacharacters)
            if self._looks_like_regex(pattern):
                try:
                    regex = self._get_compiled_regex(pattern)
                    return bool(regex.search(name))
                except re.error:
                    # If regex compilation fails, fall back to exact match
                    return pattern == name
            
            # For non-wildcard patterns, only do exact match (not substring)
            return False
        
        return False
    
    def matches_text_pattern(self, text: str, pattern: Union[str, Pattern]) -> bool:
        """
        Check if text matches a pattern (for source code searching).
        
        Args:
            text: The text to search in
            pattern: Pattern to match (string or compiled regex)
            
        Returns:
            True if text contains matches for the pattern
        """
        if pattern is None:
            return True
        
        # Handle regex Pattern objects
        if hasattr(pattern, 'search'):
            return bool(pattern.search(text))
        
        # Handle string patterns as regex
        if isinstance(pattern, str):
            try:
                regex = self._get_compiled_regex(pattern)
                return bool(regex.search(text))
            except re.error:
                # If regex fails, do substring search
                return pattern in text
        
        return False
    
    def matches_type_pattern(self, type_name: str, pattern: Union[str, List[str], Pattern]) -> bool:
        """
        Check if a type name matches a pattern.
        
        Special handling for Solidity types:
        - Handles array types (uint256[] matches uint256)
        - Handles mapping types
        - Supports inheritance checks (would need more context)
        
        Args:
            type_name: The type name to test
            pattern: Pattern to match against
            
        Returns:
            True if type matches the pattern
        """
        # First try exact matching
        if self.matches_name_pattern(type_name, pattern):
            return True
        
        # Handle array types - check base type
        if type_name.endswith('[]'):
            base_type = type_name[:-2]
            if self.matches_name_pattern(base_type, pattern):
                return True
        
        # Handle multi-dimensional arrays
        array_match = re.match(r'(.+?)(\[\d*\])+$', type_name)
        if array_match:
            base_type = array_match.group(1)
            if self.matches_name_pattern(base_type, pattern):
                return True
        
        # Handle mapping types
        mapping_match = re.match(r'mapping\s*\(\s*(.+?)\s*=>\s*(.+?)\s*\)', type_name)
        if mapping_match:
            key_type = mapping_match.group(1).strip()
            value_type = mapping_match.group(2).strip()
            if (self.matches_name_pattern(key_type, pattern) or 
                self.matches_name_pattern(value_type, pattern)):
                return True
        
        return False
    
    def create_regex_pattern(self, pattern_str: str, 
                           case_sensitive: bool = True,
                           whole_word: bool = False,
                           multiline: bool = False) -> Pattern:
        """
        Create a compiled regex pattern with options.
        
        Args:
            pattern_str: The regex pattern string
            case_sensitive: Whether matching should be case sensitive
            whole_word: Whether to match whole words only
            multiline: Whether to enable multiline mode
            
        Returns:
            Compiled regex pattern
        """
        flags = 0
        
        if not case_sensitive:
            flags |= re.IGNORECASE
        
        if multiline:
            flags |= re.MULTILINE | re.DOTALL
        
        if whole_word:
            pattern_str = r'\b' + pattern_str + r'\b'
        
        return re.compile(pattern_str, flags)
    
    def create_wildcard_patterns(self, patterns: List[str]) -> List[str]:
        """
        Convert shell-style wildcards to regex patterns.
        
        Args:
            patterns: List of wildcard patterns
            
        Returns:
            List of equivalent regex patterns
        """
        regex_patterns = []
        for pattern in patterns:
            regex_pattern = fnmatch.translate(pattern)
            regex_patterns.append(regex_pattern)
        return regex_patterns
    
    def filter_by_multiple_patterns(self, items: List[str], 
                                   patterns: List[Union[str, Pattern]],
                                   match_all: bool = False) -> List[str]:
        """
        Filter items by multiple patterns.
        
        Args:
            items: List of items to filter
            patterns: List of patterns to match against
            match_all: If True, items must match ALL patterns (AND logic).
                      If False, items must match ANY pattern (OR logic).
            
        Returns:
            List of items that match the criteria
        """
        if not patterns:
            return items
        
        filtered_items = []
        
        for item in items:
            if match_all:
                # AND logic - item must match all patterns
                if all(self.matches_name_pattern(item, pattern) for pattern in patterns):
                    filtered_items.append(item)
            else:
                # OR logic - item must match at least one pattern
                if any(self.matches_name_pattern(item, pattern) for pattern in patterns):
                    filtered_items.append(item)
        
        return filtered_items
    
    def _looks_like_regex(self, pattern: str) -> bool:
        """Check if a string looks like it might be a regex pattern."""
        regex_chars = set(r'.*+?[]{}()|\^$')
        return any(char in pattern for char in regex_chars)
    
    def _get_compiled_regex(self, pattern: str) -> Pattern:
        """Get a compiled regex from cache or compile and cache it."""
        if pattern not in self._regex_cache:
            self._regex_cache[pattern] = re.compile(pattern)
        return self._regex_cache[pattern]


class FilterBuilder:
    """Builder for complex filter conditions."""
    
    def __init__(self):
        """Initialize filter builder."""
        self.conditions = []
    
    def name_matches(self, pattern: Union[str, List[str], Pattern]) -> "FilterBuilder":
        """Add name matching condition."""
        self.conditions.append(('name', 'matches', pattern))
        return self
    
    def name_not_matches(self, pattern: Union[str, List[str], Pattern]) -> "FilterBuilder":
        """Add name not matching condition."""
        self.conditions.append(('name', 'not_matches', pattern))
        return self
    
    def type_matches(self, pattern: Union[str, List[str], Pattern]) -> "FilterBuilder":
        """Add type matching condition."""
        self.conditions.append(('type', 'matches', pattern))
        return self
    
    def visibility_is(self, visibility: Any) -> "FilterBuilder":
        """Add visibility condition."""
        self.conditions.append(('visibility', 'equals', visibility))
        return self
    
    def has_modifier(self, modifier: str) -> "FilterBuilder":
        """Add modifier condition."""
        self.conditions.append(('modifiers', 'contains', modifier))
        return self
    
    def attribute_equals(self, attribute: str, value: Any) -> "FilterBuilder":
        """Add generic attribute equality condition."""
        self.conditions.append((attribute, 'equals', value))
        return self
    
    def attribute_in(self, attribute: str, values: List[Any]) -> "FilterBuilder":
        """Add generic attribute in list condition."""
        self.conditions.append((attribute, 'in', values))
        return self
    
    def custom_predicate(self, predicate: callable) -> "FilterBuilder":
        """Add custom predicate condition."""
        self.conditions.append(('custom', 'predicate', predicate))
        return self
    
    def build(self) -> callable:
        """Build a filter function from the conditions."""
        def filter_func(obj):
            matcher = PatternMatcher()
            
            for condition in self.conditions:
                attr, op, value = condition
                
                if attr == 'custom':
                    if not value(obj):
                        return False
                elif attr == 'name':
                    obj_value = getattr(obj, 'name', '')
                    if op == 'matches':
                        if not matcher.matches_name_pattern(obj_value, value):
                            return False
                    elif op == 'not_matches':
                        if matcher.matches_name_pattern(obj_value, value):
                            return False
                elif attr == 'type':
                    obj_value = getattr(obj, 'type_name', '') or getattr(obj, 'node_type', '')
                    if op == 'matches':
                        if not matcher.matches_type_pattern(str(obj_value), value):
                            return False
                elif hasattr(obj, attr):
                    obj_value = getattr(obj, attr)
                    
                    if op == 'equals':
                        if obj_value != value:
                            return False
                    elif op == 'in':
                        if obj_value not in value:
                            return False
                    elif op == 'contains':
                        if hasattr(obj_value, '__contains__'):
                            if value not in obj_value:
                                return False
                        else:
                            if obj_value != value:
                                return False
            
            return True
        
        return filter_func
    
    def clear(self) -> "FilterBuilder":
        """Clear all conditions."""
        self.conditions = []
        return self