"""Tree-sitter based Solidity parser."""

import logging
from pathlib import Path
from typing import Optional, Union, List, Dict, Any, Tuple

import tree_sitter
import tree_sitter_solidity

from sol_query.models.source_location import SourceLocation

logger = logging.getLogger(__name__)


class ParseError(Exception):
    """Exception raised when parsing fails."""

    def __init__(self, message: str, source_file: Optional[Path] = None,
                 line: Optional[int] = None, column: Optional[int] = None) -> None:
        super().__init__(message)
        self.source_file = source_file
        self.line = line
        self.column = column


class SolidityParser:
    """Tree-sitter based Solidity parser with robust error handling."""

    def __init__(self) -> None:
        """Initialize the parser with Solidity language support."""
        self._language = tree_sitter.Language(tree_sitter_solidity.language())
        self._parser = tree_sitter.Parser(self._language)

        # Cache for parsed trees
        self._tree_cache: Dict[str, tree_sitter.Tree] = {}

    def parse_text(self, source_code: str, file_path: Optional[Path] = None) -> tree_sitter.Tree:
        """
        Parse Solidity source code text.
        
        Args:
            source_code: The Solidity source code as a string
            file_path: Optional path to the source file for error reporting
            
        Returns:
            The parsed tree-sitter tree
            
        Raises:
            ParseError: If parsing fails or tree is invalid
        """
        try:
            # Convert string to bytes as required by tree-sitter
            source_bytes = source_code.encode('utf-8')

            # Parse the source code
            tree = self._parser.parse(source_bytes)

            if tree is None:
                raise ParseError("Failed to parse source code", file_path)

            # Check for parsing errors
            if tree.root_node.has_error:
                error_nodes = self._find_error_nodes(tree.root_node)
                if error_nodes:
                    first_error = error_nodes[0]
                    line, column = self._get_node_position(first_error, source_code)
                    raise ParseError(
                        f"Syntax error at line {line}, column {column}",
                        file_path, line, column
                    )
                else:
                    raise ParseError("Parsing completed with errors", file_path)

            return tree

        except Exception as e:
            if isinstance(e, ParseError):
                raise
            raise ParseError(f"Unexpected parsing error: {e}", file_path) from e

    def parse_file(self, file_path: Path) -> tree_sitter.Tree:
        """
        Parse a Solidity file.
        
        Args:
            file_path: Path to the Solidity file
            
        Returns:
            The parsed tree-sitter tree
            
        Raises:
            ParseError: If file cannot be read or parsed
            FileNotFoundError: If file does not exist
        """
        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {file_path}")

        if not file_path.is_file():
            raise ParseError(f"Path is not a file: {file_path}")

        # Check cache first
        cache_key = str(file_path.resolve())
        if cache_key in self._tree_cache:
            return self._tree_cache[cache_key]

        try:
            # Read file content
            with open(file_path, 'r', encoding='utf-8') as f:
                source_code = f.read()

            # Parse the content
            tree = self.parse_text(source_code, file_path)

            # Cache the result
            self._tree_cache[cache_key] = tree

            return tree

        except (UnicodeDecodeError, IOError) as e:
            raise ParseError(f"Failed to read file: {e}", file_path) from e

    def parse_directory(self, directory_path: Path,
                       pattern: str = "*.sol",
                       recursive: bool = True) -> Dict[Path, tree_sitter.Tree]:
        """
        Parse all Solidity files in a directory.
        
        Args:
            directory_path: Path to the directory
            pattern: File pattern to match (default: "*.sol")
            recursive: Whether to search recursively
            
        Returns:
            Dictionary mapping file paths to parsed trees
            
        Raises:
            ParseError: If directory cannot be accessed
        """
        if not directory_path.exists():
            raise ParseError(f"Directory not found: {directory_path}")

        if not directory_path.is_dir():
            raise ParseError(f"Path is not a directory: {directory_path}")

        results = {}
        errors = []

        # Find all matching files
        if recursive:
            files = directory_path.rglob(pattern)
        else:
            files = directory_path.glob(pattern)

        for file_path in files:
            try:
                tree = self.parse_file(file_path)
                results[file_path] = tree
            except (ParseError, FileNotFoundError) as e:
                errors.append((file_path, e))
                logger.warning(f"Failed to parse {file_path}: {e}")

        if errors and not results:
            # If no files parsed successfully, raise an error
            raise ParseError(f"Failed to parse any files in {directory_path}")

        return results

    def clear_cache(self) -> None:
        """Clear the internal tree cache."""
        self._tree_cache.clear()

    def get_source_location(self, node: tree_sitter.Node,
                           source_code: str, file_path: Optional[Path] = None) -> SourceLocation:
        """
        Get source location information for a tree-sitter node.
        
        Args:
            node: The tree-sitter node
            source_code: The original source code
            file_path: Optional path to the source file
            
        Returns:
            SourceLocation with detailed position information
        """
        start_line, start_column = self._get_node_position(node, source_code)
        end_line, end_column = self._get_node_end_position(node, source_code)

        # Extract the source text for this node
        source_text = source_code[node.start_byte:node.end_byte]

        return SourceLocation(
            file_path=file_path,
            start_line=start_line,
            start_column=start_column,
            end_line=end_line,
            end_column=end_column,
            start_byte=node.start_byte,
            end_byte=node.end_byte,
            source_text=source_text
        )

    def _find_error_nodes(self, node: tree_sitter.Node) -> List[tree_sitter.Node]:
        """Find all error nodes in the tree."""
        errors = []

        if node.type == 'ERROR':
            errors.append(node)

        for child in node.children:
            errors.extend(self._find_error_nodes(child))

        return errors

    def _get_node_position(self, node: tree_sitter.Node, source_code: str) -> Tuple[int, int]:
        """Get line and column position of node start (1-indexed)."""
        lines = source_code[:node.start_byte].split('\n')
        line = len(lines)
        column = len(lines[-1]) + 1
        return line, column

    def _get_node_end_position(self, node: tree_sitter.Node, source_code: str) -> Tuple[int, int]:
        """Get line and column position of node end (1-indexed)."""
        lines = source_code[:node.end_byte].split('\n')
        line = len(lines)
        column = len(lines[-1]) + 1
        return line, column