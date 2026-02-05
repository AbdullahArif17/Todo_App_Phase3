import zlib
import gzip
import bz2
import lzma
from typing import Any, Dict, List, Union
import json
import pickle
from enum import Enum


class CompressionAlgorithm(Enum):
    """Enumeration of supported compression algorithms."""
    ZLIB = "zlib"
    GZIP = "gzip"
    BZIP2 = "bz2"
    LZMA = "lzma"


class ConversationCompression:
    """
    Utility class for compressing and decompressing conversation data.
    """

    @staticmethod
    def compress_data(data: Union[str, bytes, Dict, List], algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB) -> bytes:
        """
        Compress data using the specified algorithm.

        Args:
            data: Data to compress (string, bytes, dict, or list)
            algorithm: Compression algorithm to use

        Returns:
            Compressed data as bytes
        """
        # Convert data to bytes if needed
        if isinstance(data, str):
            data_bytes = data.encode('utf-8')
        elif isinstance(data, (dict, list)):
            data_bytes = json.dumps(data).encode('utf-8')
        elif isinstance(data, bytes):
            data_bytes = data
        else:
            # For other types, try to serialize with pickle
            data_bytes = pickle.dumps(data)

        # Apply compression based on algorithm
        if algorithm == CompressionAlgorithm.ZLIB:
            return zlib.compress(data_bytes)
        elif algorithm == CompressionAlgorithm.GZIP:
            return gzip.compress(data_bytes)
        elif algorithm == CompressionAlgorithm.BZIP2:
            return bz2.compress(data_bytes)
        elif algorithm == CompressionAlgorithm.LZMA:
            return lzma.compress(data_bytes)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

    @staticmethod
    def decompress_data(compressed_data: bytes, algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB, return_type: str = 'str') -> Union[str, Dict, List, Any]:
        """
        Decompress data using the specified algorithm.

        Args:
            compressed_data: Compressed data as bytes
            algorithm: Compression algorithm used for compression
            return_type: Expected return type ('str', 'dict', 'list', 'auto')

        Returns:
            Decompressed data in the requested format
        """
        # Decompress based on algorithm
        if algorithm == CompressionAlgorithm.ZLIB:
            decompressed_bytes = zlib.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.GZIP:
            decompressed_bytes = gzip.decompress(compressed_data)
        elif algorithm == CompressionAlgorithm.BZIP2:
            decompressed_bytes = bz2.decompress(compressed_bytes)
        elif algorithm == CompressionAlgorithm.LZMA:
            decompressed_bytes = lzma.decompress(compressed_data)
        else:
            raise ValueError(f"Unsupported compression algorithm: {algorithm}")

        # Convert bytes back to requested type
        decompressed_str = decompressed_bytes.decode('utf-8')

        if return_type == 'str':
            return decompressed_str
        elif return_type == 'dict':
            return json.loads(decompressed_str)
        elif return_type == 'list':
            return json.loads(decompressed_str)
        elif return_type == 'auto':
            try:
                # Try to parse as JSON first
                parsed = json.loads(decompressed_str)
                if isinstance(parsed, (dict, list)):
                    return parsed
                else:
                    return decompressed_str
            except json.JSONDecodeError:
                # If JSON parsing fails, return as string
                return decompressed_str
        else:
            raise ValueError(f"Unsupported return type: {return_type}")

    @staticmethod
    def compress_conversation_data(conversation_data: Dict) -> bytes:
        """
        Compress conversation data specifically.

        Args:
            conversation_data: Dictionary containing conversation data

        Returns:
            Compressed conversation data as bytes
        """
        return ConversationCompression.compress_data(conversation_data, CompressionAlgorithm.GZIP)

    @staticmethod
    def decompress_conversation_data(compressed_data: bytes) -> Dict:
        """
        Decompress conversation data specifically.

        Args:
            compressed_data: Compressed conversation data as bytes

        Returns:
            Decompressed conversation data as dictionary
        """
        return ConversationCompression.decompress_data(compressed_data, CompressionAlgorithm.GZIP, 'dict')

    @staticmethod
    def get_compression_ratio(original_size: int, compressed_size: int) -> float:
        """
        Calculate the compression ratio.

        Args:
            original_size: Original size in bytes
            compressed_size: Compressed size in bytes

        Returns:
            Compression ratio as a percentage (e.g., 75.0 for 75% reduction)
        """
        if original_size == 0:
            return 0.0
        return ((original_size - compressed_size) / original_size) * 100

    @staticmethod
    def compress_message_content(content: str, algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB) -> bytes:
        """
        Compress a single message content.

        Args:
            content: Message content to compress
            algorithm: Compression algorithm to use

        Returns:
            Compressed message content as bytes
        """
        return ConversationCompression.compress_data(content, algorithm)

    @staticmethod
    def decompress_message_content(compressed_content: bytes, algorithm: CompressionAlgorithm = CompressionAlgorithm.ZLIB) -> str:
        """
        Decompress a single message content.

        Args:
            compressed_content: Compressed message content as bytes
            algorithm: Compression algorithm used for compression

        Returns:
            Decompressed message content as string
        """
        return ConversationCompression.decompress_data(compressed_content, algorithm, 'str')


# Convenience functions for common operations
def compress_conversation(conversation_dict: Dict) -> bytes:
    """Compress a conversation dictionary."""
    return ConversationCompression.compress_conversation_data(conversation_dict)


def decompress_conversation(compressed_bytes: bytes) -> Dict:
    """Decompress a conversation dictionary."""
    return ConversationCompression.decompress_conversation_data(compressed_bytes)


def compress_large_message(content: str) -> bytes:
    """Compress a large message content using best algorithm."""
    # For large content, use GZIP for good balance of speed and compression
    return ConversationCompression.compress_message_content(content, CompressionAlgorithm.GZIP)


def decompress_large_message(compressed_content: bytes) -> str:
    """Decompress a large message content."""
    return ConversationCompression.decompress_message_content(compressed_content, CompressionAlgorithm.GZIP)