"""
PDF Upload and Processing API Endpoints for Artha AI
===================================================

FastAPI endpoints for uploading and processing financial PDF documents.
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File, Form
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
import logging
import io

from services.pdf_processor_service import get_pdf_processor_service, PDFProcessorService

logger = logging.getLogger(__name__)

# Create router
router = APIRouter(prefix="/api/pdf", tags=["pdf-upload"])

# Pydantic models for request/response
class PDFUploadResponse(BaseModel):
    success: bool
    message: str
    filename: Optional[str] = None
    document_type: Optional[str] = None
    extraction_date: Optional[str] = None
    accounts: Optional[List[Dict[str, Any]]] = None
    transactions: Optional[List[Dict[str, Any]]] = None
    summary: Optional[Dict[str, Any]] = None
    insights: Optional[List[Dict[str, str]]] = None
    confidence_score: Optional[float] = None

class PDFAnalysisRequest(BaseModel):
    analysis_type: str = "comprehensive"  # comprehensive, summary, insights_only
    user_query: Optional[str] = None

@router.post("/upload", response_model=PDFUploadResponse)
async def upload_financial_pdf(
    file: UploadFile = File(...),
    analysis_type: str = Form("comprehensive"),
    user_query: str = Form(None)
):
    """
    Upload and process a financial PDF document
    """
    try:
        logger.info(f"📄 Receiving PDF upload: {file.filename}")
        
        # Validate file type
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(
                status_code=400,
                detail="Only PDF files are supported"
            )
        
        # Validate file size (10MB limit)
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:  # 10MB
            raise HTTPException(
                status_code=400,
                detail="File size exceeds 10MB limit"
            )
        
        # Process the PDF
        pdf_processor = get_pdf_processor_service()
        result = await pdf_processor.process_financial_pdf(file_content, file.filename)
        
        if not result['success']:
            raise HTTPException(
                status_code=400,
                detail=result['message']
            )
        
        # Return processed data
        return PDFUploadResponse(
            success=True,
            message=result['message'],
            filename=result['filename'],
            document_type=result['document_type'],
            extraction_date=result['extraction_date'],
            accounts=result['accounts'],
            transactions=result['transactions'],
            summary=result['summary'],
            insights=result['insights'],
            confidence_score=result['confidence_score']
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ PDF upload failed: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF processing failed: {str(e)}"
        )

@router.post("/analyze-with-ai")
async def analyze_pdf_with_ai(
    file: UploadFile = File(...),
    user_query: str = Form("Analyze my financial data and provide insights")
):
    """
    Upload PDF and get AI-powered financial analysis
    """
    try:
        logger.info(f"🤖 AI analysis requested for: {file.filename}")
        
        # Validate file
        if not file.filename.lower().endswith('.pdf'):
            raise HTTPException(status_code=400, detail="Only PDF files are supported")
        
        file_content = await file.read()
        if len(file_content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        # Process PDF
        pdf_processor = get_pdf_processor_service()
        extraction_result = await pdf_processor.process_financial_pdf(file_content, file.filename)
        
        if not extraction_result['success']:
            raise HTTPException(status_code=400, detail=extraction_result['message'])
        
        # Generate AI analysis using the existing AI system
        ai_analysis = await generate_ai_financial_analysis(extraction_result, user_query)
        
        return {
            "success": True,
            "filename": file.filename,
            "extraction_summary": {
                "document_type": extraction_result['document_type'],
                "accounts_found": len(extraction_result['accounts']),
                "transactions_found": len(extraction_result['transactions']),
                "confidence_score": extraction_result['confidence_score']
            },
            "ai_analysis": ai_analysis,
            "extracted_data": {
                "accounts": extraction_result['accounts'][:3],  # Show first 3 accounts
                "recent_transactions": extraction_result['transactions'][:10],  # Show first 10 transactions
                "summary": extraction_result['summary']
            }
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ AI analysis failed: {e}")
        raise HTTPException(status_code=500, detail=f"AI analysis failed: {str(e)}")

@router.post("/batch-upload")
async def upload_multiple_pdfs(
    files: List[UploadFile] = File(...),
    analysis_type: str = Form("comprehensive")
):
    """
    Upload and process multiple financial PDF documents
    """
    try:
        if len(files) > 5:  # Limit to 5 files
            raise HTTPException(
                status_code=400,
                detail="Maximum 5 files allowed per batch"
            )
        
        results = []
        pdf_processor = get_pdf_processor_service()
        
        for file in files:
            logger.info(f"📄 Processing batch file: {file.filename}")
            
            if not file.filename.lower().endswith('.pdf'):
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": "Invalid file type - only PDF files are supported"
                })
                continue
            
            file_content = await file.read()
            if len(file_content) > 10 * 1024 * 1024:
                results.append({
                    "filename": file.filename,
                    "success": False,
                    "message": "File size exceeds 10MB limit"
                })
                continue
            
            # Process the PDF
            result = await pdf_processor.process_financial_pdf(file_content, file.filename)
            results.append(result)
        
        # Generate batch summary
        successful_files = [r for r in results if r['success']]
        total_accounts = sum(len(r.get('accounts', [])) for r in successful_files)
        total_transactions = sum(len(r.get('transactions', [])) for r in successful_files)
        
        return {
            "success": True,
            "message": f"Processed {len(successful_files)}/{len(files)} files successfully",
            "batch_summary": {
                "total_files": len(files),
                "successful_files": len(successful_files),
                "failed_files": len(files) - len(successful_files),
                "total_accounts_extracted": total_accounts,
                "total_transactions_extracted": total_transactions
            },
            "file_results": results
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"❌ Batch upload failed: {e}")
        raise HTTPException(status_code=500, detail=f"Batch upload failed: {str(e)}")

@router.get("/supported-formats")
async def get_supported_formats():
    """
    Get information about supported PDF formats and document types
    """
    return {
        "supported_file_types": [".pdf"],
        "max_file_size_mb": 10,
        "supported_document_types": [
            "Bank Statements",
            "Investment Reports",
            "Credit Card Statements", 
            "EPF Statements",
            "Insurance Documents",
            "Mutual Fund Statements",
            "Loan Statements"
        ],
        "extraction_capabilities": [
            "Account balances and details",
            "Transaction history with categorization",
            "Investment portfolio data",
            "Income and expense analysis",
            "Financial summary statistics",
            "AI-powered insights and recommendations"
        ],
        "languages_supported": ["English", "Hindi (limited)"],
        "accuracy_note": "Best results with machine-readable PDFs. Scanned documents may have lower accuracy."
    }

@router.get("/processing-status")
async def get_processing_status():
    """
    Get PDF processing service status
    """
    try:
        pdf_processor = get_pdf_processor_service()
        
        return {
            "status": "active",
            "service": "PDF Financial Data Processor",
            "capabilities": [
                "Text extraction from PDF documents",
                "Financial data parsing and categorization", 
                "Account and transaction detection",
                "AI-powered financial insights",
                "Multi-document batch processing"
            ],
            "supported_formats": pdf_processor.supported_formats,
            "max_file_size_mb": pdf_processor.max_file_size // (1024 * 1024),
            "timestamp": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"❌ PDF processor status check failed: {e}")
        return {
            "status": "error",
            "message": "PDF processor service unavailable"
        }

async def generate_ai_financial_analysis(extraction_result: Dict[str, Any], user_query: str) -> str:
    """
    Generate AI analysis of extracted financial data
    """
    try:
        # Import AI components
        from main import ArthaAIChatbot
        from google import genai
        import os
        
        # Initialize Gemini client
        api_key = os.getenv('GOOGLE_API_KEY')
        if not api_key:
            return "AI analysis unavailable - Google API key not configured"
        
        client = genai.Client(api_key=api_key)
        
        # Prepare financial data summary for AI with validation
        accounts_data = extraction_result.get('accounts', [])
        transactions_data = extraction_result.get('transactions', [])
        summary_data = extraction_result.get('summary', {})
        confidence = extraction_result.get('confidence_score', 0.0)
        
        data_summary = f"""
        EXTRACTED DOCUMENT DATA:
        - Document Type: {extraction_result.get('document_type', 'Unknown')}
        - Data Extraction Confidence: {confidence:.2f} {'(LOW - Data may be unreliable)' if confidence < 0.8 else '(Good)'}
        - Accounts Found: {len(accounts_data)}
        - Transactions Found: {len(transactions_data)}
        
        ACCOUNT DETAILS (if any):
        {format_accounts_for_ai(accounts_data)}
        
        TRANSACTION DETAILS (if any):
        {format_transactions_for_ai(transactions_data)}
        
        FINANCIAL SUMMARY (if available):
        {format_summary_for_ai(summary_data)}
        
        DATA QUALITY NOTES:
        - Confidence Score: {confidence:.2f}/1.0
        - Missing or unclear data should be explicitly mentioned
        - Only the above data was extracted from the document
        """
        
        # AI prompt for financial analysis with strict fact-checking
        prompt = f"""
        You are a financial advisor analyzing uploaded financial documents. You MUST be extremely accurate and only use the exact data provided.
        
        CRITICAL INSTRUCTIONS:
        - ONLY analyze the data that is explicitly provided below
        - DO NOT make assumptions or add information not present in the extracted data
        - If data is missing or unclear, explicitly state "Data not available" or "Cannot determine from provided information"
        - DO NOT hallucinate financial figures, account details, or transaction information
        - If the confidence score is low, mention data quality concerns
        
        User Query: {user_query}
        
        ACTUAL EXTRACTED DATA (confidence: {extraction_result['confidence_score']:.2f}):
        {data_summary}
        
        Please provide an analysis that:
        1. States exactly what data was found in the document
        2. Identifies any data quality issues or gaps
        3. Provides insights ONLY based on the actual extracted data
        4. Clearly distinguishes between facts from the document vs. general recommendations
        5. Warns if the data appears incomplete or unreliable
        
        Start your response by confirming what specific data was extracted from the document.
        If the confidence score is below 0.8, mention potential data extraction issues.
        """
        
        # Generate AI response using Gemini 2.5 Pro for advanced PDF analysis
        response = client.models.generate_content(
            model="gemini-2.5-pro",
            contents=prompt
        )
        
        return response.text if response.text else "Unable to generate analysis at this time"
        
    except Exception as e:
        logger.error(f"❌ AI analysis generation failed: {e}")
        return f"AI analysis unavailable: {str(e)}"

def format_accounts_for_ai(accounts: List[Dict[str, Any]]) -> str:
    """Format account data for AI analysis"""
    if not accounts:
        return "No account information was extracted from the document"
    
    formatted = []
    for i, acc in enumerate(accounts[:5], 1):  # Limit to 5 accounts
        account_num = acc.get('account_number', 'Not found')
        bank_name = acc.get('bank_name', 'Not specified')
        balance = acc.get('balance', 'Not available')
        
        if account_num != 'Not found' and len(str(account_num)) > 4:
            account_display = f"****{str(account_num)[-4:]}"
        else:
            account_display = account_num
            
        if isinstance(balance, (int, float)):
            balance_display = f"₹{balance:,.2f}"
        else:
            balance_display = str(balance)
            
        formatted.append(f"Account {i}: {account_display} at {bank_name} - Balance: {balance_display}")
    
    return "\n".join(formatted)

def format_transactions_for_ai(transactions: List[Dict[str, Any]]) -> str:
    """Format transaction data for AI analysis"""
    if not transactions:
        return "No transaction data was extracted from the document"
    
    formatted = []
    for i, txn in enumerate(transactions[:10], 1):  # Limit to 10 transactions
        date = txn.get('date', 'Date not found')
        description = txn.get('description', 'Description not available')
        amount = txn.get('amount', 'Amount not available')
        txn_type = txn.get('transaction_type', 'Type not specified')
        
        # Truncate description if too long
        if isinstance(description, str) and len(description) > 50:
            description = description[:47] + "..."
            
        # Format amount properly
        if isinstance(amount, (int, float)):
            amount_display = f"₹{amount:,.2f}"
        else:
            amount_display = str(amount)
            
        formatted.append(f"{i}. {date}: {description} - {amount_display} ({txn_type})")
    
    if len(transactions) > 10:
        formatted.append(f"... and {len(transactions) - 10} more transactions")
    
    return "\n".join(formatted)

def format_summary_for_ai(summary: Dict[str, Any]) -> str:
    """Format summary data for AI analysis"""
    if not summary:
        return "No financial summary was extracted from the document"
    
    formatted_lines = []
    
    # Format each summary item with proper validation
    total_balance = summary.get('total_balance')
    if total_balance is not None and isinstance(total_balance, (int, float)):
        formatted_lines.append(f"- Total Balance: ₹{total_balance:,.2f}")
    else:
        formatted_lines.append("- Total Balance: Not available in document")
    
    total_credits = summary.get('total_credits')
    if total_credits is not None and isinstance(total_credits, (int, float)):
        formatted_lines.append(f"- Total Credits: ₹{total_credits:,.2f}")
    else:
        formatted_lines.append("- Total Credits: Not available in document")
    
    total_debits = summary.get('total_debits')
    if total_debits is not None and isinstance(total_debits, (int, float)):
        formatted_lines.append(f"- Total Debits: ₹{total_debits:,.2f}")
    else:
        formatted_lines.append("- Total Debits: Not available in document")
    
    net_flow = summary.get('net_flow')
    if net_flow is not None and isinstance(net_flow, (int, float)):
        formatted_lines.append(f"- Net Flow: ₹{net_flow:,.2f}")
    else:
        formatted_lines.append("- Net Flow: Not available in document")
    
    # Handle category breakdown
    category_breakdown = summary.get('category_breakdown', {})
    if category_breakdown and isinstance(category_breakdown, dict):
        top_categories = dict(list(category_breakdown.items())[:3])
        formatted_lines.append(f"- Top Spending Categories: {top_categories}")
    else:
        formatted_lines.append("- Category Breakdown: Not available in document")
    
    return "\n".join(formatted_lines)