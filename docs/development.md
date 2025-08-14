# Development Guide

Guide for contributing to Sol-Query development and extending its functionality.

## Development Setup

### Prerequisites

- Python 3.11+
- `uv` package manager (recommended)
- Git

### Environment Setup

```bash
# Clone the repository
git clone <repository-url>
cd sol-query

# Install development dependencies
uv sync --dev

# Install pre-commit hooks (if available)
pre-commit install

# Run tests to verify setup
uv run python -m pytest tests/ -v
```

### Development Tools

```bash
# Code formatting
uv run black sol_query/ tests/

# Type checking
uv run mypy sol_query/

# Linting
uv run ruff check sol_query/ tests/

# Test coverage
uv run python -m pytest tests/ --cov=sol_query --cov-report=html
```

## Project Structure

```
sol-query/
├── sol_query/                 # Main package
│   ├── core/                  # Core parsing and AST building
│   │   ├── parser.py          # Tree-sitter integration
│   │   ├── ast_builder.py     # AST construction
│   │   ├── ast_nodes.py       # AST node definitions
│   │   └── source_manager.py  # File management
│   ├── query/                 # Query engine and collections
│   │   ├── engine.py          # Main query engine
│   │   └── collections.py     # Fluent collection classes
│   ├── utils/                 # Utilities
│   │   ├── pattern_matching.py # Pattern matching logic
│   │   └── serialization.py   # JSON serialization
│   └── models/                # Data models
│       └── source_location.py # Source location tracking
├── tests/                     # Test suite
│   ├── fixtures/              # Test data
│   ├── test_basic_functionality.py
│   ├── test_comprehensive_queries.py
│   └── test_sol_bug_bench.py
├── docs/                      # Documentation
└── sol-bug-bench/            # Test contracts
```

## Testing Strategy

### Test Categories

1. **Unit Tests** (`test_basic_functionality.py`)
   - Core functionality testing
   - Individual method validation
   - Edge case handling

2. **Integration Tests** (`test_comprehensive_queries.py`)
   - End-to-end query workflows
   - Multiple component interaction
   - Complex query scenarios

3. **Real-world Tests** (`test_sol_bug_bench.py`)
   - Testing against actual Solidity projects
   - Performance validation
   - Compatibility verification

### Writing Tests

```python
import pytest
from pathlib import Path
from sol_query import SolidityQueryEngine

class TestNewFeature:
    """Test class for new functionality."""
    
    @pytest.fixture
    def engine(self):
        """Create engine with test fixtures."""
        engine = SolidityQueryEngine()
        engine.load_sources(Path("tests/fixtures"))
        return engine
    
    def test_new_query_method(self, engine):
        """Test new query functionality."""
        # Arrange
        expected_count = 5
        
        # Act
        results = engine.new_query_method(param="value")
        
        # Assert
        assert len(results) == expected_count
        assert all(hasattr(r, 'required_attribute') for r in results)
```

### Running Tests

```bash
# Run all tests
uv run python -m pytest tests/ -v

# Run specific test file
uv run python -m pytest tests/test_basic_functionality.py -v

# Run specific test method
uv run python -m pytest tests/test_basic_functionality.py::TestBasicFunctionality::test_find_contracts -v

# Run with coverage
uv run python -m pytest tests/ --cov=sol_query --cov-report=term-missing

# Run performance tests
uv run python -m pytest tests/test_sol_bug_bench.py::TestSolBugBenchQueries::test_performance_on_larger_codebase -v
```

## Adding New Features

### 1. Adding New AST Node Types

To add support for a new Solidity construct:

1. **Define the Node Class** in `ast_nodes.py`:

```python
@dataclass
class NewConstructDeclaration(ASTNode):
    """Represents a new Solidity construct."""
    
    name: str
    parameters: List[Parameter] = Field(default_factory=list)
    custom_attribute: Optional[str] = None
    
    def get_signature(self) -> str:
        """Get the construct signature."""
        params = ", ".join(p.get_signature() for p in self.parameters)
        return f"{self.name}({params})"
```

2. **Add Parsing Logic** in `ast_builder.py`:

