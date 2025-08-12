"""
PDF Generation Service for Artha AI
==================================

Comprehensive PDF generation for portfolio reports, financial analysis, and chat conversations.
"""

import io
import os
import logging
from datetime import datetime, date
from typing import Dict, List, Any, Optional
import json

# PDF Generation imports
from reportlab.lib import colors
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, PageBreak, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.graphics.shapes import Drawing
from reportlab.graphics.charts.linecharts import HorizontalLineChart
from reportlab.graphics.charts.piecharts import Pie
from reportlab.lib.colors import HexColor

# Chart generation
import matplotlib
matplotlib.use('Agg')  # Use non-GUI backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from matplotlib.backends.backend_agg import FigureCanvasAgg
import numpy as np

logger = logging.getLogger(__name__)


class PDFGenerationService:
    """Service for generating various types of PDF reports"""
    
    def __init__(self):
        """Initialize PDF generation service"""
        self.styles = getSampleStyleSheet()
        self.setup_custom_styles()
        logger.info("✅ PDF Generation Service initialized")
    
    def setup_custom_styles(self):
        """Setup custom paragraph styles for reports"""
        self.custom_styles = {
            'title': ParagraphStyle(
                'CustomTitle',
                parent=self.styles['Title'],
                fontSize=24,
                textColor=HexColor('#00B899'),
                spaceAfter=30,
                alignment=1  # Center alignment
            ),
            'heading': ParagraphStyle(
                'CustomHeading',
                parent=self.styles['Heading1'],
                fontSize=16,
                textColor=HexColor('#2D3748'),
                spaceBefore=20,
                spaceAfter=12
            ),
            'subheading': ParagraphStyle(
                'CustomSubHeading',
                parent=self.styles['Heading2'],
                fontSize=14,
                textColor=HexColor('#4A5568'),
                spaceBefore=15,
                spaceAfter=8
            ),
            'body': ParagraphStyle(
                'CustomBody',
                parent=self.styles['Normal'],
                fontSize=11,
                textColor=HexColor('#2D3748'),
                spaceAfter=8,
                leftIndent=0,
                rightIndent=0
            ),
            'highlight': ParagraphStyle(
                'CustomHighlight',
                parent=self.styles['Normal'],
                fontSize=12,
                textColor=HexColor('#00B899'),
                spaceBefore=10,
                spaceAfter=10,
                leftIndent=20,
                rightIndent=20,
                backColor=HexColor('#F0FDF4'),
                borderColor=HexColor('#00B899'),
                borderWidth=1,
                borderPadding=10
            )
        }
    
    def generate_portfolio_report(self, user_data: Dict[str, Any], portfolio_data: Dict[str, Any], 
                                analytics_data: Dict[str, Any]) -> bytes:
        """Generate comprehensive portfolio PDF report"""
        try:
            logger.info("📄 Generating portfolio PDF report...")
            
            # Create PDF buffer
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            # Build content
            content = []
            
            # Add title and header
            content.extend(self._add_report_header("Portfolio Analysis Report", user_data))
            
            # Add portfolio summary
            content.extend(self._add_portfolio_summary(portfolio_data))
            
            # Add financial metrics
            content.extend(self._add_financial_metrics(analytics_data))
            
            # Add asset allocation chart
            if 'allocation' in analytics_data:
                content.extend(self._add_allocation_chart(analytics_data['allocation']))
            
            # Add performance analysis
            if 'growth' in analytics_data:
                content.extend(self._add_performance_analysis(analytics_data['growth']))
            
            # Add recommendations
            if 'insights' in analytics_data:
                content.extend(self._add_recommendations(analytics_data['insights']))
            
            # Add footer
            content.extend(self._add_report_footer())
            
            # Build PDF
            doc.build(content)
            
            # Get PDF data
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            logger.info("✅ Portfolio PDF report generated successfully")
            return pdf_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate portfolio PDF: {e}")
            raise
    
    def generate_chat_conversation_report(self, conversation_data: Dict[str, Any]) -> bytes:
        """Generate PDF report of chat conversation"""
        try:
            logger.info("📄 Generating chat conversation PDF report...")
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            content = []
            
            # Add title
            content.append(Paragraph("Artha AI Chat Conversation Report", self.custom_styles['title']))
            content.append(Spacer(1, 20))
            
            # Add conversation metadata
            metadata = conversation_data.get('metadata', {})
            content.append(Paragraph(f"Conversation Date: {metadata.get('date', 'N/A')}", self.custom_styles['body']))
            content.append(Paragraph(f"Duration: {metadata.get('duration', 'N/A')}", self.custom_styles['body']))
            content.append(Paragraph(f"Message Count: {len(conversation_data.get('messages', []))}", self.custom_styles['body']))
            content.append(Spacer(1, 20))
            
            # Add messages
            content.append(Paragraph("Conversation History", self.custom_styles['heading']))
            
            messages = conversation_data.get('messages', [])
            for i, message in enumerate(messages):
                sender = "You" if message.get('type') == 'user' else "Artha AI"
                timestamp = message.get('timestamp', 'Unknown time')
                
                content.append(Paragraph(f"<b>{sender}</b> - {timestamp}", self.custom_styles['subheading']))
                content.append(Paragraph(message.get('content', ''), self.custom_styles['body']))
                content.append(Spacer(1, 10))
                
                if i < len(messages) - 1:  # Add separator except for last message
                    content.append(Spacer(1, 5))
            
            content.extend(self._add_report_footer())
            
            doc.build(content)
            
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            logger.info("✅ Chat conversation PDF report generated successfully")
            return pdf_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate chat conversation PDF: {e}")
            raise
    
    def generate_financial_analysis_report(self, analysis_data: Dict[str, Any], 
                                         financial_data: Dict[str, Any]) -> bytes:
        """Generate comprehensive financial analysis PDF report"""
        try:
            logger.info("📄 Generating financial analysis PDF report...")
            
            buffer = io.BytesIO()
            doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=72, leftMargin=72, 
                                  topMargin=72, bottomMargin=18)
            
            content = []
            
            # Add title and header
            content.extend(self._add_report_header("Financial Analysis Report", {}))
            
            # Add executive summary
            if 'summary' in analysis_data:
                content.append(Paragraph("Executive Summary", self.custom_styles['heading']))
                content.append(Paragraph(analysis_data['summary'], self.custom_styles['highlight']))
                content.append(Spacer(1, 20))
            
            # Add current financial position
            content.extend(self._add_financial_position(financial_data))
            
            # Add risk assessment
            if 'risk_analysis' in analysis_data:
                content.extend(self._add_risk_assessment(analysis_data['risk_analysis']))
            
            # Add investment recommendations
            if 'investment_recommendations' in analysis_data:
                content.extend(self._add_investment_recommendations(analysis_data['investment_recommendations']))
            
            content.extend(self._add_report_footer())
            
            doc.build(content)
            
            buffer.seek(0)
            pdf_data = buffer.getvalue()
            buffer.close()
            
            logger.info("✅ Financial analysis PDF report generated successfully")
            return pdf_data
            
        except Exception as e:
            logger.error(f"❌ Failed to generate financial analysis PDF: {e}")
            raise
    
    def _add_report_header(self, title: str, user_data: Dict[str, Any]) -> List:
        """Add report header with title and user info"""
        content = []
        
        # Title
        content.append(Paragraph(title, self.custom_styles['title']))
        content.append(Spacer(1, 20))
        
        # Generated date
        content.append(Paragraph(f"Generated on: {datetime.now().strftime('%B %d, %Y at %I:%M %p')}", 
                                self.custom_styles['body']))
        
        # User info if available
        if user_data:
            user_name = user_data.get('name', 'N/A')
            content.append(Paragraph(f"Prepared for: {user_name}", self.custom_styles['body']))
        
        content.append(Spacer(1, 30))
        
        return content
    
    def _add_portfolio_summary(self, portfolio_data: Dict[str, Any]) -> List:
        """Add portfolio summary section"""
        content = []
        
        content.append(Paragraph("Portfolio Summary", self.custom_styles['heading']))
        
        # Create summary table
        summary_data = [
            ['Metric', 'Value'],
            ['Net Worth', f"₹{portfolio_data.get('net_worth', 0):,.2f}"],
            ['Total Assets', f"₹{portfolio_data.get('total_assets', 0):,.2f}"],
            ['Total Liabilities', f"₹{portfolio_data.get('total_liabilities', 0):,.2f}"],
            ['Mutual Fund Value', f"₹{portfolio_data.get('mutual_funds_value', 0):,.2f}"],
            ['Bank Balance', f"₹{portfolio_data.get('bank_balance', 0):,.2f}"],
            ['EPF Value', f"₹{portfolio_data.get('epf_value', 0):,.2f}"]
        ]
        
        table = Table(summary_data, colWidths=[3*inch, 2*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#00B899')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 14),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
            ('GRID', (0, 0), (-1, -1), 1, colors.black)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _add_financial_metrics(self, analytics_data: Dict[str, Any]) -> List:
        """Add financial metrics section"""
        content = []
        
        content.append(Paragraph("Financial Metrics", self.custom_styles['heading']))
        
        growth_data = analytics_data.get('growth', {})
        risk_data = analytics_data.get('risk', {})
        
        metrics_data = [
            ['Metric', 'Value', 'Description'],
            ['Growth Rate', f"{growth_data.get('annual_growth', 0):.2f}%", 'Year-over-year portfolio growth'],
            ['Volatility', f"{risk_data.get('volatility', 0):.2f}%", 'Portfolio risk measure'],
            ['Max Drawdown', f"{risk_data.get('max_drawdown', 0):.2f}%", 'Maximum decline from peak'],
            ['Sharpe Ratio', f"{risk_data.get('sharpe_ratio', 0):.2f}", 'Risk-adjusted returns'],
            ['Diversification Score', f"{risk_data.get('diversification_score', 0):.2f}", 'Portfolio diversification level']
        ]
        
        table = Table(metrics_data, colWidths=[2*inch, 1.5*inch, 2.5*inch])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), HexColor('#4A5568')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 12),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('BACKGROUND', (0, 1), (-1, -1), colors.white),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
            ('FONTSIZE', (0, 1), (-1, -1), 10)
        ]))
        
        content.append(table)
        content.append(Spacer(1, 20))
        
        return content
    
    def _add_allocation_chart(self, allocation_data: Dict[str, Any]) -> List:
        """Add asset allocation pie chart"""
        content = []
        
        content.append(Paragraph("Asset Allocation", self.custom_styles['heading']))
        
        try:
            # Create matplotlib pie chart
            labels = list(allocation_data.keys())
            sizes = list(allocation_data.values())
            
            fig, ax = plt.subplots(figsize=(8, 6))
            colors_list = ['#00B899', '#4A5568', '#E53E3E', '#3182CE', '#805AD5', '#D69E2E']
            
            ax.pie(sizes, labels=labels, autopct='%1.1f%%', startangle=90, 
                  colors=colors_list[:len(labels)])
            ax.axis('equal')
            plt.title('Asset Allocation', fontsize=16, fontweight='bold')
            
            # Save chart to buffer
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            plt.close()
            
            img_buffer.seek(0)
            
            # Add chart to PDF
            img = Image(img_buffer, width=5*inch, height=3.75*inch)
            content.append(img)
            content.append(Spacer(1, 20))
            
        except Exception as e:
            logger.warning(f"Failed to create allocation chart: {e}")
            content.append(Paragraph("Asset allocation chart could not be generated.", self.custom_styles['body']))
        
        return content
    
    def _add_performance_analysis(self, growth_data: Dict[str, Any]) -> List:
        """Add performance analysis section"""
        content = []
        
        content.append(Paragraph("Performance Analysis", self.custom_styles['heading']))
        
        performance_text = f"""
        Your portfolio has shown a {growth_data.get('annual_growth', 0):.2f}% annual growth rate. 
        Over the analyzed period, your portfolio has {'outperformed' if growth_data.get('annual_growth', 0) > 10 else 'underperformed'} 
        the market benchmark. The portfolio shows {'strong' if growth_data.get('annual_growth', 0) > 15 else 'moderate' if growth_data.get('annual_growth', 0) > 5 else 'weak'} 
        growth characteristics.
        """
        
        content.append(Paragraph(performance_text, self.custom_styles['body']))
        content.append(Spacer(1, 20))
        
        return content
    
    def _add_recommendations(self, insights_data: List[Dict[str, Any]]) -> List:
        """Add recommendations section"""
        content = []
        
        content.append(Paragraph("Recommendations", self.custom_styles['heading']))
        
        for i, insight in enumerate(insights_data[:5], 1):  # Limit to top 5 insights
            content.append(Paragraph(f"{i}. {insight.get('title', 'Recommendation')}", self.custom_styles['subheading']))
            content.append(Paragraph(insight.get('description', 'No description available'), self.custom_styles['body']))
            content.append(Spacer(1, 10))
        
        return content
    
    def _add_financial_position(self, financial_data: Dict[str, Any]) -> List:
        """Add current financial position section"""
        content = []
        
        content.append(Paragraph("Current Financial Position", self.custom_styles['heading']))
        
        net_worth_data = financial_data.get('net_worth', {}).get('netWorthResponse', {})
        total_value = net_worth_data.get('totalNetWorthValue', {}).get('units', '0')
        
        content.append(Paragraph(f"Current Net Worth: ₹{total_value}", self.custom_styles['highlight']))
        
        # Add asset breakdown if available
        assets = net_worth_data.get('assetValues', [])
        if assets:
            content.append(Paragraph("Asset Breakdown:", self.custom_styles['subheading']))
            for asset in assets[:10]:  # Limit to top 10 assets
                asset_type = asset.get('netWorthAttribute', 'Unknown')
                asset_value = asset.get('value', {}).get('units', '0')
                content.append(Paragraph(f"• {asset_type}: ₹{asset_value}", self.custom_styles['body']))
        
        content.append(Spacer(1, 20))
        
        return content
    
    def _add_risk_assessment(self, risk_data: Dict[str, Any]) -> List:
        """Add risk assessment section"""
        content = []
        
        content.append(Paragraph("Risk Assessment", self.custom_styles['heading']))
        
        risk_level = risk_data.get('overall_risk', 'Moderate')
        content.append(Paragraph(f"Overall Risk Level: {risk_level}", self.custom_styles['highlight']))
        
        if 'recommendations' in risk_data:
            for rec in risk_data['recommendations'][:3]:
                content.append(Paragraph(f"• {rec}", self.custom_styles['body']))
        
        content.append(Spacer(1, 20))
        
        return content
    
    def _add_investment_recommendations(self, recommendations: List[Dict[str, Any]]) -> List:
        """Add investment recommendations section"""
        content = []
        
        content.append(Paragraph("Investment Recommendations", self.custom_styles['heading']))
        
        for i, rec in enumerate(recommendations[:3], 1):
            content.append(Paragraph(f"{i}. {rec.get('title', 'Investment Opportunity')}", self.custom_styles['subheading']))
            content.append(Paragraph(rec.get('description', 'No description available'), self.custom_styles['body']))
            if 'expected_return' in rec:
                content.append(Paragraph(f"Expected Return: {rec['expected_return']}", self.custom_styles['body']))
            content.append(Spacer(1, 10))
        
        return content
    
    def _add_report_footer(self) -> List:
        """Add report footer"""
        content = []
        
        content.append(Spacer(1, 30))
        content.append(Paragraph("—" * 60, self.custom_styles['body']))
        content.append(Paragraph("This report was generated by Artha AI Financial Analysis System", 
                                self.custom_styles['body']))
        content.append(Paragraph("For questions or support, please contact your financial advisor.", 
                                self.custom_styles['body']))
        
        return content


# Service instance
pdf_service = PDFGenerationService()


def get_pdf_service() -> PDFGenerationService:
    """Get PDF generation service instance"""
    return pdf_service