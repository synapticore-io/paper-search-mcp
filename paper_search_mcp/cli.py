#!/usr/bin/env python3
"""
Command-line interface for paper-search-mcp.
Provides commands for searching and downloading academic papers from multiple sources.
"""
import asyncio
import os
from typing import Optional
import typer
from rich.console import Console
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
import json

from .academic_platforms.arxiv import ArxivSearcher
from .academic_platforms.pubmed import PubMedSearcher
from .academic_platforms.biorxiv import BioRxivSearcher
from .academic_platforms.medrxiv import MedRxivSearcher
from .academic_platforms.google_scholar import GoogleScholarSearcher
from .academic_platforms.iacr import IACRSearcher
from .academic_platforms.semantic import SemanticSearcher
from .academic_platforms.crossref import CrossRefSearcher
from .academic_platforms.searxng import SearXNGSearcher
from .knowledge import KnowledgeStore
from .document_processor import DocumentProcessor, DOCLING_AVAILABLE

app = typer.Typer(
    name="paper-search",
    help="Search and download academic papers from multiple sources",
    add_completion=False,
)
console = Console()

# Initialize searchers
arxiv_searcher = ArxivSearcher()
pubmed_searcher = PubMedSearcher()
biorxiv_searcher = BioRxivSearcher()
medrxiv_searcher = MedRxivSearcher()
google_scholar_searcher = GoogleScholarSearcher()
iacr_searcher = IACRSearcher()
semantic_searcher = SemanticSearcher()
crossref_searcher = CrossRefSearcher()
searxng_searcher = SearXNGSearcher()

# Initialize knowledge store
knowledge_store = KnowledgeStore()

# Initialize document processor if available
doc_processor = DocumentProcessor() if DOCLING_AVAILABLE else None


def display_papers(papers, source: str):
    """Display papers in a formatted table."""
    if not papers:
        console.print(f"[yellow]No papers found from {source}[/yellow]")
        return
    
    table = Table(title=f"Papers from {source}")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="green")
    table.add_column("Authors", style="blue")
    table.add_column("Year", style="magenta")
    
    for paper in papers:
        year = paper.published_date.year if paper.published_date else "N/A"
        authors = ", ".join(paper.authors[:3]) + ("..." if len(paper.authors) > 3 else "")
        table.add_row(
            paper.paper_id,
            paper.title[:80] + ("..." if len(paper.title) > 80 else ""),
            authors[:40] + ("..." if len(authors) > 40 else ""),
            str(year)
        )
    
    console.print(table)
    console.print(f"\n[green]Found {len(papers)} papers[/green]")


@app.command()
def search(
    query: str = typer.Argument(..., help="Search query"),
    source: str = typer.Option("arxiv", "--source", "-s", help="Source to search: arxiv, pubmed, biorxiv, medrxiv, google-scholar, iacr, semantic, crossref"),
    max_results: int = typer.Option(10, "--max-results", "-n", help="Maximum number of results"),
    year: Optional[int] = typer.Option(None, "--year", "-y", help="Filter by publication year (if supported)"),
):
    """Search for academic papers from various sources."""
    
    async def run_search():
        searchers = {
            "arxiv": arxiv_searcher,
            "pubmed": pubmed_searcher,
            "biorxiv": biorxiv_searcher,
            "medrxiv": medrxiv_searcher,
            "google-scholar": google_scholar_searcher,
            "iacr": iacr_searcher,
            "semantic": semantic_searcher,
            "crossref": crossref_searcher,
            "searxng": searxng_searcher,
        }
        
        if source not in searchers:
            console.print(f"[red]Error: Unknown source '{source}'[/red]")
            console.print(f"Available sources: {', '.join(searchers.keys())}")
            raise typer.Exit(1)
        
        searcher = searchers[source]
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Searching {source}...", total=None)
            
            try:
                if year and source in ["crossref"]:
                    papers = await searcher.search(query, year=year, max_results=max_results)
                else:
                    papers = await searcher.search(query, max_results=max_results)
                
                display_papers(papers, source)
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_search())