```python
def _build_new_construct(self, node: tree_sitter.Node) -> NewConstructDeclaration:
    """Build a new construct declaration."""
    name = self._get_node_text(self._find_child_by_type(node, "identifier"))
    
    # Extract parameters, attributes, etc.
    parameters = self._extract_parameters(node)
    custom_attribute = self._extract_custom_attribute(node)
    
    return NewConstructDeclaration(
        node_type=NodeType.NEW_CONSTRUCT,
        source_location=self._create_source_location(node),
        raw_node=node,
        name=name,
        parameters=parameters,
        custom_attribute=custom_attribute
    )
```

3. **Add to Contract Building** in `ast_builder.py`:

```python
def _build_contract(self, node: tree_sitter.Node) -> ContractDeclaration:
    # ... existing code ...
    
    # Add new construct parsing
    new_constructs = []
    for child in node.children:
        if child.type == "new_construct_definition":
            new_constructs.append(self._build_new_construct(child))
    
    return ContractDeclaration(
        # ... existing fields ...
        new_constructs=new_constructs
    )
```

### 2. Adding New Query Methods

To add a new traditional query method:

1. **Add to SolidityQueryEngine** in `engine.py`:

```python
def find_new_constructs(
    self,
    name_patterns: Optional[Union[str, List[str], Pattern]] = None,
    custom_attribute: Optional[str] = None,
    contract_name: Optional[str] = None,
    **filters: Any
) -> List[NewConstructDeclaration]:
    """Find new construct declarations."""
    
    # Get all constructs from contracts
    all_constructs = []
    contracts = self._get_contracts(contract_name)
    
    for contract in contracts:
        all_constructs.extend(contract.new_constructs)
    
    # Apply filters
    result = all_constructs
    
    if name_patterns:
        result = [c for c in result 
                 if self.pattern_matcher.matches_name_pattern(c.name, name_patterns)]
    
    if custom_attribute:
        result = [c for c in result if c.custom_attribute == custom_attribute]
    
    return result
```

### 3. Adding New Collection Classes

To add a fluent collection for the new construct:

1. **Create Collection Class** in `collections.py`:

```python
class NewConstructCollection(BaseCollection[NewConstructDeclaration]):
    """Collection of new construct declarations with fluent query methods."""
    
    def with_name(self, pattern: Union[str, Pattern]) -> 'NewConstructCollection':
        """Filter by name pattern."""
        filtered = [c for c in self._elements 
                   if self._engine.pattern_matcher.matches_name_pattern(c.name, pattern)]
        return NewConstructCollection(filtered, self._engine)
    
    def with_custom_attribute(self, value: str) -> 'NewConstructCollection':
        """Filter by custom attribute value."""
        filtered = [c for c in self._elements if c.custom_attribute == value]
        return NewConstructCollection(filtered, self._engine)
    
    def by_parameter_count(self, count: int) -> 'NewConstructCollection':
        """Filter by parameter count."""
        filtered = [c for c in self._elements if len(c.parameters) == count]
        return NewConstructCollection(filtered, self._engine)
```

2. **Add Property to Engine** in `engine.py`:

```python
@property
def new_constructs(self) -> NewConstructCollection:
    """Get new construct collection for fluent queries."""
    all_constructs = self.find_new_constructs()
    return NewConstructCollection(all_constructs, self)
```

### 4. Adding Navigation Methods

To add navigation between collections:

```python
# In ContractCollection
def get_new_constructs(self) -> NewConstructCollection:
    """Get all new constructs from contracts in this collection."""
    all_constructs = []
    for contract in self._elements:
        all_constructs.extend(contract.new_constructs)
    return NewConstructCollection(all_constructs, self._engine)

# In NewConstructCollection  
def get_parameters(self) -> ParameterCollection:
    """Get all parameters from constructs in this collection."""
    all_parameters = []
    for construct in self._elements:
        all_parameters.extend(construct.parameters)
    return ParameterCollection(all_parameters, self._engine)
```

## Code Style Guidelines

### Python Style

- **PEP 8 Compliance**: Follow Python style guidelines
- **Type Hints**: Use type hints for all public methods
- **Docstrings**: Google-style docstrings for all classes and methods
- **Line Length**: 88 characters (Black default)

