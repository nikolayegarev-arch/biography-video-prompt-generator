"""
File operations with atomic writes and error handling.
"""
import json
import csv
import tempfile
import shutil
import logging
from pathlib import Path
from typing import Dict, List, Any, Optional
from exceptions import FileOperationError

logger = logging.getLogger(__name__)


def atomic_write(file_path: Path, content: str, encoding: str = 'utf-8'):
    """
    Atomically write content to file using temp file + rename.
    
    Args:
        file_path: Target file path
        content: Content to write
        encoding: File encoding
        
    Raises:
        FileOperationError: If write fails
    """
    try:
        # Create parent directory if it doesn't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Write to temporary file in same directory
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )
        
        try:
            with open(temp_fd, 'w', encoding=encoding) as f:
                f.write(content)
            
            # Atomic rename
            shutil.move(temp_path, file_path)
            logger.debug(f"Successfully wrote to {file_path}")
        except Exception as e:
            # Clean up temp file on error
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            raise e
    except Exception as e:
        raise FileOperationError(f"Failed to write {file_path}: {e}")


def save_json(file_path: Path, data: Dict[str, Any], indent: int = 2):
    """
    Save data to JSON file atomically.
    
    Args:
        file_path: Target file path
        data: Data to save
        indent: JSON indentation
        
    Raises:
        FileOperationError: If save fails
    """
    try:
        content = json.dumps(data, indent=indent, ensure_ascii=False)
        atomic_write(file_path, content)
    except Exception as e:
        raise FileOperationError(f"Failed to save JSON to {file_path}: {e}")


def load_json(file_path: Path) -> Dict[str, Any]:
    """
    Load data from JSON file.
    
    Args:
        file_path: File path to load
        
    Returns:
        Loaded data
        
    Raises:
        FileOperationError: If load fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        raise FileOperationError(f"File not found: {file_path}")
    except json.JSONDecodeError as e:
        raise FileOperationError(f"Invalid JSON in {file_path}: {e}")
    except Exception as e:
        raise FileOperationError(f"Failed to load JSON from {file_path}: {e}")


def save_text(file_path: Path, content: str):
    """
    Save text content to file atomically.
    
    Args:
        file_path: Target file path
        content: Text content to save
        
    Raises:
        FileOperationError: If save fails
    """
    atomic_write(file_path, content)


def load_text(file_path: Path) -> str:
    """
    Load text content from file.
    
    Args:
        file_path: File path to load
        
    Returns:
        File content
        
    Raises:
        FileOperationError: If load fails
    """
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return f.read()
    except FileNotFoundError:
        raise FileOperationError(f"File not found: {file_path}")
    except Exception as e:
        raise FileOperationError(f"Failed to load text from {file_path}: {e}")


def save_csv(file_path: Path, data: List[Dict[str, Any]], fieldnames: Optional[List[str]] = None):
    """
    Save data to CSV file.
    
    Args:
        file_path: Target file path
        data: List of dictionaries to save
        fieldnames: Optional list of field names (auto-detected if None)
        
    Raises:
        FileOperationError: If save fails
    """
    try:
        if not data:
            raise FileOperationError("No data to save to CSV")
        
        # Auto-detect fieldnames if not provided
        if fieldnames is None:
            fieldnames = list(data[0].keys())
        
        # Write to temporary file
        temp_fd, temp_path = tempfile.mkstemp(
            dir=file_path.parent,
            prefix=f".{file_path.name}.",
            suffix=".tmp"
        )
        
        try:
            with open(temp_fd, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                writer.writerows(data)
            
            # Atomic rename
            shutil.move(temp_path, file_path)
            logger.debug(f"Successfully wrote CSV to {file_path}")
        except Exception as e:
            # Clean up temp file on error
            try:
                Path(temp_path).unlink(missing_ok=True)
            except:
                pass
            raise e
    except Exception as e:
        raise FileOperationError(f"Failed to save CSV to {file_path}: {e}")


def ensure_directory(directory: Path):
    """
    Ensure directory exists, create if necessary.
    
    Args:
        directory: Directory path
        
    Raises:
        FileOperationError: If directory creation fails
    """
    try:
        directory.mkdir(parents=True, exist_ok=True)
    except Exception as e:
        raise FileOperationError(f"Failed to create directory {directory}: {e}")


def list_files(directory: Path, pattern: str = "*.txt") -> List[Path]:
    """
    List files in directory matching pattern.
    
    Args:
        directory: Directory to search
        pattern: Glob pattern
        
    Returns:
        List of matching file paths
        
    Raises:
        FileOperationError: If listing fails
    """
    try:
        if not directory.exists():
            return []
        return sorted(directory.glob(pattern))
    except Exception as e:
        raise FileOperationError(f"Failed to list files in {directory}: {e}")
