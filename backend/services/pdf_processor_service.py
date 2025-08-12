"""
PDF Processing Service for Financial Data Extraction
===================================================

Service to extract and parse financial data from uploaded PDF documents.
Supports bank statements, investment reports, and other financial documents.
"""

import io
import os
import re
import logging
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import tempfile

# Text processing
import json
from dataclasses import dataclass

# Initialize logger first
logger = logging.getLogger(__name__)

# PDF Processing imports with graceful fallback
try:
    import PyPDF2
    PYPDF2_AVAILABLE = True
except ImportError:
    PYPDF2_AVAILABLE = False
    logger.warning("PyPDF2 not available - some PDF features may be limited")

try:
    import pdfplumber
    PDFPLUMBER_AVAILABLE = True
except ImportError:
    PDFPLUMBER_AVAILABLE = False
    logger.warning("pdfplumber not available - some PDF features may be limited")

try:
    from PIL import Image
    import pytesseract
    OCR_AVAILABLE = True
except ImportError:
    OCR_AVAILABLE = False
    logger.warning("OCR dependencies not available - scanned PDF support limited")

@dataclass
class FinancialTransaction:
    """Represents a financial transaction extracted from PDF"""
    date: str
    description: str
    amount: float
    transaction_type: str  # 'debit', 'credit', 'investment'
    category: str = 'unknown'
    account: str = 'unknown'

@dataclass
class FinancialAccount:
    """Represents a financial account from PDF"""
    account_number: str
    account_type: str  # 'savings', 'current', 'investment', 'credit_card'
    balance: float
    bank_name: str = 'unknown'
    currency: str = 'INR'

@dataclass
class ExtractedFinancialData:
    """Container for all extracted financial data"""
    document_type: str
    extraction_date: str
    accounts: List[FinancialAccount]
    transactions: List[FinancialTransaction]
    summary: Dict[str, Any]
    raw_text: str
    confidence_score: float


