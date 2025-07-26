"""
Test script for the new Demat Broker Selection feature.
This demonstrates the complete flow from recommendations to broker selection and login.
"""

from services.demat_broker_service import create_demat_broker_interface

def main():
    print("🧪 TESTING DEMAT BROKER SELECTION FEATURE")
    print("=" * 50)
    
    print("\n📊 Simulating investment recommendations...")
    
    # Sample investment recommendations
    sample_recommendations = [
        """
        Based on your ₹50,000 investment profile:
        
        🎯 RECOMMENDED PORTFOLIO:
        • Nifty ETF (NIFTYBEES): ₹20,000 (40%)
        • Bank Nifty ETF (BANKBEES): ₹15,000 (30%) 
        • Gold ETF (GOLDBEES): ₹10,000 (20%)
        • Emergency Fund: ₹5,000 (10%)
        
        Expected Returns: 12-15% annually
        Risk Level: Moderate
        Investment Horizon: 3-5 years
        """
    ]
    
    print("✅ Investment recommendations generated!")
    print("\n🚀 Now testing the 'Invest Now' feature...")
    
    # Test the demat broker interface
    create_demat_broker_interface(sample_recommendations)

if __name__ == "__main__":
    main()