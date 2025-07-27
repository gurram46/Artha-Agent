"""
Demo-only hardcoded responses with * indicator
For demo accounts: Return intelligent hardcoded data instantly
For real accounts: Use actual SAndeep AI agents
"""

import random
from datetime import datetime
from typing import Dict, Any, List

class DemoResponseEngine:
    """
    Hardcoded intelligent responses for DEMO accounts only
    All responses include * to indicate demo data
    """
    
    def __init__(self):
        self.demo_indicator = "* DEMO DATA"
        
    def get_hardcoded_investment_recommendation(self, 
                                               investment_amount: float,
                                               risk_tolerance: str,
                                               investment_goal: str,
                                               net_worth: float) -> str:
        """
        Complete hardcoded investment recommendation based on recent market research
        """
        
        # Personalize based on input parameters
        risk_level = risk_tolerance.lower()
        amount_formatted = f"₹{investment_amount:,.0f}"
        net_worth_formatted = f"₹{net_worth:,.0f}"
        
        response = f"""
# 🎯 **SAndeep Multi-Agent Investment Analysis** {self.demo_indicator}

## 📊 **Investment Summary**
- **Investment Amount:** {amount_formatted}
- **Risk Profile:** {risk_tolerance.title()}
- **Investment Goal:** {investment_goal.replace('_', ' ').title()}
- **Current Net Worth:** {net_worth_formatted}

## 🤖 **4-Agent Analysis Complete**

### **📈 Data Analyst Agent Findings:**
Based on current market conditions (July 2025):
- **Market Status:** BSE Sensex at 86,000 levels, Nifty at 26,277
- **Market Outlook:** Corrections creating buying opportunities
- **FII Activity:** Net selling creating value picks
- **Best SIP Strategy:** Systematic investment recommended

### **💹 Trading Analyst Agent Recommendations:**

#### **🏆 TOP MUTUAL FUND PICKS** {self.demo_indicator}

**1. Nippon India Large Cap Fund**
- **3-Year Returns:** 22.74% *
- **5-Year Returns:** 25.94% *
- **Minimum SIP:** ₹100 *
- **Allocation:** 25% (₹{investment_amount * 0.25:,.0f}) *

**2. HDFC Mid-Cap Opportunities Fund**
- **3-Year Returns:** 33.18% *
- **5-Year Returns:** 32.88% *
- **Minimum SIP:** ₹100 *
- **Allocation:** 20% (₹{investment_amount * 0.20:,.0f}) *

**3. SBI Long Term Equity Fund (ELSS)**
- **3-Year Returns:** 30.65% *
- **5-Year Returns:** 29.03% *
- **Tax Benefit:** ₹1.5L deduction under 80C *
- **Allocation:** 15% (₹{investment_amount * 0.15:,.0f}) *

#### **📊 BLUE CHIP STOCK PICKS** {self.demo_indicator}

**1. Tata Consultancy Services (TCS)**
- **Sector:** IT Services *
- **ROE:** 59.60% *
- **Investment Thesis:** Cash-rich, zero-debt, AI leader *
- **Allocation:** 10% (₹{investment_amount * 0.10:,.0f}) *

**2. ICICI Bank**
- **Sector:** Banking *
- **ROE:** 18.98% *
- **Investment Thesis:** Digital banking leader *
- **Allocation:** 10% (₹{investment_amount * 0.10:,.0f}) *

### **⚖️ Risk Analyst Agent Assessment:**

{self._get_risk_specific_advice(risk_level, investment_amount)}

### **🚀 Execution Analyst Agent - Broker Recommendations:**

#### **📱 BEST BROKERS FOR YOUR PROFILE** {self.demo_indicator}

**For Beginners: Groww**
- **Delivery Trading:** Free *
- **Demat AMC:** Free *
- **Rating:** 4.0/5 *
- **Best For:** Simple UI, goal-based investing *

**For Long-term: Zerodha**
- **Delivery Trading:** Free *
- **Platform:** Kite (best-in-class) *
- **Rating:** 4.5/5 *
- **Best For:** Serious investors *

**For Full Service: Angel One**
- **Research:** Comprehensive *
- **PMS Available:** Yes *
- **Rating:** 4.5/5 *
- **Best For:** Guided investing *

## 📋 **COMPLETE PORTFOLIO ALLOCATION** {self.demo_indicator}

| **Investment** | **Type** | **Amount** | **%** | **Expected Returns** |
|---|---|---|---|---|
| Nippon Large Cap Fund | Mutual Fund | ₹{investment_amount * 0.25:,.0f} | 25% | 22.74% * |
| HDFC Mid Cap Fund | Mutual Fund | ₹{investment_amount * 0.20:,.0f} | 20% | 33.18% * |
| SBI ELSS Fund | Tax Saver | ₹{investment_amount * 0.15:,.0f} | 15% | 30.65% * |
| TCS Stock | Blue Chip | ₹{investment_amount * 0.10:,.0f} | 10% | 25-30% * |
| ICICI Bank Stock | Banking | ₹{investment_amount * 0.10:,.0f} | 10% | 20-25% * |
| Emergency Fund | Liquid/FD | ₹{investment_amount * 0.20:,.0f} | 20% | 6-7% * |

## 🎯 **KEY INSIGHTS & NEXT STEPS** {self.demo_indicator}

### **✅ Why These Recommendations:**
1. **Diversified Portfolio:** Mix of large cap, mid cap, and ELSS *
2. **Tax Optimization:** ELSS provides ₹46,350 tax saving *
3. **Risk-Adjusted:** Suitable for {risk_tolerance.title()} risk profile *
4. **Quality Picks:** Top-performing funds with proven track records *
5. **Blue Chip Exposure:** TCS and ICICI for stability *

### **📅 Investment Timeline:**
- **Month 1-3:** Start SIPs in all mutual funds *
- **Month 4-6:** Begin stock investments through STP *
- **Month 7-12:** Monitor and rebalance quarterly *

### **🔄 SIP Schedule Recommendation:**
- **Total Monthly SIP:** ₹{investment_amount / 10:,.0f} (if spread over 10 months) *
- **Large Cap SIP:** ₹{(investment_amount * 0.25) / 10:,.0f}/month *
- **Mid Cap SIP:** ₹{(investment_amount * 0.20) / 10:,.0f}/month *
- **ELSS SIP:** ₹{(investment_amount * 0.15) / 10:,.0f}/month *

## 🛡️ **Risk Mitigation** {self.demo_indicator}
- **Emergency Fund:** 20% in liquid investments *
- **Diversification:** Across 6 different assets *
- **SIP Strategy:** Rupee cost averaging *
- **Quality Focus:** Only top-rated funds and stocks *

## 📞 **Ready to Invest?** {self.demo_indicator}
1. **Open Demat Account:** Groww (for beginners) or Zerodha (for experience) *
2. **Start SIPs:** Begin with mutual funds *
3. **KYC Completion:** Complete in 24 hours *
4. **First Investment:** Can start with just ₹100 *

---
*🤖 Generated by SAndeep Multi-Agent Investment System*
*📅 Analysis Date: {datetime.now().strftime('%B %d, %Y')} {self.demo_indicator}*
*⚡ Response Time: Instant (Demo Mode)*
"""
        
        return response.strip()
    
    def _get_risk_specific_advice(self, risk_level: str, amount: float) -> str:
        """Get risk-specific advice with demo indicator"""
        
        if risk_level == "conservative":
            return f"""
**Conservative Risk Profile Analysis** {self.demo_indicator}
- **Recommended Allocation:** 60% Debt, 30% Large Cap, 10% Emergency *
- **Expected Annual Returns:** 12-15% *
- **Volatility:** Low to moderate *
- **Strategy:** Focus on large cap funds and debt instruments *
- **Timeline:** 5+ years for optimal results *
"""
        elif risk_level == "aggressive":
            return f"""
**Aggressive Risk Profile Analysis** {self.demo_indicator}
- **Recommended Allocation:** 70% Equity, 20% Mid/Small Cap, 10% Emergency *
- **Expected Annual Returns:** 18-25% *
- **Volatility:** High (prepare for 20-30% swings) *
- **Strategy:** Mid cap focus with growth stocks *
- **Timeline:** 7+ years for wealth creation *
"""
        else:  # moderate
            return f"""
**Moderate Risk Profile Analysis** {self.demo_indicator}
- **Recommended Allocation:** 50% Large Cap, 30% Mid Cap, 20% Safe instruments *
- **Expected Annual Returns:** 15-20% *
- **Volatility:** Moderate (10-15% swings expected) *
- **Strategy:** Balanced approach with quality picks *
- **Timeline:** 5-7 years for good returns *
"""
    
    def get_hardcoded_chat_response(self, query: str, financial_data: Dict[str, Any]) -> str:
        """
        Hardcoded chat responses for common investment queries
        """
        
        query_lower = query.lower()
        net_worth = financial_data.get('net_worth', {}).get('netWorthResponse', {}).get('totalNetWorthValue', {}).get('units', '0')
        
        # Best mutual funds query
        if any(word in query_lower for word in ['best', 'mutual fund', 'sip', 'recommend']):
            return f"""
# 🏆 **Best Mutual Funds 2025** {self.demo_indicator}

## **🥇 TOP LARGE CAP FUNDS**
**1. Nippon India Large Cap Fund**
- **3Y Returns:** 22.74% *
- **5Y Returns:** 25.94% *
- **Min SIP:** ₹100 *
- **Why:** Consistent performer with strong portfolio *

**2. ICICI Prudential Bluechip Fund**
- **3Y Returns:** 22.26% *
- **5Y Returns:** 24.7% *
- **Why:** Proven track record in blue chip stocks *

## **🚀 TOP MID CAP FUNDS**
**1. HDFC Mid-Cap Opportunities Fund**
- **3Y Returns:** 33.18% *
- **5Y Returns:** 32.88% *
- **Min SIP:** ₹100 *
- **Why:** Outstanding mid cap performance *

## **💰 BEST ELSS (Tax Saving)**
**1. SBI Long Term Equity Fund**
- **3Y Returns:** 30.65% *
- **Tax Benefit:** ₹1.5L deduction *
- **Lock-in:** Only 3 years *

**Your Net Worth:** ₹{net_worth} *
**Recommendation:** Start with ₹5,000 monthly SIP across these funds *

*🤖 SAndeep AI Analysis {self.demo_indicator}*
"""
        
        # Stock recommendations query
        elif any(word in query_lower for word in ['stock', 'share', 'equity', 'buy']):
            return f"""
# 📈 **Top Stock Picks 2025** {self.demo_indicator}

## **🏆 BLUE CHIP RECOMMENDATIONS**

**1. Tata Consultancy Services (TCS)**
- **Sector:** IT Services *
- **Current Price:** ₹4,200 (approx) *
- **Target:** ₹5,000 (19% upside) *
- **ROE:** 59.60% *
- **Why:** Cash-rich, zero debt, AI leader *

**2. ICICI Bank**
- **Sector:** Banking *
- **ROE:** 18.98% *
- **Dividend Yield:** 1.2% *
- **Why:** Digital banking pioneer *

**3. Reliance Industries**
- **Sector:** Diversified *
- **Businesses:** Oil, Telecom, Retail, Green Energy *
- **Why:** India's largest private company *

**Your Profile:** Net Worth ₹{net_worth} *
**Suggestion:** Invest ₹10,000-15,000 per stock via SIP *

*📊 Updated: July 2025 {self.demo_indicator}*
"""
        
        # Broker comparison query
        elif any(word in query_lower for word in ['broker', 'demat', 'trading', 'platform']):
            return f"""
# 📱 **Best Trading Platforms 2025** {self.demo_indicator}

## **🥇 TOP BROKER COMPARISON**

**For Beginners: Groww ⭐⭐⭐⭐**
- **Delivery:** Free *
- **Demat AMC:** Free *
- **Interface:** Very simple *
- **Best For:** First-time investors *

**For Serious Investors: Zerodha ⭐⭐⭐⭐⭐**
- **Delivery:** Free *
- **Platform:** Kite (best-in-class) *
- **Education:** Excellent *
- **Best For:** Long-term investors *

**For Full Service: Angel One ⭐⭐⭐⭐⭐**
- **Research:** Comprehensive *
- **Advisory:** Available *
- **PMS:** Yes *
- **Best For:** Guided investing *

**For Active Trading: Upstox ⭐⭐⭐⭐**
- **Speed:** Fastest execution *
- **Tools:** Advanced charting *
- **API:** Available *

**Recommendation for your profile:** Start with Groww, upgrade to Zerodha later *

*💡 All data updated July 2025 {self.demo_indicator}*
"""
        
        # Market outlook query
        elif any(word in query_lower for word in ['market', 'outlook', 'sensex', 'nifty', '2025']):
            return f"""
# 📊 **Indian Market Outlook 2025** {self.demo_indicator}

## **📈 CURRENT MARKET STATUS**
- **BSE Sensex:** ~86,000 levels *
- **Nifty 50:** ~26,277 *
- **Nifty Bank:** ~54,467 *
- **Market Cap:** All-time highs reached in 2024 *

## **🎯 2025 PREDICTIONS**
**Challenges:**
- FII selling pressure (₹2L+ crores outflow) *
- Rupee at 85.13 vs USD (all-time low) *
- Corporate earnings pressure *

**Opportunities:**
- Market corrections = buying opportunities *
- Quality stocks at reasonable valuations *
- SIP investments ideal for volatility *

## **💡 INVESTMENT STRATEGY**
**Best Approach for 2025:**
1. **Continue SIPs** - Don't stop during volatility *
2. **Quality Focus** - Stick to top-rated funds *
3. **Diversification** - Mix large cap, mid cap, ELSS *
4. **Long-term View** - 5-7 year minimum horizon *

**Your Action:** With ₹{net_worth} net worth, focus on systematic investing *

*📅 Analysis: July 2025 {self.demo_indicator}*
"""
        
        # Tax saving query
        elif any(word in query_lower for word in ['tax', 'save', '80c', 'elss']):
            return f"""
# 💰 **Tax Saving Investments 2025** {self.demo_indicator}

## **🏆 BEST 80C OPTIONS**

**1. ELSS Mutual Funds (RECOMMENDED)**
- **Deduction:** Up to ₹1.5L *
- **Lock-in:** Only 3 years *
- **Returns:** 15-25% potential *
- **Top Pick:** SBI Long Term Equity Fund (30.65% returns) *

**2. PPF (Public Provident Fund)**
- **Deduction:** Up to ₹1.5L *
- **Lock-in:** 15 years *
- **Returns:** ~7.1% (tax-free) *
- **Benefit:** EEE status *

**3. EPF (Employee Provident Fund)**
- **Automatic:** From salary *
- **Returns:** ~8.25% *
- **Employer:** Matching contribution *

## **💡 TAX CALCULATION**
**If you invest ₹1.5L in ELSS:**
- **Tax Saved:** ₹46,350 (30% bracket) *
- **Effective Cost:** ₹1,03,650 *
- **3-Year Potential:** ₹2.8L+ (at 25% CAGR) *

**Your Net Worth:** ₹{net_worth} *
**Recommendation:** Maximize ELSS allocation for tax + growth *

*🧮 Calculations based on current tax rates {self.demo_indicator}*
"""
        
        # Default comprehensive response
        else:
            return f"""
# 🤖 **SAndeep AI Investment Assistant** {self.demo_indicator}

## **📊 QUICK INSIGHTS FOR YOUR PROFILE**
- **Your Net Worth:** ₹{net_worth} *
- **Analysis Date:** {datetime.now().strftime('%B %d, %Y')} *

## **🎯 TOP RECOMMENDATIONS**

**1. Start Monthly SIP:** ₹5,000-10,000 across top funds *
**2. Best Large Cap:** Nippon India Large Cap Fund (22.74% returns) *
**3. Best Mid Cap:** HDFC Mid-Cap Opportunities (33.18% returns) *
**4. Tax Saving:** SBI ELSS Fund (30.65% returns) *
**5. Blue Chip Stock:** TCS (59.60% ROE) *

## **📱 RECOMMENDED BROKER**
**Groww** - Perfect for beginners with free delivery trading *

## **💡 NEXT STEPS**
1. Open demat account with Groww *
2. Start with ₹1,000 SIP in Nippon Large Cap Fund *
3. Add ELSS for tax savings *
4. Gradually increase investment amount *

*Ask me about specific topics: "best mutual funds", "top stocks", "broker comparison", "tax saving" *

*🚀 Powered by SAndeep Multi-Agent AI {self.demo_indicator}*
"""

    def get_demo_indicator(self) -> str:
        """Return the demo indicator"""
        return self.demo_indicator

# Global instance for quick access
demo_responses = DemoResponseEngine()