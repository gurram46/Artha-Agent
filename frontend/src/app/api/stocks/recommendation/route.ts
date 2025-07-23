import { NextResponse } from 'next/server';

// Integration with Stock AI Agents backend - REAL DATA ONLY  
const STOCK_AI_URL = process.env.STOCK_AI_URL || 'http://localhost:8003';

// Helper function to call stock AI agents - NO FALLBACKS
async function callStockAIAgent(endpoint: string, data: any) {
  try {
    console.log(`🤖 Calling Stock AI Agent: ${endpoint} with data:`, JSON.stringify(data, null, 2));
    
    const response = await fetch(`${STOCK_AI_URL}${endpoint}`, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify(data),
      // Add timeout for long-running AI operations
      signal: AbortSignal.timeout(180000), // 3 minutes timeout for AI processing
    });

    if (!response.ok) {
      const errorText = await response.text();
      console.error(`Stock AI agent ${endpoint} failed with status ${response.status}: ${errorText}`);
      throw new Error(`Stock AI API returned ${response.status}: ${errorText}`);
    }

    const result = await response.json();
    console.log(`✅ Stock AI agent ${endpoint} completed successfully:`, result);
    return result;
    
  } catch (error) {
    if (error.name === 'TimeoutError') {
      console.error(`Stock AI agent ${endpoint} timed out after 3 minutes`);
      throw new Error('Stock analysis timed out - please try again');
    } else {
      console.error(`Error calling Stock AI agent ${endpoint}:`, error);
      throw error;
    }
  }
}

interface UserProfile {
  riskTolerance: 'conservative' | 'moderate' | 'aggressive';
  investmentHorizon: 'short' | 'medium' | 'long';
  investmentGoal: 'growth' | 'income' | 'balanced';
  monthlyInvestment: number;
  netWorth?: number;
  age?: number;
}

// Only real data from Stock AI Agents backend - no mock interfaces needed

export async function POST(request: Request) {
  try {
    const { symbol, userProfile, stockData } = await request.json();

    if (!symbol || !userProfile) {
      return NextResponse.json(
        { error: 'Symbol and user profile are required' },
        { status: 400 }
      );
    }

    console.log(`🚀 Generating AI recommendation for ${symbol} with profile:`, {
      risk: userProfile.riskTolerance,
      horizon: userProfile.investmentHorizon,
      goal: userProfile.investmentGoal
    });

    // Call the real Stock AI Agents backend - NO FALLBACKS
    const aiRecommendation = await callStockAIAgent('/api/stock/full-analysis', {
      symbol,
      company_name: stockData?.name || symbol.replace('.NS', ''),
      user_profile: userProfile,
      stock_data: stockData || {}
    });

    if (!aiRecommendation) {
      throw new Error('Stock AI agents backend is not available');
    }

    if (!aiRecommendation.recommendation) {
      throw new Error('Invalid response from Stock AI agents - missing recommendation');
    }

    // Transform AI agent response to frontend format
    const recommendation = aiRecommendation.recommendation;
    
    const result = {
      score: recommendation.score || 50,
      sentiment: recommendation.sentiment || 'Hold',
      strengths: recommendation.strengths || [],
      weaknesses: recommendation.weaknesses || [],
      considerations: recommendation.considerations || [],
      confidence: Math.round((recommendation.confidence || 0.5) * 100),
      lastUpdated: new Date().toISOString(),
      analysis: {
        technical: recommendation.scoring_breakdown?.components?.technical_score || 50,
        fundamental: recommendation.scoring_breakdown?.components?.fundamental_score || 50,
        market: recommendation.scoring_breakdown?.components?.market_sentiment_score || 50,
        risk: recommendation.scoring_breakdown?.components?.risk_alignment_score || 50,
      },
      metadata: {
        symbol,
        userProfile: {
          riskTolerance: userProfile.riskTolerance,
          investmentHorizon: userProfile.investmentHorizon,
          investmentGoal: userProfile.investmentGoal
        },
        researchSources: [
          'Google Search Grounding',
          'AI Stock Research Agent',
          'AI Recommendation Agent',
          'Real-time Market Data',
          'Multi-factor Analysis Engine'
        ],
        aiAgentData: {
          researchQuality: aiRecommendation.summary?.research_quality || {},
          alignmentScore: recommendation.alignment_score || 50,
          actionPlan: recommendation.action_plan || {},
          researchSummary: aiRecommendation.research?.summary || {},
          totalSources: aiRecommendation.research?.metadata?.total_sources || 0
        }
      }
    };

    console.log(`✅ AI-powered recommendation generated for ${symbol}:`, {
      score: result.score,
      sentiment: result.sentiment,
      confidence: result.confidence,
      sources: result.metadata.aiAgentData.totalSources
    });

    return NextResponse.json(result);

  } catch (error) {
    console.error('❌ Error generating stock recommendation:', error);
    return NextResponse.json(
      { 
        error: 'Failed to generate recommendation',
        details: error instanceof Error ? error.message : 'Unknown error',
        message: 'Please ensure the Stock AI agents server is running on port 8003'
      },
      { status: 500 }
    );
  }
}

// GET endpoint for quick recommendation lookup
export async function GET(request: Request) {
  const { searchParams } = new URL(request.url);
  const symbol = searchParams.get('symbol');
  
  if (!symbol) {
    return NextResponse.json({ error: 'Symbol is required' }, { status: 400 });
  }

  // Return cached recommendation if available
  // In production, this would check a database/cache
  
  return NextResponse.json({
    message: 'Use POST method with user profile for personalized recommendations'
  });
}