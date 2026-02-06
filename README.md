# Paper Search MCP

MCP server and CLI for academic paper search, download, and knowledge synthesis across 11 platforms — with SurrealDB knowledge graph, Docling document processing, and Docker-ready deployment.

![PyPI](https://img.shields.io/pypi/v/paper-search-mcp.svg) ![License](https://img.shields.io/badge/license-MIT-blue.svg) ![Python](https://img.shields.io/badge/python-3.10+-blue.svg)
[![smithery badge](https://smithery.ai/badge/@openags/paper-search-mcp)](https://smithery.ai/server/@openags/paper-search-mcp)

---

## What It Does

- **Search** papers across 11 academic platforms via a single MCP server or CLI
- **Download** full-text PDFs where available
- **Process** documents with Docling — extract structured content from PDFs, DOCX, PPTX, HTML
- **Store** papers, concepts, and relationships in a SurrealDB knowledge graph
- **Query** your knowledge base — find similar papers, explore concept relationships

```
User/AI → CLI / MCP Server → Platform Searchers → Academic APIs → Papers
                ↓                                         ↓
         FastMCP (30+ tools)                     Knowledge Graph (SurrealDB)
                ↓                                         ↓
         Document Processor (Docling)            SearXNG Meta-Search
```

## Supported Platforms

| Platform | Search | Download | Read | Notes |
|----------|--------|----------|------|-------|
| arXiv | ✓ | ✓ | ✓ | Preprint repository |
| PubMed | ✓ | ✓ | ✓ | Biomedical literature |
| bioRxiv | ✓ | ✓ | ✓ | Biology preprints |
| medRxiv | ✓ | ✓ | ✓ | Medical preprints |
| Semantic Scholar | ✓ | ✓ | ✓ | AI-powered search (API key optional) |
| CrossRef | ✓ | ✓ | ✓ | Citation database + DOI lookup |
| IACR ePrint | ✓ | ✓ | ✓ | Cryptology papers |
| Google Scholar | ✓ | — | — | Web scraping |
| SearXNG | ✓ | — | — | Privacy-focused meta-search (self-hosted) |
| Sci-Hub | — | ✓ | — | PDF downloads via DOI (optional) |
| Hugging Face Hub | ✓ | — | — | ML papers and datasets |

## Key Features

### Knowledge Graph (SurrealDB)

Store papers, extract concepts, and build a research knowledge base:

- **Store papers** with full metadata into SurrealDB
- **Add concepts** and link them to papers with relationship strength
- **Find similar papers** through concept overlap
- **Search your knowledge base** across stored papers
- **Get stats** on your accumulated knowledge

### Document Processing (Docling)

Go beyond simple PDF text extraction:

- **Structured parsing** — sections, tables, figures, references
- **Multi-format** — PDF, DOCX, PPTX, HTML
- **URL processing** — download and process documents from URLs
- **Markdown export** — clean, structured output

### Docker Stack

Full research infrastructure in one `docker-compose up`:

| Service | Purpose | Port |
|---------|---------|------|
| Paper Search MCP | MCP server | 3000 |
| SurrealDB | Knowledge graph | 8000 |
| SearXNG | Meta-search engine | 8080 |
| Valkey (Redis) | SearXNG cache | — |

## Installation

### Quick Start (MCP Client)

```bash
uv add paper-search-mcp
```

Configure Claude Desktop (`claude_desktop_config.json`):

```json
{
  "mcpServers": {
    "paper_search_server": {
      "command": "uv",
      "args": ["run", "-m", "paper_search_mcp.server"],
      "env": {
        "SEMANTIC_SCHOLAR_API_KEY": ""
      }
    }
  }
}
```

### Via Smithery

```bash
npx -y @smithery/cli install @openags/paper-search-mcp --client claude
```

### Docker — All-in-One Image

Everything in a single container (supervisord-managed):

```bash
git clone https://github.com/synapticore-io/paper-search-cli.git
cd paper-search-cli
docker build -f Dockerfile.allinone -t paper-search-mcp .
docker run -d --name paper-search \
  -p 3000:3000 -p 8080:8080 \
  -v paper-search-data:/data/surrealdb \
  -v paper-search-downloads:/app/downloads \
  paper-search-mcp
```

Starts SurrealDB, SearXNG, Valkey, and the MCP server — all in one container.

### Docker — Compose (Multi-Container)

If you prefer separate containers:

```bash
docker compose up -d
```

### Development

```bash
git clone https://github.com/synapticore-io/paper-search-cli.git
cd paper-search-cli
uv venv && source .venv/bin/activate
uv sync
```

## CLI Usage

```bash
# Search across platforms
paper-search search "transformer architectures" --source arxiv --max-results 10
paper-search search "CRISPR" --source pubmed --max-results 20
paper-search search "neural rendering" --source semantic

# Download papers
paper-search download 2106.12345 --source arxiv --output ./papers

# Read paper text
paper-search read 2106.12345 --source arxiv --all

# List all available sources
paper-search list-sources
```

## MCP Tools

### Search & Download (per platform)

| Tool | Description |
|------|-------------|
| `search_arxiv` | Search arXiv preprints |
| `search_pubmed` | Search PubMed biomedical literature |
| `search_biorxiv` | Search bioRxiv biology preprints |
| `search_medrxiv` | Search medRxiv medical preprints |
| `search_google_scholar` | Search Google Scholar |
| `search_iacr` | Search IACR cryptology archive |
| `search_semantic` | Search Semantic Scholar |
| `search_crossref` | Search CrossRef citation database |
| `search_searxng` | Search via SearXNG meta-search |
| `get_crossref_paper_by_doi` | Lookup paper by DOI |
| `download_*` / `read_*` | Download/read per platform |

### Knowledge Graph

| Tool | Description |
|------|-------------|
| `store_paper_knowledge` | Store paper metadata in SurrealDB |
| `get_paper_knowledge` | Retrieve stored paper by ID |
| `search_knowledge` | Search across stored papers |
| `add_concept_knowledge` | Add a concept/topic |
| `relate_paper_concept` | Link paper to concept with strength |
| `get_similar_papers_knowledge` | Find similar papers via concept overlap |
| `get_knowledge_stats` | Statistics on your knowledge base |

### Document Processing

| Tool | Description |
|------|-------------|
| `process_pdf_advanced` | Extract structured content from PDF (Docling) |
| `process_document_url` | Download and process document from URL |

## Python API

```python
import asyncio
from paper_search_mcp.academic_platforms.arxiv import ArxivSearcher

async def search():
    searcher = ArxivSearcher()
    papers = await searcher.search("quantum computing", max_results=5)
    for paper in papers:
        print(f"{paper.title} ({paper.published_date.year})")
        print(f"  {paper.url}")

asyncio.run(search())
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `SEMANTIC_SCHOLAR_API_KEY` | Semantic Scholar API key | — |
| `SURREALDB_URL` | SurrealDB connection URL | `ws://localhost:8000/rpc` |
| `SURREALDB_USER` | SurrealDB username | `root` |
| `SURREALDB_PASS` | SurrealDB password | `root` |
| `SURREALDB_NS` | SurrealDB namespace | `paper_search` |
| `SURREALDB_DB` | SurrealDB database | `knowledge` |
| `SEARXNG_URL` | SearXNG instance URL | `http://localhost:8080` |

## License

MIT License. See [LICENSE](LICENSE) for details.

---

*Fork of [openags/paper-search-mcp](https://github.com/openags/paper-search-mcp), extended with SurrealDB knowledge graph, Docling document processing, SearXNG meta-search, and Docker deployment.*
