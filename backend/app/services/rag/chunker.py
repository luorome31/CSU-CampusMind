"""
Text Chunker - Split text into chunks
"""
import uuid
from datetime import datetime
from typing import List

from app.schema.chunk import ChunkModel


class TextChunker:
    """Split text into chunks with overlap"""

    def __init__(self, chunk_size: int = 500, overlap_size: int = 100):
        self.chunk_size = chunk_size
        self.overlap_size = overlap_size

    def split_text_by_lines(self, text: str) -> List[str]:
        """
        Split text by newlines, ensuring each chunk doesn't exceed chunk_size
        with overlap_size overlap between chunks.
        """
        lines = text.splitlines()
        chunks = []
        current_chunk = []
        current_length = 0

        for line in lines:
            line_length = len(line)

            if current_length + line_length > self.chunk_size:
                if current_chunk:
                    chunk = "\n".join(current_chunk)
                    chunks.append(chunk)
                    # Keep overlap from the end
                    overlap = chunk[-self.overlap_size:] if self.overlap_size > 0 else ""
                    current_chunk = [overlap] if overlap else []
                    current_length = len(overlap)

            current_chunk.append(line)
            current_length += line_length

        # Handle last chunk
        if current_chunk:
            chunk = "\n".join(current_chunk)
            chunks.append(chunk)

        return chunks

    def chunk_text(
        self,
        text: str,
        file_id: str,
        file_name: str,
        knowledge_id: str
    ) -> List[ChunkModel]:
        """Convert text into chunk models"""
        contents = self.split_text_by_lines(text)
        chunks = []
        update_time = datetime.now().isoformat()

        for content in contents:
            chunk_id = f"{file_id[:8]}_{uuid.uuid4().hex[:8]}"
            chunks.append(ChunkModel(
                chunk_id=chunk_id,
                content=content,
                file_id=file_id,
                file_name=file_name,
                knowledge_id=knowledge_id,
                update_time=update_time
            ))

        return chunks


# Default chunker instance
default_chunker = TextChunker(chunk_size=500, overlap_size=100)
