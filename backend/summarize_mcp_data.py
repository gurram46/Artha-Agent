import json
import os
from typing import Dict, List, Any

def compress_value(amount: Any) -> str:
    """Convert amount to compressed format (K/L/Cr)"""
    try:
        val = float(str(amount).replace(',', ''))
        if val >= 10000000:
            return f"{val/10000000:.1f}Cr"
        elif val >= 100000:
            return f"{val/100000:.0f}L"
        elif val >= 1000:
            return f"{val/1000:.0f}K"
        else:
            return str(int(val))
    except:
        return "0"

def extract_key_data(data: Dict[str, Any]) -> Dict[str, Any]:
    """Extract only essential data points for local LLM processing"""
    summary = {}
    
    # Net Worth
    if 'netWorthResponse' in data:
        nw = data['netWorthResponse']
        summary['nw'] = compress_value(nw.get('totalNetWorthValue', {}).get('units', 0))
        
        # Assets
        assets = {}
        for asset in nw.get('assetValues', []):
            asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '').lower()
            if asset_type in ['mutual_fund', 'epf', 'indian_securities', 'savings_accounts']:
                key = asset_type.replace('_', '').replace('accounts', 'acc')
                assets[key] = compress_value(asset.get('value', {}).get('units', 0))
        summary['assets'] = assets
        
        # Liabilities
        total_debt = 0
        for liability in nw.get('liabilityValues', []):
            total_debt += float(liability.get('value', {}).get('units', 0))
        if total_debt > 0:
            summary['debt'] = compress_value(total_debt)
    
    # Top MF holdings
    if 'mfSchemeAnalytics' in data:
        mf_list = []
        for fund in data['mfSchemeAnalytics'].get('schemeAnalytics', [])[:3]:
            details = fund.get('enrichedAnalytics', {}).get('analytics', {}).get('schemeDetails', {})
            val = float(details.get('currentValue', {}).get('units', 0))
            xirr = details.get('XIRR', 0)
            if val > 10000:  # Only include significant holdings
                mf_list.append({
                    'v': compress_value(val),
                    'r': f"{xirr:.0f}%" if isinstance(xirr, (int, float)) and xirr != 0 else None
                })
        if mf_list:
            summary['mf'] = mf_list
    
    # Credit Score
    if 'creditReports' in data:
        score = data['creditReports'][0].get('creditReportData', {}).get('score', {}).get('bureauScore')
        if score:
            summary['credit'] = score
    
    # EPF
    if 'uanAccounts' in data:
        epf = data['uanAccounts'][0].get('rawDetails', {}).get('overall_pf_balance', {})
        balance = epf.get('current_pf_balance')
        if balance:
            summary['epf'] = compress_value(balance)
    
    # MF Transactions summary
    if 'transactions' in data:
        total_invested = 0
        for tx in data['transactions']:
            if tx.get('externalOrderType') == 'BUY':
                total_invested += float(tx.get('transactionAmount', {}).get('units', 0))
        if total_invested > 0:
            summary['mf_invested'] = compress_value(total_invested)
    
    return summary

