'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import MCPDataService from '@/services/mcpDataService';

// Particle Background Component
const ParticleBackground = () => {
  const [particles, setParticles] = useState<Array<{id: number, x: number, y: number, size: number, speed: number, opacity: number}>>([]);

  useEffect(() => {
    const newParticles = Array.from({ length: 80 }, (_, i) => ({
      id: i,
      x: Math.random() * 100,
      y: Math.random() * 100,
      size: Math.random() * 3 + 1,
      speed: Math.random() * 1.5 + 0.3,
      opacity: Math.random() * 0.5 + 0.1
    }));
    setParticles(newParticles);

    const interval = setInterval(() => {
      setParticles(prev => prev.map(particle => ({
        ...particle,
        y: particle.y > 105 ? -5 : particle.y + particle.speed * 0.1,
        opacity: Math.sin(Date.now() * 0.001 + particle.id) * 0.3 + 0.4
      })));
    }, 50);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="absolute inset-0 overflow-hidden pointer-events-none">
      {particles.map(particle => (
        <div
          key={particle.id}
          className="absolute bg-[rgb(0,184,153)] rounded-full"
          style={{
            left: `${particle.x}%`,
            top: `${particle.y}%`,
            width: `${particle.size}px`,
            height: `${particle.size}px`,
            opacity: particle.opacity,
            boxShadow: `0 0 ${particle.size * 2}px rgba(0,184,153,0.3)`
          }}
        />
      ))}
    </div>
  );
};

// Animated Counter Component
const AnimatedCounter = ({ 
  end, 
  duration = 2000, 
  prefix = '', 
  suffix = '',
  decimals = 0 
}: { 
  end: number, 
  duration?: number, 
  prefix?: string, 
  suffix?: string,
  decimals?: number 
}) => {
  const [count, setCount] = useState(0);
  const [isVisible, setIsVisible] = useState(false);
  const ref = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting && !isVisible) {
          setIsVisible(true);
        }
      },
      { threshold: 0.1 }
    );

    if (ref.current) {
      observer.observe(ref.current);
    }

    return () => observer.disconnect();
  }, [isVisible]);

  useEffect(() => {
    if (!isVisible) return;

    let startTime: number;
    const animate = (currentTime: number) => {
      if (!startTime) startTime = currentTime;
      const progress = Math.min((currentTime - startTime) / duration, 1);
      
      const easeOutQuart = 1 - Math.pow(1 - progress, 4);
      setCount(easeOutQuart * end);
      
      if (progress < 1) {
        requestAnimationFrame(animate);
      }
    };

    requestAnimationFrame(animate);
  }, [isVisible, end, duration]);

  const formatNumber = (num: number) => {
    if (decimals > 0) {
      return num.toFixed(decimals);
    }
    return Math.floor(num).toLocaleString();
  };

  return (
    <div ref={ref} className="text-4xl font-black text-[rgb(0,184,153)] mb-2 group-hover:scale-110 transition-transform duration-300">
      {prefix}{formatNumber(count)}{suffix}
    </div>
  );
};

