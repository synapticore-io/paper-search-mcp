# GitHub Copilot Instructions for paper-search-mcp

## Project Overview

This is a Model Context Protocol (MCP) server for searching and downloading academic papers from multiple sources, including arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, and CrossRef.

**Tech Stack:**
- Python 3.10+
- FastMCP for MCP server implementation
- httpx for async HTTP requests
- BeautifulSoup4 and lxml for HTML parsing
- unittest for testing

**Project Structure:**
- `paper_search_mcp/` - Main package directory
  - `server.py` - MCP server implementation with tool definitions
  - `paper.py` - Paper data model class
  - `academic_platforms/` - Platform-specific searcher implementations
- `tests/` - Unit tests for each platform and the server
- `docs/` - Documentation and images

## Build and Test Commands

**Installing dependencies:**
```bash
# Using uv (recommended)
uv venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate
uv add -e .

# Or using pip
pip install -e .
```

**Running tests:**
```bash
# Run all tests
python -m unittest discover -s tests

# Run specific test file
python -m unittest tests.test_arxiv
python -m unittest tests.test_server

# Run specific test method
python -m unittest tests.test_arxiv.TestArxivSearcher.test_search
```

**Building the package:**
```bash
python -m pip install build
python -m build
```

**Running the MCP server:**
```bash
# For development
uv run -m paper_search_mcp.server

# For production (after installation)
python -m paper_search_mcp.server
```

## Coding Conventions and Rules

### General Python Style
- Follow PEP 8 style guidelines
- Use type hints for function parameters and return values
- Python 3.10+ features are acceptable
- Use descriptive variable names

### Code Organization
- Each academic platform should have its own module in `academic_platforms/`
- All searchers should return `Paper` objects or lists of `Paper` objects
- Use the `Paper` class defined in `paper.py` for consistent data structure
- Async functions should use `async/await` syntax properly
- Use relative imports within the package: `from ..paper import Paper` (from academic_platforms/)
- Platform searchers use `requests` library synchronously
- Server.py wraps synchronous operations in async context using `httpx`

### Testing Requirements
- Each platform searcher should have a corresponding test file in `tests/`
- Test files should be named `test_<platform>.py`
- Use `unittest.TestCase` for test classes
- Tests should verify that search results return the expected structure
- Include basic functionality tests (search, download where applicable)

### File Modification Guidelines
- **DO NOT** modify:
  - `LICENSE` file
  - `.gitignore` unless adding necessary exceptions
  - `uv.lock` directly (managed by uv)
  - Existing working tests unless fixing bugs

- **CAREFUL** when modifying:
  - `server.py` - core MCP server, changes affect all tools
  - `paper.py` - data model used across all platforms

### Adding New Academic Platforms

When adding a new academic platform searcher:

1. Create a new file in `academic_platforms/<platform_name>.py`
2. Implement a searcher class that inherits appropriate base patterns
3. Implement `search()` method returning `List[Paper]`
4. Import and initialize the searcher in `server.py`
5. Add corresponding MCP tools in `server.py` using `@mcp.tool()` decorator
6. Create tests in `tests/test_<platform_name>.py`
7. Update README.md TODO list if applicable

### Example: Platform Searcher Implementation

```python
# academic_platforms/example.py
from typing import List
from datetime import datetime
import requests
from ..paper import Paper

class ExampleSearcher:
    """Searcher for Example Platform."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on Example Platform.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        papers = []
        # Implementation here
        return papers
```

### Example: MCP Tool Definition

```python
# In server.py
from .academic_platforms.example import ExampleSearcher

example_searcher = ExampleSearcher()

@mcp.tool()
async def search_example(query: str, max_results: int = 10) -> List[Dict]:
    """Search academic papers from Example Platform.
    
    Args:
        query: Search query string (e.g., 'machine learning').
        max_results: Maximum number of papers to return (default: 10).
        
    Returns:
        List of dictionaries with paper metadata.
    """
    return await async_search(example_searcher, query, max_results)
```

### Example: Unit Test

```python
# tests/test_example.py
import unittest
from paper_search_mcp.academic_platforms.example import ExampleSearcher

class TestExampleSearcher(unittest.TestCase):
    def test_search(self):
        searcher = ExampleSearcher()
        papers = searcher.search("machine learning", max_results=10)
        self.assertEqual(len(papers), 10)
        self.assertTrue(papers[0].title)
        
if __name__ == '__main__':
    unittest.main()
```

## Security Considerations

- Never commit API keys or secrets to the repository
- API keys should be passed through environment variables
- Validate and sanitize user inputs in search queries
- Be cautious with file downloads - validate paths and content
- Rate limit API calls to external services when possible

## Common Patterns

### Platform searchers use requests synchronously
```python
import requests
from typing import List

def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """Search implementation using requests."""
    response = requests.get(self.BASE_URL, params={'q': query})
    response.raise_for_status()
    # Process response
    return papers
```

### Server wraps synchronous searchers in async context
```python
# In server.py, httpx is used as async wrapper
async def async_search(searcher, query: str, max_results: int, **kwargs) -> List[Dict]:
    async with httpx.AsyncClient() as client:
        # Searchers use requests internally
        papers = searcher.search(query, max_results=max_results)
        return [paper.to_dict() for paper in papers]
```

### Paper object creation
```python
from datetime import datetime

paper = Paper(
    paper_id="unique-id",
    title="Paper Title",
    authors=["Author One", "Author Two"],
    abstract="Paper abstract text",
    doi="10.1234/example.doi",
    published_date=datetime(2024, 1, 1),
    pdf_url="https://example.com/paper.pdf",
    url="https://example.com/paper",
    source="example_platform"
)
```

### Error handling in searchers
```python
import requests

try:
    response = requests.get(url, timeout=10)
    response.raise_for_status()
except requests.RequestException as e:
    print(f"Error fetching data: {e}")
    return []
```

## Documentation

- Update README.md when adding new features or platforms
- Keep the TODO list in README.md up to date
- Document any new environment variables in README.md
- Add docstrings to all public methods and classes

## MCP Integration Notes

- This server uses the FastMCP framework from the MCP Python SDK
- Tools are registered using `@mcp.tool()` decorator
- All tool functions should be async
- Tool docstrings are exposed to MCP clients as tool descriptions
- Return types should be JSON-serializable (Dict, List, str, etc.)

## Dependencies

When adding new dependencies:
1. Add them to `dependencies` in `pyproject.toml`
2. Run `uv add <package>` to update lock file
3. Document why the dependency is needed
4. Prefer lightweight, well-maintained packages

## Version Management

- Version is defined in `pyproject.toml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version before creating release tags
- Tag format: `v0.1.0`, `v0.2.0`, etc.
