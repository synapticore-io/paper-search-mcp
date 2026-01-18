# GitHub Copilot Instructions for paper-search-mcp

## Project Overview

This is a Model Context Protocol (MCP) server for searching and downloading academic papers from multiple sources, including arXiv, PubMed, bioRxiv, medRxiv, Google Scholar, IACR ePrint Archive, Semantic Scholar, and CrossRef.

**Tech Stack:**
- Python 3.10+
- FastMCP for MCP server implementation
- httpx for async HTTP requests
- BeautifulSoup4 and lxml for HTML parsing
- unittest for testing
- typer for CLI
- rich for enhanced terminal output

**Project Structure:**
- `paper_search_mcp/` - Main package directory
  - `server.py` - MCP server implementation with tool definitions
  - `cli.py` - Command-line interface using typer
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

**Using the CLI:**
```bash
# Search for papers
paper-search search "machine learning" --source arxiv --max-results 10

# Download a paper
paper-search download 2106.12345 --source arxiv --output ./downloads

# Read paper text
paper-search read 2106.12345 --source arxiv

# List available sources
paper-search list-sources
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
- All searcher methods (search, download_pdf, read_paper) are async and use httpx
- Use relative imports within the package: `from ..paper import Paper` (from academic_platforms/)
- Platform searchers use `httpx` library with async/await pattern
- Server.py uses FastMCP framework to expose async searcher methods as MCP tools
- CLI module uses typer to provide command-line interface to all search/download functions

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
import httpx
from ..paper import Paper

class ExampleSearcher:
    """Searcher for Example Platform."""
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key
        self.base_url = "https://api.example.com"
    
    async def search(self, query: str, max_results: int = 10) -> List[Paper]:
        """
        Search for papers on Example Platform.
        
        Args:
            query: Search query string
            max_results: Maximum number of results to return
            
        Returns:
            List of Paper objects
        """
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.base_url,
                params={'q': query, 'limit': max_results}
            )
            response.raise_for_status()
            data = response.json()
            
        papers = []
        for item in data['results']:
            papers.append(Paper(
                paper_id=item['id'],
                title=item['title'],
                authors=item['authors'],
                abstract=item['abstract'],
                doi=item.get('doi', ''),
                published_date=datetime.fromisoformat(item['date']),
                pdf_url=item.get('pdf_url', ''),
                url=item['url'],
                source='example'
            ))
        return papers
    
    async def download_pdf(self, paper_id: str, save_path: str) -> str:
        """Download PDF for a paper."""
        pdf_url = f"{self.base_url}/papers/{paper_id}/pdf"
        async with httpx.AsyncClient() as client:
            response = await client.get(pdf_url)
            response.raise_for_status()
        
        output_file = f"{save_path}/{paper_id}.pdf"
        with open(output_file, 'wb') as f:
            f.write(response.content)
        return output_file
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

### Platform searchers use httpx with async/await
```python
import httpx
from typing import List

async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    """Search implementation using httpx."""
    async with httpx.AsyncClient() as client:
        response = await client.get(self.BASE_URL, params={'q': query})
        response.raise_for_status()
        # Process response
    return papers
```

### Server exposes async searchers as MCP tools
```python
# In server.py
async def async_search(searcher, query: str, max_results: int, **kwargs) -> List[Dict]:
    # Searchers now use httpx internally and are async
    papers = await searcher.search(query, max_results=max_results)
    return [paper.to_dict() for paper in papers]

@mcp.tool()
async def search_arxiv(query: str, max_results: int = 10) -> List[Dict]:
    """Search academic papers from arXiv."""
    return await async_search(arxiv_searcher, query, max_results)
```

### CLI commands use asyncio to run async functions
```python
# In cli.py
@app.command()
def search(query: str, source: str = "arxiv", max_results: int = 10):
    """Search for papers."""
    async def run_search():
        papers = await searcher.search(query, max_results=max_results)
        display_papers(papers, source)
    
    asyncio.run(run_search())
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
import httpx

async def search(self, query: str, max_results: int = 10) -> List[Paper]:
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=10.0)
            response.raise_for_status()
            # Process response
    except httpx.HTTPError as e:
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

**Current key dependencies:**
- `httpx[socks]>=0.28.1` - Async HTTP client for all network requests
- `fastmcp` - FastMCP framework for MCP server
- `mcp[cli]>=1.6.0` - MCP Python SDK
- `typer>=0.9.0` - CLI framework
- `rich>=13.0.0` - Enhanced terminal output
- `feedparser` - RSS/Atom feed parsing (for arXiv)
- `beautifulsoup4>=4.12.0` - HTML parsing
- `lxml>=4.9.0` - XML/HTML parser
- `PyPDF2>=3.0.0` - PDF text extraction

## Version Management

- Version is defined in `pyproject.toml`
- Follow semantic versioning (MAJOR.MINOR.PATCH)
- Update version before creating release tags
- Tag format: `v0.1.0`, `v0.2.0`, etc.