// Interactive Feature Card Component
const InteractiveFeatureCard = ({ 
  icon, 
  title, 
  description, 
  delay = 0,
  gradient = 'from-[rgb(0,184,153)] to-[rgb(0,164,133)]',
  hoverColor = 'rgba(0,184,153,0.1)'
}: {
  icon: string,
  title: string,
  description: string,
  delay?: number,
  gradient?: string,
  hoverColor?: string
}) => {
  const [isHovered, setIsHovered] = useState(false);
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const cardRef = useRef<HTMLDivElement>(null);

  const handleMouseMove = (e: React.MouseEvent<HTMLDivElement>) => {
    if (!cardRef.current) return;
    const rect = cardRef.current.getBoundingClientRect();
    setMousePosition({
      x: e.clientX - rect.left,
      y: e.clientY - rect.top
    });
  };

  return (
    <div 
      ref={cardRef}
      className={`group relative bg-gradient-to-br from-[rgba(24,25,27,0.9)] to-[rgba(30,32,34,0.9)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 backdrop-blur-xl transition-all duration-500 hover:border-[rgba(0,184,153,0.5)] hover:shadow-2xl hover:shadow-[rgba(0,184,153,0.1)] hover:-translate-y-2 animate-fade-in cursor-pointer overflow-hidden`}
      style={{ animationDelay: `${delay}ms` }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onMouseMove={handleMouseMove}
    >
      {/* Dynamic gradient overlay */}
      <div className="absolute inset-0 bg-gradient-to-br from-[rgba(0,184,153,0.05)] to-transparent rounded-3xl opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
      
      {/* Mouse follow effect */}
      {isHovered && (
        <div 
          className="absolute w-40 h-40 rounded-full pointer-events-none transition-all duration-300 opacity-30"
          style={{
            left: mousePosition.x - 80,
            top: mousePosition.y - 80,
            background: `radial-gradient(circle, ${hoverColor} 0%, transparent 70%)`
          }}
        />
      )}
      
      {/* Floating particles on hover */}
      {isHovered && (
        <div className="absolute inset-0 pointer-events-none">
          {[...Array(6)].map((_, i) => (
            <div
              key={i}
              className="absolute w-1 h-1 bg-[rgb(0,184,153)] rounded-full animate-ping"
              style={{
                left: `${20 + i * 15}%`,
                top: `${30 + (i % 2) * 40}%`,
                animationDelay: `${i * 200}ms`,
                animationDuration: '2s'
              }}
            />
          ))}
        </div>
      )}
      
      <div className="relative z-10">
        <div className={`w-20 h-20 bg-gradient-to-br ${gradient} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg group-hover:scale-110 group-hover:rotate-3 transition-all duration-300`}>
          <span className="text-white font-bold text-lg">
            {title.split(' ').map(word => word[0]).join('')}
          </span>
        </div>
        <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-[rgb(0,184,153)] transition-colors duration-300">
          {title}
        </h3>
        <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
          {description}
        </p>
        
        {/* Floating action indicator */}
        <div className="absolute top-4 right-4 w-3 h-3 bg-[rgb(0,184,153)] rounded-full opacity-0 group-hover:opacity-100 animate-pulse transition-opacity duration-300"></div>
      </div>
    </div>
  );
};

// Floating Action Button Component
const FloatingActionButton = () => {
  const [isExpanded, setIsExpanded] = useState(false);
  const { dispatch } = useAppContext();

  const actions = [
    {
      text: "?",
      color: "bg-blue-600 hover:bg-blue-700",
      action: () => console.log('Help clicked')
    },
    {
      text: "C",
      color: "bg-green-600 hover:bg-green-700",
      action: () => dispatch({ type: 'SET_ACTIVE_TAB', payload: 'chat' })
    },
    {
      text: "P",
      color: "bg-purple-600 hover:bg-purple-700",
      action: () => dispatch({ type: 'SET_ACTIVE_TAB', payload: 'portfolio' })
    }
  ];

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <div className={`transition-all duration-300 ${isExpanded ? 'mb-4 space-y-3' : 'mb-0'}`}>
        {isExpanded && actions.map((action, i) => (
          <button
            key={i}
            onClick={action.action}
            className={`flex items-center justify-center w-12 h-12 ${action.color} text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 animate-fade-in hover:scale-110`}
            style={{ animationDelay: `${i * 100}ms` }}
          >
            <span className="text-lg font-bold">{action.text}</span>
          </button>
        ))}
      </div>
      
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className={`flex items-center justify-center w-14 h-14 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white rounded-full shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-110 ${isExpanded ? 'rotate-45' : ''}`}
      >
        <span className="text-2xl font-bold">{isExpanded ? '×' : '+'}</span>
      </button>
    </div>
  );
};

