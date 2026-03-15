"""
E2E Test Script - CampusMind RAG Pipeline

Usage:
    python test_e2e.py

Requirements:
    - MinIO running on localhost:9000 (or configured)
    - Elasticsearch running on localhost:9200 (or configured)
    - ChromaDB (local file)
    - OpenAI API key (or other embedding provider)
"""
import asyncio
import os
import sys

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from app.services.rag.indexer import indexer
from app.services.rag.handler import rag_handler
from app.api.services.knowledge import KnowledgeService
from app.database.session import create_db_and_tables


async def test_full_pipeline():
    """Test the full RAG pipeline"""
    print("=" * 60)
    print("CampusMind E2E Test")
    print("=" * 60)

    # Step 1: Initialize Database
    print("\n[1] Initializing database...")
    create_db_and_tables()
    print("    ✓ Database initialized")

    # Step 2: Create Knowledge Base
    print("\n[2] Creating knowledge base...")
    try:
        kb = KnowledgeService.create_knowledge(
            name="test_knowledge",
            user_id="test_user",
            description="Test knowledge base for E2E"
        )
        print(f"    ✓ Knowledge base created: {kb.id}")
    except Exception as e:
        print(f"    ⚠ Knowledge base may already exist: {e}")

    # Step 3: Index Test Content
    print("\n[3] Indexing test content...")
    test_content = """
    CampusMind is an AI-powered campus assistant.

    Features:
    1. Web Crawling - Uses crawl4ai to fetch web content
    2. Knowledge Management - Store and manage knowledge bases
    3. RAG Retrieval - Hybrid search with ChromaDB and Elasticsearch
    4. Smart Response - AI-powered answers with context

    Technology Stack:
    - FastAPI for REST API
    - ChromaDB for vector storage
    - Elasticsearch for keyword search
    - MinIO for object storage
    """

    result = await indexer.index_content(
        content=test_content,
        knowledge_id="test_knowledge",
        source_name="test.txt",
        metadata={"test": "e2e"}
    )

    if result.get("success"):
        print(f"    ✓ Indexed {result.get('chunk_count')} chunks")
    else:
        print(f"    ✗ Indexing failed: {result.get('error')}")
        return

    # Step 4: Test Retrieval
    print("\n[4] Testing retrieval...")

    test_queries = [
        "What is CampusMind?",
        "What technologies are used?",
        "What are the features?"
    ]

    for query in test_queries:
        print(f"\n    Query: {query}")
        result = await rag_handler.retrieve_with_sources(
            query=query,
            knowledge_ids=["test_knowledge"],
            top_k=3
        )

        if result["context"]:
            print(f"    ✓ Found {len(result['sources'])} sources")
            print(f"    Context preview: {result['context'][:100]}...")
        else:
            print(f"    ✗ No results found")

    print("\n" + "=" * 60)
    print("E2E Test Complete!")
    print("=" * 60)


async def test_minimal():
    """Minimal test without external services"""
    print("\n[Minimal Test] Creating test content...")

    test_content = """
    Python is a high-level programming language.
    FastAPI is a modern web framework.
    ChromaDB is a vector database.
    """

    result = await indexer.index_content(
        content=test_content,
        knowledge_id="minimal_test",
        source_name="test.txt"
    )

    print(f"Index result: {result}")

    # Simple retrieval
    result = await rag_handler.retrieve_with_sources(
        query="What is Python?",
        knowledge_ids=["minimal_test"],
        top_k=2
    )

    print(f"Retrieve result: {result}")


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="CampusMind E2E Test")
    parser.add_argument("--minimal", action="store_true", help="Run minimal test")
    args = parser.parse_args()

    if args.minimal:
        asyncio.run(test_minimal())
    else:
        asyncio.run(test_full_pipeline())