```python
def find_elements(
    self,
    name_patterns: Optional[Union[str, List[str], Pattern]] = None,
    **filters: Any
) -> List[ASTNode]:
    """
    Find elements matching the specified criteria.
    
    Args:
        name_patterns: Pattern(s) to match against element names
        **filters: Additional filter conditions
        
    Returns:
        List of matching AST nodes
        
    Raises:
        ValueError: If patterns are invalid
    """
    # Implementation here
    pass
```

### Error Handling

- **Graceful Degradation**: Continue processing when possible
- **Informative Messages**: Include context in error messages
- **Structured Exceptions**: Use custom exception types

```python
class ParseError(Exception):
    """Error during parsing operation."""
    
    def __init__(self, message: str, source_file: Optional[Path] = None):
        self.source_file = source_file
        super().__init__(message)
```

### Performance Considerations

- **Lazy Evaluation**: Defer expensive operations until needed
- **Caching**: Cache expensive computations
- **Memory Efficiency**: Use generators for large result sets

```python
def _get_all_functions(self) -> List[FunctionDeclaration]:
    """Get all functions with caching."""
    if not hasattr(self, '_cached_functions'):
        self._cached_functions = []
        for contract in self.contracts:
            self._cached_functions.extend(contract.functions)
    return self._cached_functions
```

## Contributing Workflow

### 1. Issue Creation

Before starting work:
- Check existing issues for duplicates
- Create detailed issue with reproduction steps
- Discuss approach with maintainers

### 2. Development Process

```bash
# Create feature branch
git checkout -b feature/new-functionality

# Make changes with tests
# ... development work ...

# Run full test suite
uv run python -m pytest tests/ -v

# Check code quality
uv run black sol_query/ tests/
uv run mypy sol_query/
uv run ruff check sol_query/ tests/

# Commit changes
git add .
git commit -m "feat: add new functionality

- Add support for new Solidity construct
- Implement fluent query interface  
- Add comprehensive tests
- Update documentation"
```

### 3. Pull Request Process

1. **Create PR** with clear description
2. **Link Issues** that the PR addresses
3. **Add Tests** for new functionality
4. **Update Documentation** as needed
5. **Request Review** from maintainers

### PR Template

```markdown
## Description
Brief description of changes made.

## Changes
- [ ] New feature implementation
- [ ] Test coverage added
- [ ] Documentation updated
- [ ] Breaking changes (if any)

## Testing
- [ ] All tests pass
- [ ] New tests added for new functionality
- [ ] Manual testing completed

## Related Issues
Fixes #123
```

## Performance Optimization

### Profiling

```bash
# Profile specific operations
uv run python -m cProfile -o profile.stats example.py

# Analyze with snakeviz
uv run snakeviz profile.stats

# Memory profiling
uv run python -m memory_profiler example.py
```

### Optimization Strategies

1. **AST Caching**: Cache parsed ASTs to avoid re-parsing
2. **Lazy Loading**: Load source files only when needed
3. **Index Building**: Build indexes for common queries
4. **Parallel Processing**: Use multiprocessing for large codebases

## Documentation Guidelines

### Code Documentation

- **Class Docstrings**: Describe purpose, usage, examples
- **Method Docstrings**: Parameters, returns, raises, examples
- **Type Hints**: Complete type information for all APIs

### API Documentation

Keep `docs/api-reference.md` updated with:
- New methods and classes
- Parameter descriptions
- Usage examples
- Migration guides for breaking changes

### Examples

Add practical examples to `docs/query-examples.md` for:
- New query patterns
- Real-world use cases
- Integration scenarios

## Release Process

### Version Management

- **Semantic Versioning**: MAJOR.MINOR.PATCH
- **Changelog**: Maintain CHANGELOG.md
- **Breaking Changes**: Document migration paths

### Release Checklist

1. Update version in `pyproject.toml`
2. Update CHANGELOG.md
3. Run full test suite
4. Update documentation
5. Create release tag
6. Publish to PyPI (if applicable)

This development guide provides the foundation for contributing to Sol-Query while maintaining code quality and consistency.