@app.command()
def download(
    paper_id: str = typer.Argument(..., help="Paper ID to download"),
    source: str = typer.Option("arxiv", "--source", "-s", help="Source: arxiv, biorxiv, medrxiv, iacr, semantic"),
    output_dir: str = typer.Option("./downloads", "--output", "-o", help="Output directory"),
):
    """Download a paper PDF by its ID."""
    
    async def run_download():
        searchers = {
            "arxiv": arxiv_searcher,
            "biorxiv": biorxiv_searcher,
            "medrxiv": medrxiv_searcher,
            "iacr": iacr_searcher,
            "semantic": semantic_searcher,
        }
        
        if source not in searchers:
            console.print(f"[red]Error: Unknown source '{source}'[/red]")
            console.print(f"Available sources for download: {', '.join(searchers.keys())}")
            raise typer.Exit(1)
        
        searcher = searchers[source]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Downloading paper {paper_id}...", total=None)
            
            try:
                pdf_path = await searcher.download_pdf(paper_id, output_dir)
                console.print(f"[green]✓ Downloaded to: {pdf_path}[/green]")
            except Exception as e:
                console.print(f"[red]Error downloading paper: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_download())


@app.command()
def read(
    paper_id: str = typer.Argument(..., help="Paper ID to read"),
    source: str = typer.Option("arxiv", "--source", "-s", help="Source: arxiv, biorxiv, medrxiv, iacr, semantic"),
    output_dir: str = typer.Option("./downloads", "--output", "-o", help="Directory where PDF is/will be saved"),
    show_all: bool = typer.Option(False, "--all", "-a", help="Show full text (default: first 1000 chars)"),
):
    """Read and extract text from a paper PDF."""
    
    async def run_read():
        searchers = {
            "arxiv": arxiv_searcher,
            "biorxiv": biorxiv_searcher,
            "medrxiv": medrxiv_searcher,
            "iacr": iacr_searcher,
            "semantic": semantic_searcher,
        }
        
        if source not in searchers:
            console.print(f"[red]Error: Unknown source '{source}'[/red]")
            console.print(f"Available sources for reading: {', '.join(searchers.keys())}")
            raise typer.Exit(1)
        
        searcher = searchers[source]
        
        # Create output directory if it doesn't exist
        os.makedirs(output_dir, exist_ok=True)
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            console=console,
        ) as progress:
            progress.add_task(f"Reading paper {paper_id}...", total=None)
            
            try:
                text = await searcher.read_paper(paper_id, output_dir)
                if text:
                    if show_all:
                        console.print(text)
                    else:
                        console.print(text[:1000])
                        if len(text) > 1000:
                            console.print(f"\n[dim]... ({len(text) - 1000} more characters. Use --all to see full text)[/dim]")
                    console.print(f"\n[green]✓ Total length: {len(text)} characters[/green]")
                else:
                    console.print("[yellow]No text extracted from paper[/yellow]")
            except Exception as e:
                console.print(f"[red]Error reading paper: {e}[/red]")
                raise typer.Exit(1)
    
    asyncio.run(run_read())


@app.command()
def list_sources():
    """List all available paper sources."""
    sources = [
        ("arxiv", "arXiv - Open access preprint repository", "search, download, read"),
        ("pubmed", "PubMed - Biomedical literature database", "search"),
        ("biorxiv", "bioRxiv - Preprint server for biology", "search, download, read"),
        ("medrxiv", "medRxiv - Preprint server for health sciences", "search, download, read"),
        ("google-scholar", "Google Scholar - Academic search engine", "search"),
        ("iacr", "IACR ePrint - Cryptology preprint archive", "search, download, read"),
        ("semantic", "Semantic Scholar - AI-powered research tool", "search, download, read"),
        ("crossref", "CrossRef - Citation linking service", "search"),
        ("searxng", "SearXNG - Privacy-focused metasearch engine", "search"),
    ]
    
    table = Table(title="Available Paper Sources")
    table.add_column("Source", style="cyan", no_wrap=True)
    table.add_column("Description", style="green")
    table.add_column("Capabilities", style="blue")
    
    for source, description, capabilities in sources:
        table.add_row(source, description, capabilities)
    
    console.print(table)


