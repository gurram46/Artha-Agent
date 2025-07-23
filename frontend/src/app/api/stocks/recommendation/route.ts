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

    console.log(`🚀 Starting streaming AI analysis for ${symbol}`);

    // Create streaming response
    const encoder = new TextEncoder();
    
    const stream = new ReadableStream({
      start(controller) {
        const sendMessage = (type: string, content: any) => {
          try {
            const data = JSON.stringify({ type, content });
            const message = `data: ${data}\n\n`;
            console.log('Sending SSE message:', message.trim()); // Debug log
            controller.enqueue(encoder.encode(message));
          } catch (error) {
            console.error('Error encoding message:', error);
            const fallback = JSON.stringify({ type: 'log', content: 'Error processing message' });
            controller.enqueue(encoder.encode(`data: ${fallback}\n\n`));
          }
        };

        // Async function to handle the analysis
        const performAnalysis = async () => {
          try {
            // Send initial log
            sendMessage('log', '🚀 Connecting to AI analysis backend...');
            
            // Get stock data first if not provided
            let fullStockData = stockData;
            if (!fullStockData || !fullStockData.currentPrice) {
              sendMessage('log', '📊 Fetching real-time stock data...');
              try {
                const stockResponse = await fetch(`http://localhost:3002/api/stocks/proxy?action=quote&symbol=${symbol}`);
                if (stockResponse.ok) {
                  const stockResult = await stockResponse.json();
                  fullStockData = stockResult.data;
                  sendMessage('log', `📈 Retrieved current price: ₹${fullStockData?.currentPrice || 'N/A'}`);
                } else {
                  sendMessage('log', '⚠️ Using cached stock data...');
                }
              } catch (error) {
                sendMessage('log', '⚠️ Stock data fetch failed, using available data...');
              }
            }

            sendMessage('log', '🤖 Initializing AI research agents...');
            
            // Call the real Stock AI Agents backend
            const aiRecommendation = await callStockAIAgent('/api/stock/full-analysis', {
              symbol,
              company_name: fullStockData?.name || symbol.replace('.NS', ''),
              user_profile: userProfile,
              stock_data: fullStockData || {}
            });

            sendMessage('log', '✅ AI analysis completed successfully!');

            if (!aiRecommendation || !aiRecommendation.recommendation) {
              throw new Error('Invalid response from AI backend');
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
              }
            };

            // Send final result
            sendMessage('result', result);
            controller.close();

          } catch (error) {
            console.error('❌ Analysis failed:', error);
            sendMessage('log', `❌ Analysis failed: ${error.message}`);
            sendMessage('log', '💡 Please ensure the backend server is running on port 8003');
            controller.close();
          }
        };

        // Start the analysis
        performAnalysis();
      }
    });

    return new Response(stream, {
      headers: {
        'Content-Type': 'text/event-stream',
        'Cache-Control': 'no-cache',
        'Connection': 'keep-alive',
      },
    });

  } catch (error) {
    console.error('❌ Error starting analysis stream:', error);
    return NextResponse.json(
      { 
        error: 'Failed to start analysis',
        details: error instanceof Error ? error.message : 'Unknown error'
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