'use client';

import React, { useState } from 'react';

interface PDFExportButtonProps {
  type: 'portfolio' | 'chat' | 'financial-analysis' | 'conversation';
  conversationId?: string;
  userId?: string;
  variant?: 'default' | 'outline' | 'minimal';
  className?: string;
  onExportStart?: () => void;
  onExportComplete?: () => void;
  onExportError?: (error: string) => void;
}

export default function PDFExportButton({
  type,
  conversationId,
  userId = 'demo-user',
  variant = 'default',
  className = '',
  onExportStart,
  onExportComplete,
  onExportError
}: PDFExportButtonProps) {
  const [isExporting, setIsExporting] = useState(false);

  const handleExportPDF = async () => {
    setIsExporting(true);
    onExportStart?.();

    try {
      let url = '';
      let filename = '';

      switch (type) {
        case 'portfolio':
          url = `/api/portfolio/export?format=pdf`;
          filename = `artha_portfolio_${new Date().toISOString().split('T')[0]}.pdf`;
          break;
        
        case 'chat':
          if (!conversationId) {
            throw new Error('Conversation ID is required for chat export');
          }
          url = `/api/chat/conversations/${conversationId}/export/pdf?user_id=${userId}`;
          filename = `artha_chat_${conversationId.slice(0, 8)}_${new Date().toISOString().split('T')[0]}.pdf`;
          break;
        
        case 'financial-analysis':
          url = `/api/generate-pdf/financial-analysis?demo=false`;
          filename = `artha_financial_analysis_${new Date().toISOString().split('T')[0]}.pdf`;
          break;
        
        case 'conversation':
          url = `/api/chat/export/all-conversations/pdf?user_id=${userId}&days=30`;
          filename = `artha_all_conversations_${new Date().toISOString().split('T')[0]}.pdf`;
          break;
        
        default:
          throw new Error('Invalid export type');
      }

      // Create a temporary link to download the PDF
      const link = document.createElement('a');
      link.href = `http://localhost:8000${url}`;
      link.download = filename;
      link.target = '_blank';
      
      // Append to body, click, and remove
      document.body.appendChild(link);
      link.click();
      document.body.removeChild(link);

      onExportComplete?.();
    } catch (error) {
      console.error('PDF export failed:', error);
      const errorMessage = error instanceof Error ? error.message : 'Export failed';
      onExportError?.(errorMessage);
    } finally {
      setIsExporting(false);
    }
  };

  const getButtonText = () => {
    if (isExporting) return 'Generating PDF...';
    
    switch (type) {
      case 'portfolio': return 'Export Portfolio PDF';
      case 'chat': return 'Export Chat PDF';
      case 'financial-analysis': return 'Generate Analysis PDF';
      case 'conversation': return 'Export All Chats PDF';
      default: return 'Export PDF';
    }
  };

  const getButtonIcon = () => (
    <svg 
      className="w-4 h-4 mr-2" 
      fill="none" 
      stroke="currentColor" 
      viewBox="0 0 24 24"
    >
      {isExporting ? (
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-8l-4-4m0 0L8 8m4-4v12"
        />
      ) : (
        <path 
          strokeLinecap="round" 
          strokeLinejoin="round" 
          strokeWidth={2} 
          d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"
        />
      )}
    </svg>
  );

  const baseStyles = "inline-flex items-center px-4 py-2 rounded-lg font-medium transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed";
  
  const variantStyles = {
    default: "bg-[rgb(34,197,94)] hover:bg-[rgb(22,163,74)] text-white shadow-sm hover:shadow-md",
    outline: "border-2 border-[rgb(34,197,94)] text-[rgb(34,197,94)] hover:bg-[rgb(34,197,94)] hover:text-white",
    minimal: "text-[rgb(34,197,94)] hover:bg-[rgba(34,197,94,0.1)] px-2 py-1"
  };

  return (
    <button
      onClick={handleExportPDF}
      disabled={isExporting}
      className={`${baseStyles} ${variantStyles[variant]} ${className}`}
      title={getButtonText()}
    >
      {getButtonIcon()}
      <span className="text-sm">{getButtonText()}</span>
    </button>
  );
}

// Individual export button components for specific use cases
export const PortfolioExportButton = (props: Omit<PDFExportButtonProps, 'type'>) => (
  <PDFExportButton {...props} type="portfolio" />
);

export const ChatExportButton = (props: Omit<PDFExportButtonProps, 'type'>) => (
  <PDFExportButton {...props} type="chat" />
);

export const FinancialAnalysisExportButton = (props: Omit<PDFExportButtonProps, 'type'>) => (
  <PDFExportButton {...props} type="financial-analysis" />
);

export const AllConversationsExportButton = (props: Omit<PDFExportButtonProps, 'type'>) => (
  <PDFExportButton {...props} type="conversation" />
);