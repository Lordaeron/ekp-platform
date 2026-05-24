"""Test cases for KnowledgePlatform core functionality"""

import pandas as pd
import tempfile
from pathlib import Path
from ekp_platform.core.platform import KnowledgePlatform


def test_platform_initialization():
    """Test that KnowledgePlatform initializes correctly"""
    ekp = KnowledgePlatform()
    assert len(ekp.datasources) == 0
    assert len(ekp.metadata) == 0
    assert ekp.__repr__() == "KnowledgePlatform(datasources=0, status=active)"


def test_load_table():
    """Test loading table files functionality"""
    # Create a sample CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("name,age,salary\n")
        f.write("Alice,30,100000\n")
        f.write("Bob,25,80000\n")
        f.write("Charlie,35,120000\n")
        temp_path = Path(f.name)

    try:
        ekp = KnowledgePlatform()
        df = ekp.load_table(temp_path)
        assert len(df) == 3
        assert list(df.columns) == ["name", "age", "salary"]

        # Check metadata
        metadata = ekp.metadata[temp_path.name]
        assert metadata["rows"] == 3
        assert "name" in metadata["dtypes"]
        assert metadata["null_values"]["name"] == 0
    finally:
        temp_path.unlink()


def test_datasource_management():
    """Test datasource adding and management functionality"""
    ekp = KnowledgePlatform()

    # Add file datasource
    ekp.add_file_datasource("/tmp/data", name="test_data")
    assert "test_data" in ekp.datasources
    assert ekp.datasources["test_data"]["type"] == "file"

    # Add database datasource
    ekp.add_database_datasource("mysql://user:pass@host/db", name="test_db")
    assert "test_db" in ekp.datasources
    assert ekp.datasources["test_db"]["type"] == "database"

    # Check summary
    summary = ekp.get_datasource_summary()
    assert summary["total_datasources"] == 2
    assert len(summary["datasources"]) == 2
