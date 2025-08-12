#!/usr/bin/env python3
"""
Simple test script to verify PDF processing functionality
"""

import sys
import os
import logging

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_pdf_imports():
    """Test if PDF processing imports work"""
    try:
        from services.pdf_processor_service import PDFProcessorService
        logger.info("✅ PDF processor service imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import PDF processor service: {e}")
        return False

def test_pdf_endpoints():
    """Test if PDF endpoints can be imported"""
    try:
        from api.pdf_upload_endpoints import router as pdf_router
        logger.info("✅ PDF endpoints imported successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to import PDF endpoints: {e}")
        return False

def test_pdf_service_creation():
    """Test if PDF service can be created"""
    try:
        from services.pdf_processor_service import PDFProcessorService
        service = PDFProcessorService()
        logger.info("✅ PDF processor service created successfully")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to create PDF processor service: {e}")
        return False

def main():
    """Run all tests"""
    logger.info("🧪 Starting PDF processing tests...")
    
    tests = [
        ("PDF Imports", test_pdf_imports),
        ("PDF Endpoints", test_pdf_endpoints),
        ("PDF Service Creation", test_pdf_service_creation),
    ]
    
    results = []
    for test_name, test_func in tests:
        logger.info(f"🔍 Running test: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
            if result:
                logger.info(f"✅ {test_name}: PASSED")
            else:
                logger.error(f"❌ {test_name}: FAILED")
        except Exception as e:
            logger.error(f"❌ {test_name}: FAILED with exception: {e}")
            results.append((test_name, False))
    
    # Summary
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    logger.info(f"\n📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        logger.info("🎉 All tests passed! PDF processing should work.")
        return True
    else:
        logger.error("💥 Some tests failed. PDF processing may have issues.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)