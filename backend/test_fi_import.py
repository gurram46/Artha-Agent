#!/usr/bin/env python3
"""
Test Fi Money MCP Client Import
"""

import sys
import os

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

print("Testing Fi Money MCP client import...")

try:
    from core.fi_mcp.production_client import get_user_financial_data, FinancialData
    print("✅ Fi Money MCP client imported successfully")
except ImportError as e:
    print(f"❌ Fi Money MCP client import failed: {e}")
    print(f"Error type: {type(e)}")
    print(f"Error args: {e.args}")
    
    # Try importing individual components
    try:
        import aiohttp
        print("✅ aiohttp imported successfully")
    except ImportError as aio_e:
        print(f"❌ aiohttp import failed: {aio_e}")
    
    try:
        from core.fi_mcp import production_client
        print("✅ production_client module imported successfully")
    except ImportError as pc_e:
        print(f"❌ production_client module import failed: {pc_e}")
        
    # Check if the file exists
    import os
    file_path = os.path.join(os.path.dirname(__file__), 'core', 'fi_mcp', 'production_client.py')
    if os.path.exists(file_path):
        print(f"✅ File exists: {file_path}")
    else:
        print(f"❌ File not found: {file_path}")

print("Test completed.")