#!/usr/bin/env python3
"""
Command-line interface for the Perplexity Agent.
Usage: python cli.py "your query here"
"""

import argparse
import sys
import os
from typing import Optional
from perplexity_agent import PerplexityAgent

def main():
    parser = argparse.ArgumentParser(
        description="Advanced Perplexity-like agent for researching topics and generating reports",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python cli.py "Can I buy Reliance stock right now?" --comprehensive --max-articles 30
  python cli.py "TCS earnings analysis" --financial --max-articles 15
  python cli.py "Current inflation rate in India" --output reports/inflation_report.txt
  python cli.py "AI trends 2024" --quick
        """
    )
    
    parser.add_argument(
        "query",
        help="The query to research"
    )
    
    parser.add_argument(
        "--max-articles",
        type=int,
        default=20,
        help="Maximum number of articles to fetch (default: 20)"
    )
    
    parser.add_argument(
        "--output",
        type=str,
        help="Output file path (default: auto-generated in reports/ directory)"
    )
    
    parser.add_argument(
        "--quick",
        action="store_true",
        help="Quick mode - returns only analysis without saving full report"
    )
    
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Verbose output"
    )
    
    parser.add_argument(
        "--financial",
        action="store_true",
        help="Use specialized financial research mode with stock data integration"
    )
    
    parser.add_argument(
        "--comprehensive",
        action="store_true",
        help="Use comprehensive research mode to gather vast amounts of content"
    )
    
    args = parser.parse_args()
    
    # Set up logging level
    if args.verbose:
        import logging
        logging.basicConfig(level=logging.INFO)
    
    try:
        print(f"🔍 Researching: {args.query}")
        print("=" * 60)
        
        # Initialize agent
        agent = PerplexityAgent()
        
        if args.quick:
            # Quick mode
            print("Running in quick mode...")
            analysis = agent.quick_research(args.query)
            print("\n📊 Analysis:")
            print("-" * 40)
            print(analysis)
        else:
            # Full research mode
            if args.comprehensive:
                print(f"📊 Running comprehensive data collection mode...")
                print(f"Gathering raw article content (up to {args.max_articles} articles)...")
                print(f"LLM will only generate search queries - no analysis included")
                results = agent.comprehensive_research(args.query, max_articles=args.max_articles)
            elif args.financial:
                print(f"🏦 Running financial research mode...")
                print(f"Fetching up to {args.max_articles} articles + stock data...")
                results = agent.financial_research(args.query, max_articles=args.max_articles)
            else:
                print(f"Fetching up to {args.max_articles} articles...")
                results = agent.research(args.query, max_articles=args.max_articles)
            
            # Save report
            if args.output:
                # Use specified output path
                output_dir = os.path.dirname(args.output)
                if output_dir and not os.path.exists(output_dir):
                    os.makedirs(output_dir, exist_ok=True)
                filename = os.path.basename(args.output)
                if output_dir:
                    agent.output_dir = output_dir
                filepath = agent.save_report_to_file(results, filename)
            else:
                # Auto-generate filename
                filepath = agent.save_report_to_file(results)
            
            # Print results summary
            print(f"\n✅ Data collection completed!")
            print(f"📰 Articles collected: {results['articles_fetched']}")
            
            if results.get('total_content_length'):
                print(f"📊 Total content: {results['total_content_length']:,} characters")
            
            if results.get('search_queries_generated'):
                print(f"🔍 Search queries generated: {len(results['search_queries_generated'])}")
            
            if results.get('stock_data'):
                print(f"📈 Stock data retrieved: {results['stock_data'].get('symbol', 'N/A')}")
            
            print(f"⏱️  Duration: {results['duration_seconds']:.2f} seconds")
            print(f"💾 Raw data saved to: {filepath}")
            
            # Show preview only for non-comprehensive mode
            if not args.comprehensive and results.get('analysis'):
                print(f"\n📊 Analysis Preview:")
                print("-" * 40)
                analysis_preview = results['analysis'][:800]
                if len(results['analysis']) > 800:
                    analysis_preview += "..."
                print(analysis_preview)
            elif args.comprehensive:
                print(f"\n📁 Pure article data ready for your LLM processing!")
                if results.get('search_queries_generated'):
                    print(f"🔍 Generated queries: {results['search_queries_generated'][:2]}...")
                print(f"📊 Ready to feed {results['total_content_length']:,} characters to any LLM")
            
            print(f"\n📁 Full report available at: {filepath}")
    
    except KeyboardInterrupt:
        print("\n❌ Research interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Error: {e}")
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    main()