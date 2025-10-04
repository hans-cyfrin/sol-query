"""Source management system for handling multiple files and dependencies."""

import logging
from pathlib import Path
from typing import Dict, List, Optional, Set, Union, Tuple
from dataclasses import dataclass, field
from datetime import datetime

import tree_sitter

from sol_query.core.parser import SolidityParser, ParseError
from sol_query.core.ast_builder import ASTBuilder
from sol_query.core.ast_nodes import ASTNode, ContractDeclaration, ImportStatement

logger = logging.getLogger(__name__)


@dataclass
class SourceFile:
    """Represents a source file with metadata."""

    path: Path
    content: str
    last_modified: datetime
    tree: Optional[tree_sitter.Tree] = None
    ast: Optional[List[ASTNode]] = None
    contracts: List[ContractDeclaration] = field(default_factory=list)
    imports: List[ImportStatement] = field(default_factory=list)
    pragmas: List["PragmaDirective"] = field(default_factory=list)
    parse_errors: List[ParseError] = field(default_factory=list)

    def is_parsed(self) -> bool:
        """Check if file has been successfully parsed."""
        return self.tree is not None and len(self.parse_errors) == 0

    def has_contract(self, name: str) -> bool:
        """Check if file contains a contract with the given name."""
        return any(contract.name == name for contract in self.contracts)

    def get_contract(self, name: str) -> Optional[ContractDeclaration]:
        """Get a contract by name."""
        for contract in self.contracts:
            if contract.name == name:
                return contract
        return None