# Knowledge management commands
@app.command()
def knowledge_store(
    paper_id: str = typer.Argument(..., help="Paper ID to store in knowledge graph"),
    source: str = typer.Option("arxiv", "--source", "-s", help="Source platform"),
    max_results: int = typer.Option(1, help="Fetch this paper"),
):
    """Store a paper in the knowledge graph database."""
    async def run_store():
        searchers = {
            "arxiv": arxiv_searcher,
            "pubmed": pubmed_searcher,
            "biorxiv": biorxiv_searcher,
            "medrxiv": medrxiv_searcher,
            "iacr": iacr_searcher,
            "semantic": semantic_searcher,
        }
        
        searcher = searchers.get(source)
        if not searcher:
            console.print(f"[red]Source {source} not supported for storing[/red]")
            return
        
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task(f"Fetching and storing paper {paper_id}...", total=None)
            
            try:
                # Search for the paper
                papers = await searcher.search(paper_id, max_results=1)
                if not papers:
                    console.print(f"[yellow]Paper {paper_id} not found[/yellow]")
                    return
                
                paper = papers[0]
                paper_data = paper.to_dict()
                
                # Store in knowledge graph
                record_id = await knowledge_store.store_paper(paper_data)
                console.print(f"[green]✓ Paper stored with ID: {record_id}[/green]")
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(run_store())


@app.command()
def knowledge_search(
    query: str = typer.Argument(..., help="Search query"),
    limit: int = typer.Option(10, "--limit", "-l", help="Maximum results"),
):
    """Search papers in the knowledge graph."""
    async def run_search():
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task("Searching knowledge graph...", total=None)
            
            try:
                papers = await knowledge_store.search_papers(query, limit)
                
                if not papers:
                    console.print("[yellow]No papers found in knowledge graph[/yellow]")
                    return
                
                table = Table(title=f"Knowledge Graph Results for '{query}'")
                table.add_column("Paper ID", style="cyan")
                table.add_column("Title", style="green")
                table.add_column("Source", style="blue")
                
                for paper in papers:
                    table.add_row(
                        paper.get('paper_id', 'N/A'),
                        paper.get('title', 'Untitled')[:60] + "...",
                        paper.get('source', 'unknown')
                    )
                
                console.print(table)
                console.print(f"[green]Found {len(papers)} papers[/green]")
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(run_search())


@app.command()
def knowledge_stats():
    """Get statistics about the knowledge graph."""
    async def run_stats():
        try:
            stats = await knowledge_store.get_knowledge_stats()
            
            console.print("\n[bold cyan]Knowledge Graph Statistics[/bold cyan]\n")
            console.print(f"  Papers:        {stats.get('papers', 0)}")
            console.print(f"  Concepts:      {stats.get('concepts', 0)}")
            console.print(f"  Relationships: {stats.get('relationships', 0)}\n")
            
        except Exception as e:
            console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(run_stats())


# Document processing commands
@app.command()
def process_pdf(
    pdf_path: str = typer.Argument(..., help="Path to PDF file"),
    output_format: str = typer.Option("markdown", "--format", "-f", help="Output format: markdown, json"),
):
    """Process a PDF with advanced Docling parser."""
    if not doc_processor:
        console.print("[red]Docling not available. Install with: pip install docling[/red]")
        return
    
    async def run_process():
        with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), console=console) as progress:
            progress.add_task(f"Processing {pdf_path}...", total=None)
            
            try:
                result = await doc_processor.process_pdf(pdf_path)
                
                if output_format == "json":
                    console.print(json.dumps(result, indent=2, default=str))
                else:
                    console.print("\n[bold cyan]Extracted Text (Markdown):[/bold cyan]\n")
                    console.print(result.get('text', '')[:2000])
                    if len(result.get('text', '')) > 2000:
                        console.print("\n[dim]... (truncated)[/dim]")
                    
                    console.print(f"\n[green]✓ Metadata:[/green]")
                    for key, value in result.get('metadata', {}).items():
                        console.print(f"  {key}: {value}")
                
            except Exception as e:
                console.print(f"[red]Error: {e}[/red]")
    
    asyncio.run(run_process())


if __name__ == "__main__":
    app()