class PDFProcessorService:
    """Service for processing uploaded PDF financial documents"""
    
    def __init__(self):
        """Initialize PDF processor service"""
        self.supported_formats = ['pdf']
        self.max_file_size = 10 * 1024 * 1024  # 10MB limit
        logger.info("✅ PDF Processor Service initialized")
    
    async def process_financial_pdf(self, file_content: bytes, filename: str) -> Dict[str, Any]:
        """
        Process uploaded financial PDF and extract data
        """
        try:
            logger.info(f"📄 Processing financial PDF: {filename}")
            
            # Validate file
            if len(file_content) > self.max_file_size:
                return {
                    "success": False,
                    "message": f"File too large. Maximum size is {self.max_file_size // (1024*1024)}MB"
                }
            
            # Extract text from PDF
            extracted_data = await self._extract_pdf_data(file_content, filename)
            
            if not extracted_data:
                return {
                    "success": False,
                    "message": "Failed to extract data from PDF"
                }
            
            # Parse financial data
            financial_data = self._parse_financial_data(extracted_data)
            
            # Generate insights
            insights = self._generate_financial_insights(financial_data)
            
            return {
                "success": True,
                "filename": filename,
                "document_type": financial_data.document_type,
                "extraction_date": financial_data.extraction_date,
                "accounts": [self._account_to_dict(acc) for acc in financial_data.accounts],
                "transactions": [self._transaction_to_dict(txn) for txn in financial_data.transactions],
                "summary": financial_data.summary,
                "insights": insights,
                "confidence_score": financial_data.confidence_score,
                "message": f"Successfully extracted {len(financial_data.transactions)} transactions from {len(financial_data.accounts)} accounts"
            }
            
        except Exception as e:
            logger.error(f"❌ Failed to process PDF {filename}: {e}")
            return {
                "success": False,
                "message": f"PDF processing failed: {str(e)}"
            }
    
    async def _extract_pdf_data(self, file_content: bytes, filename: str) -> Optional[str]:
        """Extract text from PDF using multiple methods"""
        try:
            text_content = ""
            
            # Method 1: Try pdfplumber first (better for tables)
            if PDFPLUMBER_AVAILABLE:
                with io.BytesIO(file_content) as pdf_buffer:
                    try:
                        with pdfplumber.open(pdf_buffer) as pdf:
                            logger.info(f"📊 PDF has {len(pdf.pages)} pages")
                            
                            for page_num, page in enumerate(pdf.pages):
                                page_text = page.extract_text()
                                if page_text:
                                    text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                                
                                # Extract tables if present
                                tables = page.extract_tables()
                                for table_num, table in enumerate(tables):
                                    text_content += f"\n--- Table {table_num + 1} on Page {page_num + 1} ---\n"
                                    for row in table:
                                        if row:
                                            text_content += " | ".join([cell or "" for cell in row]) + "\n"
                        
                        if text_content.strip():
                            logger.info(f"✅ Extracted {len(text_content)} characters using pdfplumber")
                            return text_content
                            
                    except Exception as e:
                        logger.warning(f"⚠️ pdfplumber extraction failed: {e}")
            
            # Method 2: Fallback to PyPDF2
            if PYPDF2_AVAILABLE:
                with io.BytesIO(file_content) as pdf_buffer:
                    try:
                        reader = PyPDF2.PdfReader(pdf_buffer)
                        text_content = ""
                        
                        for page_num, page in enumerate(reader.pages):
                            page_text = page.extract_text()
                            if page_text:
                                text_content += f"\n--- Page {page_num + 1} ---\n{page_text}\n"
                        
                        if text_content.strip():
                            logger.info(f"✅ Extracted {len(text_content)} characters using PyPDF2")
                            return text_content
                            
                    except Exception as e:
                        logger.warning(f"⚠️ PyPDF2 extraction failed: {e}")
            
            # Method 3: OCR as last resort (for scanned PDFs)
            if OCR_AVAILABLE:
                logger.info("🔍 Attempting OCR extraction for scanned PDF...")
                return await self._extract_with_ocr(file_content)
            else:
                # Return a basic text extraction message if no libraries are available
                return f"PDF processing libraries not fully available. Please install: pip install pdfplumber PyPDF2 pytesseract Pillow"
            
        except Exception as e:
            logger.error(f"❌ PDF text extraction failed: {e}")
            return None
    
    async def _extract_with_ocr(self, file_content: bytes) -> Optional[str]:
        """Extract text using OCR for scanned PDFs"""
        if not OCR_AVAILABLE:
            logger.warning("⚠️ OCR libraries not available")
            return None
            
        try:
            # Convert PDF to images
            with io.BytesIO(file_content) as pdf_buffer:
                # Use PyPDF2 to get page count first if available
                if PYPDF2_AVAILABLE:
                    reader = PyPDF2.PdfReader(pdf_buffer)
                    page_count = len(reader.pages)
                    logger.info(f"🔍 Starting OCR for {page_count} pages...")
                
                # Convert PDF pages to images using pdf2image
                try:
                    from pdf2image import convert_from_bytes
                    images = convert_from_bytes(file_content)
                except ImportError:
                    logger.warning("⚠️ pdf2image not available for OCR")
                    return None
                
                extracted_text = ""
                for i, image in enumerate(images):
                    logger.info(f"🔍 Processing page {i+1}/{len(images)} with OCR...")
                    
                    # Convert PIL image to text using pytesseract
                    page_text = pytesseract.image_to_string(image, lang='eng')
                    if page_text.strip():
                        extracted_text += f"\n--- Page {i+1} (OCR) ---\n{page_text}\n"
                
                if extracted_text.strip():
                    logger.info(f"✅ OCR extracted {len(extracted_text)} characters")
                    return extracted_text
                else:
                    logger.warning("⚠️ OCR extraction returned no text")
                    return None
                    
        except Exception as e:
            logger.error(f"❌ OCR extraction failed: {e}")
            return None
    
    def _parse_financial_data(self, raw_text: str) -> ExtractedFinancialData:
        """Parse extracted text to identify financial data"""
        try:
            # Detect document type
            document_type = self._detect_document_type(raw_text)
            
            # Extract accounts
            accounts = self._extract_accounts(raw_text)
            
            # Extract transactions
            transactions = self._extract_transactions(raw_text)
            
            # Generate summary
            summary = self._generate_summary(accounts, transactions)
            
            # Calculate confidence score
            confidence_score = self._calculate_confidence_score(raw_text, accounts, transactions)
            
            return ExtractedFinancialData(
                document_type=document_type,
                extraction_date=datetime.now().isoformat(),
                accounts=accounts,
                transactions=transactions,
                summary=summary,
                raw_text=raw_text[:1000],  # Store first 1000 chars for reference
                confidence_score=confidence_score
            )
            
        except Exception as e:
            logger.error(f"❌ Financial data parsing failed: {e}")
            # Return empty data structure
            return ExtractedFinancialData(
                document_type="unknown",
                extraction_date=datetime.now().isoformat(),
                accounts=[],
                transactions=[],
                summary={},
                raw_text=raw_text[:1000],
                confidence_score=0.0
            )
    
    def _detect_document_type(self, text: str) -> str:
        """Detect the type of financial document"""
        text_lower = text.lower()
        
        # Bank statement patterns
        if any(keyword in text_lower for keyword in ['bank statement', 'account statement', 'transaction history']):
            return 'bank_statement'
        
        # Investment report patterns
        elif any(keyword in text_lower for keyword in ['portfolio', 'mutual fund', 'investment report', 'sip']):
            return 'investment_report'
        
        # Credit card statement
        elif any(keyword in text_lower for keyword in ['credit card', 'card statement', 'outstanding amount']):
            return 'credit_card_statement'
        
        # EPF statement
        elif any(keyword in text_lower for keyword in ['epf', 'provident fund', 'employee provident fund']):
            return 'epf_statement'
        
        # Insurance document
        elif any(keyword in text_lower for keyword in ['insurance', 'policy', 'premium']):
            return 'insurance_document'
        
        else:
            return 'financial_document'
    
    def _extract_accounts(self, text: str) -> List[FinancialAccount]:
        """Extract account information from text"""
        accounts = []
        
        try:
            # Pattern for account numbers (various formats)
            account_patterns = [
                r'account\s*(?:no|number)[:\s]*(\d{10,18})',  # Account No: 1234567890
                r'a/c\s*(?:no)?[:\s]*(\d{10,18})',           # A/C: 1234567890
                r'account[:\s]+(\d{10,18})',                  # Account: 1234567890
            ]
            
            # Pattern for balance
            balance_patterns = [
                r'balance[:\s]*(?:rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'available\s*balance[:\s]*(?:rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
                r'closing\s*balance[:\s]*(?:rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            ]
            
            # Bank name patterns
            bank_patterns = [
                r'(state bank of india|sbi)',
                r'(hdfc bank|hdfc)',
                r'(icici bank|icici)',
                r'(axis bank|axis)',
                r'(kotak mahindra|kotak)',
                r'(punjab national bank|pnb)',
            ]
            
            # Extract account numbers
            found_accounts = set()
            for pattern in account_patterns:
                matches = re.finditer(pattern, text, re.IGNORECASE)
                for match in matches:
                    account_number = match.group(1)
                    if account_number not in found_accounts:
                        found_accounts.add(account_number)
                        
                        # Try to find balance for this account
                        balance = 0.0
                        for balance_pattern in balance_patterns:
                            balance_match = re.search(balance_pattern, text[max(0, match.start()-200):match.end()+200], re.IGNORECASE)
                            if balance_match:
                                balance_str = balance_match.group(1).replace(',', '')
                                balance = float(balance_str)
                                break
                        
                        # Try to find bank name
                        bank_name = 'unknown'
                        for bank_pattern in bank_patterns:
                            bank_match = re.search(bank_pattern, text, re.IGNORECASE)
                            if bank_match:
                                bank_name = bank_match.group(1)
                                break
                        
                        accounts.append(FinancialAccount(
                            account_number=account_number,
                            account_type='savings',  # Default, could be improved with more detection
                            balance=balance,
                            bank_name=bank_name,
                            currency='INR'
                        ))
            
            logger.info(f"📊 Extracted {len(accounts)} accounts")
            return accounts
            
        except Exception as e:
            logger.error(f"❌ Account extraction failed: {e}")
            return []
    
    def _extract_transactions(self, text: str) -> List[FinancialTransaction]:
        """Extract transaction data from text"""
        transactions = []
        
        try:
            # Transaction patterns (Indian format)
            transaction_patterns = [
                # Date | Description | Debit | Credit | Balance
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+(?:Dr\.?\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)\s*(?:Cr\.?)?',
                # Date Description Amount
                r'(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})\s+(.+?)\s+(?:Rs\.?\s*|₹\s*)?(\d+(?:,\d{3})*(?:\.\d{2})?)',
            ]
            
            # Split text into lines for processing
            lines = text.split('\n')
            
            for line in lines:
                line = line.strip()
                if not line or len(line) < 20:  # Skip short lines
                    continue
                
                for pattern in transaction_patterns:
                    match = re.search(pattern, line, re.IGNORECASE)
                    if match:
                        try:
                            date_str = match.group(1)
                            description = match.group(2).strip()
                            amount_str = match.group(3).replace(',', '')
                            amount = float(amount_str)
                            
                            # Determine transaction type
                            transaction_type = 'debit'
                            if any(keyword in line.lower() for keyword in ['credit', 'cr', 'deposit']):
                                transaction_type = 'credit'
                            elif any(keyword in line.lower() for keyword in ['sip', 'investment', 'mutual fund']):
                                transaction_type = 'investment'
                            
                            # Categorize transaction
                            category = self._categorize_transaction(description)
                            
                            transactions.append(FinancialTransaction(
                                date=date_str,
                                description=description[:100],  # Limit description length
                                amount=amount,
                                transaction_type=transaction_type,
                                category=category
                            ))
                            
                        except (ValueError, IndexError) as e:
                            continue  # Skip invalid transactions
            
            logger.info(f"📊 Extracted {len(transactions)} transactions")
            return transactions[:50]  # Limit to 50 transactions to prevent overflow
            
        except Exception as e:
            logger.error(f"❌ Transaction extraction failed: {e}")
            return []
    
    def _categorize_transaction(self, description: str) -> str:
        """Categorize transaction based on description"""
        description_lower = description.lower()
        
        if any(keyword in description_lower for keyword in ['salary', 'pay', 'wage']):
            return 'income'
        elif any(keyword in description_lower for keyword in ['grocery', 'food', 'restaurant']):
            return 'food'
        elif any(keyword in description_lower for keyword in ['fuel', 'petrol', 'diesel', 'gas']):
            return 'fuel'
        elif any(keyword in description_lower for keyword in ['medical', 'doctor', 'hospital', 'pharmacy']):
            return 'healthcare'
        elif any(keyword in description_lower for keyword in ['sip', 'mutual fund', 'investment']):
            return 'investment'
        elif any(keyword in description_lower for keyword in ['emi', 'loan', 'repay']):
            return 'loan'
        elif any(keyword in description_lower for keyword in ['electricity', 'water', 'gas', 'internet']):
            return 'utilities'
        else:
            return 'others'
    
    def _generate_summary(self, accounts: List[FinancialAccount], transactions: List[FinancialTransaction]) -> Dict[str, Any]:
        """Generate summary statistics from extracted data"""
        try:
            total_balance = sum(acc.balance for acc in accounts)
            total_transactions = len(transactions)
            
            # Calculate totals by type
            credits = [txn for txn in transactions if txn.transaction_type == 'credit']
            debits = [txn for txn in transactions if txn.transaction_type == 'debit']
            investments = [txn for txn in transactions if txn.transaction_type == 'investment']
            
            total_credits = sum(txn.amount for txn in credits)
            total_debits = sum(txn.amount for txn in debits)
            total_investments = sum(txn.amount for txn in investments)
            
            # Category breakdown
            categories = {}
            for txn in transactions:
                if txn.category in categories:
                    categories[txn.category] += txn.amount
                else:
                    categories[txn.category] = txn.amount
            
            return {
                'total_accounts': len(accounts),
                'total_balance': total_balance,
                'total_transactions': total_transactions,
                'total_credits': total_credits,
                'total_debits': total_debits,
                'total_investments': total_investments,
                'category_breakdown': categories,
                'net_flow': total_credits - total_debits
            }
            
        except Exception as e:
            logger.error(f"❌ Summary generation failed: {e}")
            return {}
    
    def _calculate_confidence_score(self, raw_text: str, accounts: List[FinancialAccount], transactions: List[FinancialTransaction]) -> float:
        """Calculate confidence score based on extraction quality"""
        try:
            score = 0.0
            
            # Base score for successful extraction
            if accounts or transactions:
                score += 0.3
            
            # Account detection bonus
            if accounts:
                score += min(0.3, len(accounts) * 0.1)
            
            # Transaction detection bonus
            if transactions:
                score += min(0.3, len(transactions) * 0.01)
            
            # Text quality indicators
            if len(raw_text) > 1000:
                score += 0.1
            
            # Financial keywords presence
            financial_keywords = ['balance', 'transaction', 'account', 'amount', 'date', 'bank']
            keyword_count = sum(1 for keyword in financial_keywords if keyword in raw_text.lower())
            score += min(0.1, keyword_count * 0.02)
            
            return min(1.0, score)  # Cap at 1.0
            
        except Exception as e:
            logger.error(f"❌ Confidence calculation failed: {e}")
            return 0.0
    
    def _generate_financial_insights(self, financial_data: ExtractedFinancialData) -> List[Dict[str, str]]:
        """Generate insights based on extracted financial data"""
        insights = []
        
        try:
            summary = financial_data.summary
            
            # Account insights
            if summary.get('total_accounts', 0) > 0:
                insights.append({
                    'type': 'account_summary',
                    'title': 'Account Overview',
                    'insight': f"Found {summary['total_accounts']} accounts with total balance of ₹{summary.get('total_balance', 0):,.2f}"
                })
            
            # Transaction insights
            if summary.get('total_transactions', 0) > 0:
                insights.append({
                    'type': 'transaction_summary',
                    'title': 'Transaction Analysis',
                    'insight': f"Analyzed {summary['total_transactions']} transactions with net flow of ₹{summary.get('net_flow', 0):,.2f}"
                })
            
            # Spending pattern insights
            categories = summary.get('category_breakdown', {})
            if categories:
                top_category = max(categories.items(), key=lambda x: x[1])
                insights.append({
                    'type': 'spending_pattern',
                    'title': 'Top Spending Category',
                    'insight': f"Highest spending in '{top_category[0]}' category: ₹{top_category[1]:,.2f}"
                })
            
            # Investment insights
            if summary.get('total_investments', 0) > 0:
                insights.append({
                    'type': 'investment',
                    'title': 'Investment Activity',
                    'insight': f"Total investments: ₹{summary['total_investments']:,.2f}"
                })
            
            return insights
            
        except Exception as e:
            logger.error(f"❌ Insight generation failed: {e}")
            return []
    
    def _account_to_dict(self, account: FinancialAccount) -> Dict[str, Any]:
        """Convert FinancialAccount to dictionary"""
        return {
            'account_number': account.account_number,
            'account_type': account.account_type,
            'balance': account.balance,
            'bank_name': account.bank_name,
            'currency': account.currency
        }
    
    def _transaction_to_dict(self, transaction: FinancialTransaction) -> Dict[str, Any]:
        """Convert FinancialTransaction to dictionary"""
        return {
            'date': transaction.date,
            'description': transaction.description,
            'amount': transaction.amount,
            'transaction_type': transaction.transaction_type,
            'category': transaction.category,
            'account': transaction.account
        }


# Service instance
pdf_processor_service = PDFProcessorService()

def get_pdf_processor_service() -> PDFProcessorService:
    """Get PDF processor service instance"""
    return pdf_processor_service