class SourceManager:
    """Manages source files, dependencies, and incremental parsing."""

    def __init__(self, parser: Optional[SolidityParser] = None):
        """
        Initialize the source manager.
        
        Args:
            parser: Optional SolidityParser instance. If None, creates a new one.
        """
        self.parser = parser or SolidityParser()

        # File management
        self.files: Dict[Path, SourceFile] = {}
        self.file_patterns = ["*.sol"]

        # Dependency tracking
        self.dependency_graph: Dict[Path, Set[Path]] = {}
        self.reverse_dependencies: Dict[Path, Set[Path]] = {}

        # Performance optimization
        self._needs_contextual_analysis = False

        # Caching
        self.enable_cache = True

    def add_file(self, file_path: Union[str, Path]) -> SourceFile:
        """
        Add a single file to the source manager.
        
        Args:
            file_path: Path to the Solidity file
            
        Returns:
            The SourceFile instance
            
        Raises:
            FileNotFoundError: If file does not exist
            ParseError: If file cannot be read
        """
        path = Path(file_path).resolve()

        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not path.is_file():
            raise ParseError(f"Path is not a file: {path}")

        # Check if already loaded and up-to-date
        if path in self.files and self.enable_cache:
            existing = self.files[path]
            current_mtime = datetime.fromtimestamp(path.stat().st_mtime)
            if existing.last_modified >= current_mtime:
                return existing

        # Read file content
        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
        except (UnicodeDecodeError, IOError) as e:
            raise ParseError(f"Failed to read file {path}: {e}") from e

        # Create source file
        source_file = SourceFile(
            path=path,
            content=content,
            last_modified=datetime.fromtimestamp(path.stat().st_mtime)
        )

        # Parse the file
        self._parse_file(source_file)

        # Store in cache
        self.files[path] = source_file

        # Mark that we need to run contextual analysis
        # (will be done in batch after all files are loaded for performance)
        self._needs_contextual_analysis = True

        return source_file

    def add_directory(self,
                     directory_path: Union[str, Path],
                     recursive: bool = True,
                     patterns: Optional[List[str]] = None) -> List[SourceFile]:
        """
        Add all Solidity files from a directory.
        
        Args:
            directory_path: Path to the directory
            recursive: Whether to search recursively
            patterns: File patterns to match (default: ["*.sol"])
            
        Returns:
            List of successfully loaded SourceFile instances
            
        Raises:
            ParseError: If directory cannot be accessed
        """
        path = Path(directory_path)

        if not path.exists():
            raise ParseError(f"Directory not found: {path}")

        if not path.is_dir():
            raise ParseError(f"Path is not a directory: {path}")

        patterns = patterns or self.file_patterns
        source_files = []

        for pattern in patterns:
            if recursive:
                files = path.rglob(pattern)
            else:
                files = path.glob(pattern)

            for file_path in files:
                try:
                    source_file = self.add_file(file_path)
                    source_files.append(source_file)
                except (ParseError, FileNotFoundError) as e:
                    logger.warning(f"Failed to add file {file_path}: {e}")

        if not source_files:
            logger.warning(f"No Solidity files found in {path}")

        # Perform contextual analysis after loading all files
        self._perform_contextual_analysis()

        return source_files

    def get_file(self, file_path: Union[str, Path]) -> Optional[SourceFile]:
        """
        Get a source file by path.
        
        Args:
            file_path: Path to the file
            
        Returns:
            The SourceFile instance, or None if not found
        """
        path = Path(file_path).resolve()
        return self.files.get(path)

    def get_all_files(self) -> List[SourceFile]:
        """Get all loaded source files."""
        return list(self.files.values())

    def ensure_contextual_analysis(self) -> None:
        """Ensure contextual analysis has been performed if needed."""
        if self._needs_contextual_analysis:
            self._perform_contextual_analysis()
            self._needs_contextual_analysis = False

    def get_contracts(self, file_path: Optional[Union[str, Path]] = None) -> List[ContractDeclaration]:
        """
        Get contracts from a specific file or all files.

        Args:
            file_path: Optional path to specific file. If None, returns all contracts.

        Returns:
            List of contract declarations
        """
        # Ensure contextual analysis is done before returning contracts
        self.ensure_contextual_analysis()

        if file_path:
            source_file = self.get_file(file_path)
            return source_file.contracts if source_file else []

        contracts = []
        for source_file in self.files.values():
            contracts.extend(source_file.contracts)
        return contracts

    def find_contract(self, name: str) -> Optional[Tuple[ContractDeclaration, SourceFile]]:
        """
        Find a contract by name across all files.
        
        Args:
            name: Contract name to search for
            
        Returns:
            Tuple of (contract, source_file) if found, None otherwise
        """
        for source_file in self.files.values():
            for contract in source_file.contracts:
                if contract.name == name:
                    return contract, source_file
        return None

    def get_dependencies(self, file_path: Union[str, Path]) -> Set[Path]:
        """
        Get dependencies for a specific file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Set of file paths that this file depends on
        """
        path = Path(file_path).resolve()
        return self.dependency_graph.get(path, set())

    def get_dependents(self, file_path: Union[str, Path]) -> Set[Path]:
        """
        Get files that depend on the specified file.
        
        Args:
            file_path: Path to the file
            
        Returns:
            Set of file paths that depend on this file
        """
        path = Path(file_path).resolve()
        return self.reverse_dependencies.get(path, set())

    def refresh_file(self, file_path: Union[str, Path]) -> Optional[SourceFile]:
        """
        Refresh a specific file (reparse if changed).
        
        Args:
            file_path: Path to the file to refresh
            
        Returns:
            The refreshed SourceFile, or None if file not found
        """
        path = Path(file_path).resolve()

        if path not in self.files:
            return None

        # Remove from cache and re-add
        del self.files[path]

        try:
            return self.add_file(path)
        except (FileNotFoundError, ParseError):
            return None

    def clear_cache(self) -> None:
        """Clear all cached files and dependencies."""
        self.files.clear()
        self.dependency_graph.clear()
        self.reverse_dependencies.clear()
        self.parser.clear_cache()

    def get_parse_errors(self) -> List[Tuple[Path, ParseError]]:
        """
        Get all parse errors across all files.
        
        Returns:
            List of (file_path, error) tuples
        """
        errors = []
        for source_file in self.files.values():
            for error in source_file.parse_errors:
                errors.append((source_file.path, error))
        return errors

    def get_statistics(self) -> Dict[str, int]:
        """
        Get statistics about loaded files.
        
        Returns:
            Dictionary with statistics
        """
        total_files = len(self.files)
        parsed_files = sum(1 for f in self.files.values() if f.is_parsed())
        total_contracts = sum(len(f.contracts) for f in self.files.values())
        files_with_errors = sum(1 for f in self.files.values() if f.parse_errors)

        return {
            "total_files": total_files,
            "parsed_files": parsed_files,
            "files_with_errors": files_with_errors,
            "total_contracts": total_contracts,
            "success_rate": parsed_files / total_files if total_files > 0 else 0
        }

    def _parse_file(self, source_file: SourceFile) -> None:
        """Parse a source file and populate its AST."""
        try:
            # Parse with tree-sitter
            tree = self.parser.parse_text(source_file.content, source_file.path)
            source_file.tree = tree

            # Build AST
            ast_builder = ASTBuilder(self.parser, source_file.content, source_file.path)
            ast_nodes = ast_builder.build_ast(tree)
            source_file.ast = ast_nodes

            # Extract contracts
            source_file.contracts = [
                node for node in ast_nodes
                if isinstance(node, ContractDeclaration)
            ]

            # Extract imports
            source_file.imports = [
                node for node in ast_nodes
                if isinstance(node, ImportStatement)
            ]

            # Extract pragma directives
            source_file.pragmas = [
                node for node in ast_nodes
                if hasattr(node, 'node_type') and node.node_type.value == "pragma_directive"
            ]

            # Update dependency tracking
            self._update_dependencies(source_file)

        except ParseError as e:
            source_file.parse_errors.append(e)
            logger.warning(f"Parse error in {source_file.path}: {e}")
        except Exception as e:
            error = ParseError(f"Unexpected error: {e}", source_file.path)
            source_file.parse_errors.append(error)
            logger.error(f"Unexpected error parsing {source_file.path}: {e}")

    def _perform_contextual_analysis(self) -> None:
        """
        Perform contextual analysis on all loaded contracts.
        This improves the accuracy of external call detection.
        """
        # Get all contracts from all files (without triggering contextual analysis again)
        all_contracts = []
        for source_file in self.files.values():
            all_contracts.extend(source_file.contracts)

        if not all_contracts:
            return

        # For each file, perform contextual analysis
        for source_file in self.files.values():
            if source_file.ast:
                # Create AST builder for performing contextual analysis
                ast_builder = ASTBuilder(self.parser, source_file.content, source_file.path)

                # Perform contextual analysis on the actual AST contracts
                ast_builder.perform_contextual_analysis(all_contracts)

    def _update_dependencies(self, source_file: SourceFile) -> None:
        """Update dependency tracking for a source file."""
        path = source_file.path
        dependencies = set()

        # Resolve import paths to actual files
        for import_stmt in source_file.imports:
            import_path = import_stmt.import_path if hasattr(import_stmt, 'import_path') else str(import_stmt)
            resolved_path = self._resolve_import(import_path, path)
            if resolved_path and resolved_path in self.files:
                dependencies.add(resolved_path)

        # Update dependency graph
        self.dependency_graph[path] = dependencies

        # Update reverse dependencies
        for dep_path in dependencies:
            if dep_path not in self.reverse_dependencies:
                self.reverse_dependencies[dep_path] = set()
            self.reverse_dependencies[dep_path].add(path)

    def _resolve_import(self, import_path: str, current_file: Path) -> Optional[Path]:
        """
        Resolve an import path to an actual file path.
        
        Args:
            import_path: The import path from the source
            current_file: The current file doing the import
            
        Returns:
            Resolved path if found, None otherwise
        """
        # Handle relative imports
        if import_path.startswith('./') or import_path.startswith('../'):
            base_path = current_file.parent
            resolved = (base_path / import_path).resolve()
            if resolved.exists():
                return resolved

        # Handle absolute imports (would need more sophisticated resolution)
        # For now, just look in the same directory
        base_path = current_file.parent
        resolved = (base_path / import_path).resolve()
        if resolved.exists():
            return resolved

        # Add .sol extension if not present
        if not import_path.endswith('.sol'):
            resolved = (base_path / f"{import_path}.sol").resolve()
            if resolved.exists():
                return resolved

        return None