def create_ultra_compact_summary():
    """Create an ultra-compact summary under 1K tokens for local LLM"""
    base_path = os.path.join(os.path.dirname(__file__), '..', 'mcp-docs', 'sample_responses')
    
    # Combined data structure
    all_data = {}
    
    # Load all JSON files
    files = ['fetch_net_worth.json', 'fetch_credit_report.json', 'fetch_epf_details.json', 'fetch_mf_transactions.json']
    
    for file in files:
        try:
            with open(os.path.join(base_path, file)) as f:
                data = json.load(f)
                key_data = extract_key_data(data)
                all_data.update(key_data)
        except:
            continue
    
    # Create ultra-compact text format
    compact_lines = []
    
    # Financial snapshot
    if 'nw' in all_data:
        compact_lines.append(f"NW:{all_data['nw']}")
    
    if 'assets' in all_data:
        asset_str = ','.join([f"{k}:{v}" for k, v in all_data['assets'].items()])
        compact_lines.append(f"A:{asset_str}")
    
    if 'debt' in all_data:
        compact_lines.append(f"D:{all_data['debt']}")
    
    if 'credit' in all_data:
        compact_lines.append(f"CS:{all_data['credit']}")
    
    if 'mf' in all_data:
        mf_str = ','.join([f"{mf['v']}" + (f"@{mf['r']}" if mf.get('r') else "") for mf in all_data['mf'][:2]])
        compact_lines.append(f"MF:{mf_str}")
    
    # Save as JSON for structured access
    json_output = os.path.join(os.path.dirname(__file__), 'mcp_compact.json')
    with open(json_output, 'w') as f:
        json.dump(all_data, f, separators=(',', ':'))
    
    # Save as ultra-compact text
    text_output = os.path.join(os.path.dirname(__file__), 'mcp_summary.txt')
    with open(text_output, 'w') as f:
        f.write('|'.join(compact_lines))
    
    # Print token estimate
    text_content = '|'.join(compact_lines)
    char_count = len(text_content)
    token_estimate = char_count // 4  # Rough estimate: 1 token ≈ 4 characters
    
    print(f"Summary created:")
    print(f"- Text file: {text_output} ({char_count} chars, ~{token_estimate} tokens)")
    print(f"- JSON file: {json_output}")
    print(f"Content: {text_content}")
    
    return text_content

def generate_local_llm_format():
    """Generate format optimized for local LLM with minimal context"""
    base_path = os.path.join(os.path.dirname(__file__), '..', 'mcp-docs', 'sample_responses')
    
    # Template for local LLM
    template = {
        "user_profile": {
            "net_worth": "",
            "assets": {},
            "liabilities": "",
            "credit_score": "",
            "risk_level": ""
        },
        "key_metrics": {},
        "actions_available": [
            "analyze_portfolio",
            "check_credit_health",
            "investment_advice",
            "debt_management"
        ]
    }
    
    # Load and process data
    try:
        with open(os.path.join(base_path, 'fetch_net_worth.json')) as f:
            nw_data = json.load(f)
            
        nw_response = nw_data.get('netWorthResponse', {})
        template['user_profile']['net_worth'] = compress_value(nw_response.get('totalNetWorthValue', {}).get('units', 0))
        
        # Process assets
        for asset in nw_response.get('assetValues', []):
            asset_type = asset.get('netWorthAttribute', '').replace('ASSET_TYPE_', '').lower()
            template['user_profile']['assets'][asset_type] = compress_value(asset.get('value', {}).get('units', 0))
        
        # Calculate debt
        total_debt = sum(float(l.get('value', {}).get('units', 0)) for l in nw_response.get('liabilityValues', []))
        if total_debt > 0:
            template['user_profile']['liabilities'] = compress_value(total_debt)
        
        # Risk assessment based on portfolio
        mf_data = nw_data.get('mfSchemeAnalytics', {}).get('schemeAnalytics', [])
        high_risk_count = sum(1 for f in mf_data if 'HIGH_RISK' in f.get('schemeDetail', {}).get('fundhouseDefinedRiskLevel', ''))
        template['user_profile']['risk_level'] = "high" if high_risk_count > 2 else "moderate"
        
    except:
        pass
    
    # Save minimal format
    minimal_output = os.path.join(os.path.dirname(__file__), 'mcp_minimal.json')
    with open(minimal_output, 'w') as f:
        json.dump(template, f, separators=(',', ':'))
    
    print(f"Minimal format saved to: {minimal_output}")
    
    return template

if __name__ == "__main__":
    # Generate ultra-compact summary
    summary = create_ultra_compact_summary()
    
    # Generate minimal JSON for local LLM
    minimal = generate_local_llm_format()
    
    print("\n✅ Files generated successfully for local LLM processing!")