// Interactive Demo Preview Component
const InteractiveDemoPreview = () => {
  const [currentDemo, setCurrentDemo] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  
  const demos = [
    { 
      title: 'Portfolio Tracking', 
      description: 'Real-time portfolio monitoring with live updates',
      text: "PT",
      color: "from-blue-500 to-blue-600"
    },
    { 
      title: 'AI Chat Assistant', 
      description: 'Get instant financial advice from AI',
      text: "AI",
      color: "from-green-500 to-green-600"
    },
    { 
      title: 'Smart Analytics', 
      description: 'Advanced market insights and predictions',
      text: "SA",
      color: "from-purple-500 to-purple-600"
    }
  ];

  useEffect(() => {
    if (!isPlaying) return;
    
    const interval = setInterval(() => {
      setCurrentDemo((prev) => (prev + 1) % demos.length);
    }, 4000);
    
    return () => clearInterval(interval);
  }, [isPlaying]);

  return (
    <div className="relative max-w-4xl mx-auto mb-20">
      <div className="bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 backdrop-blur-xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-500">
        <div className="flex items-center justify-between mb-6">
          <h3 className="text-3xl font-bold text-white">
            See Artha AI in Action
          </h3>
          <button
            onClick={() => setIsPlaying(!isPlaying)}
            className="p-2 bg-[rgba(0,184,153,0.2)] hover:bg-[rgba(0,184,153,0.3)] rounded-lg transition-colors duration-300"
          >
            <span className="text-[rgb(0,184,153)] font-bold text-lg">
              {isPlaying ? '||' : '▶'}
            </span>
          </button>
        </div>
        
        <div className="relative h-64 bg-[rgba(30,32,34,0.8)] rounded-2xl overflow-hidden">
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="text-center animate-fade-in" key={currentDemo}>
              <div className={`w-16 h-16 bg-gradient-to-br ${demos[currentDemo].color} rounded-2xl flex items-center justify-center mx-auto mb-4 shadow-lg`}>
                <span className="text-white font-bold text-xl">{demos[currentDemo].text}</span>
              </div>
              <h4 className="text-xl font-bold text-white mb-2">{demos[currentDemo].title}</h4>
              <p className="text-gray-300">{demos[currentDemo].description}</p>
            </div>
          </div>
          
          <div className="absolute bottom-4 left-1/2 transform -translate-x-1/2 flex space-x-2">
            {demos.map((_, index) => (
              <button
                key={index}
                onClick={() => {
                  setCurrentDemo(index);
                  setIsPlaying(false);
                }}
                className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 ${
                  index === currentDemo ? 'bg-[rgb(0,184,153)]' : 'bg-gray-600 hover:bg-gray-500'
                }`}
              />
            ))}
          </div>
        </div>
      </div>
    </div>
  );
};

// Typewriter Effect Component
const TypewriterEffect = ({ phrases, speed = 100 }: { phrases: string[], speed?: number }) => {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);

  useEffect(() => {
    const currentPhrase = phrases[currentPhraseIndex];
    
    const timeout = setTimeout(() => {
      if (!isDeleting) {
        if (currentText.length < currentPhrase.length) {
          setCurrentText(currentPhrase.slice(0, currentText.length + 1));
        } else {
          setTimeout(() => setIsDeleting(true), 2000);
        }
      } else {
        if (currentText.length > 0) {
          setCurrentText(currentText.slice(0, -1));
        } else {
          setIsDeleting(false);
          setCurrentPhraseIndex((prev) => (prev + 1) % phrases.length);
        }
      }
    }, isDeleting ? speed / 2 : speed);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, currentPhraseIndex, phrases, speed]);

  return (
    <span className="text-[rgb(0,184,153)]">
      {currentText}
      <span className="animate-pulse">|</span>
    </span>
  );
};

// Main Enhanced Landing Page Component
const EnhancedLandingPage = () => {
  const { dispatch } = useAppContext();
  const mcpService = MCPDataService.getInstance();

  const handleDemoMode = () => {
    console.log('🎭 Activating demo mode...');
    sessionStorage.setItem('demoMode', 'true');
    dispatch({ type: 'SET_DEMO_MODE', payload: true });
    dispatch({ type: 'SET_AUTHENTICATED', payload: true });
    mcpService.setDemoMode(true);
  };

  const handleCreateProfile = () => {
    dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true });
  };

  return (
    <div className="relative min-h-screen">
      {/* Particle Background */}
      <ParticleBackground />
      
      {/* Enhanced Hero Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32">
        <div className="text-center">
          {/* Animated Badge */}
          <div className="inline-flex items-center px-6 py-3 mb-8 bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.3)] rounded-full backdrop-blur-sm animate-fade-in">
            <span className="w-2 h-2 bg-[rgb(0,184,153)] rounded-full mr-3 animate-pulse"></span>
            <span className="text-sm font-semibold text-[rgb(0,184,153)]">AI-Powered Financial Intelligence</span>
          </div>

          {/* Main Heading with Typewriter Effect */}
          <h1 className="text-6xl md:text-7xl lg:text-8xl font-black mb-8 leading-tight animate-fade-in">
            <span className="block text-white">Your Future</span>
            <span className="block bg-gradient-to-r from-[rgb(0,184,153)] via-[rgb(0,204,173)] to-[rgb(0,164,133)] bg-clip-text text-transparent">
              <TypewriterEffect phrases={['Wealth Engine', 'Investment Partner', 'Financial Advisor', 'Success Story']} />
            </span>
          </h1>

          {/* Enhanced Subtitle */}
          <p className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-12 animate-fade-in delay-300">
            Experience the next generation of financial intelligence. Get 
            <span className="text-[rgb(0,184,153)] font-semibold"> AI-powered insights</span>, 
            <span className="text-[rgb(0,184,153)] font-semibold"> real-time portfolio tracking</span>, and 
            <span className="text-[rgb(0,184,153)] font-semibold"> personalized investment strategies</span> 
            that adapt to your goals.
          </p>
          
          {/* Enhanced CTA Buttons */}
          <div className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16 animate-fade-in delay-500">
            <button
              onClick={handleDemoMode}
              className="group relative px-10 py-5 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white font-bold text-lg rounded-2xl overflow-hidden transition-all duration-500 transform hover:scale-105 hover:shadow-2xl hover:shadow-[rgba(0,184,153,0.3)]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[rgb(0,164,133)] to-[rgb(0,144,113)] opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              <span className="relative flex items-center">
                      Experience Demo
                    </span>
            </button>
            
            <button
              onClick={handleCreateProfile}
              className="group px-10 py-5 bg-transparent border-2 border-[rgb(0,184,153)] text-[rgb(0,184,153)] font-bold text-lg rounded-2xl transition-all duration-500 hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgb(0,204,173)] hover:text-[rgb(0,204,173)] hover:shadow-lg hover:shadow-[rgba(0,184,153,0.2)]"
            >
              <span className="flex items-center">
                    Create Profile
                  </span>
            </button>
          </div>

          {/* Enhanced Trust Indicators */}
          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400 animate-fade-in delay-700">
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-green-400 rounded-full mr-2 animate-pulse group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-green-400 transition-colors duration-300">Real-time Data</span>
            </div>
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse delay-200 group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-blue-400 transition-colors duration-300">Bank-grade Security</span>
            </div>
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse delay-400 group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-purple-400 transition-colors duration-300">AI-Powered Insights</span>
            </div>
          </div>
        </div>
      </div>

      {/* Enhanced Features Grid */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
            Powerful Features for 
            <span className="block bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] bg-clip-text text-transparent">
              Smart Investors
            </span>
          </h2>
          <p className="text-xl text-gray-300 max-w-3xl mx-auto">
            Everything you need to make informed financial decisions and grow your wealth
          </p>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          <InteractiveFeatureCard
            icon="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
            title="Real-Time Portfolio"
            description="Live tracking of your investments, mutual funds, and bank accounts with Fi Money integration. Get instant updates and never miss a market movement."
            delay={0}
          />
          
          <InteractiveFeatureCard
            icon="M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z"
            title="AI Financial Advisor"
            description="Get personalized investment recommendations and financial planning advice powered by advanced AI. Your digital wealth manager that never sleeps."
            delay={200}
            gradient="from-purple-500 to-purple-600"
            hoverColor="rgba(147,51,234,0.1)"
          />
          
          <InteractiveFeatureCard
            icon="M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
            title="Smart Analytics"
            description="Comprehensive insights into your financial health with performance tracking and goal monitoring. Turn data into actionable investment strategies."
            delay={400}
            gradient="from-blue-500 to-blue-600"
            hoverColor="rgba(59,130,246,0.1)"
          />
        </div>
      </div>

      {/* Interactive Demo Preview */}
      <InteractiveDemoPreview />

      {/* Enhanced Stats Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div className="bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-12 backdrop-blur-xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-500">
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            <div className="group cursor-pointer">
              <AnimatedCounter end={10000} suffix="+" />
              <div className="text-gray-300 font-semibold group-hover:text-white transition-colors duration-300">Active Users</div>
            </div>
            <div className="group cursor-pointer">
              <AnimatedCounter end={50} prefix="₹" suffix="Cr+" />
              <div className="text-gray-300 font-semibold group-hover:text-white transition-colors duration-300">Assets Tracked</div>
            </div>
            <div className="group cursor-pointer">
              <AnimatedCounter end={99.9} suffix="%" decimals={1} />
              <div className="text-gray-300 font-semibold group-hover:text-white transition-colors duration-300">Uptime</div>
            </div>
            <div className="group cursor-pointer">
              <div className="text-4xl font-black text-[rgb(0,184,153)] mb-2 group-hover:scale-110 transition-transform duration-300">24/7</div>
              <div className="text-gray-300 font-semibold group-hover:text-white transition-colors duration-300">AI Support</div>
            </div>
          </div>
        </div>
      </div>

      {/* Floating Action Button */}
      <FloatingActionButton />
    </div>
  );
};

export default EnhancedLandingPage;