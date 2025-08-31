'use client';

import React, { useState, useEffect, useRef } from 'react';
import { useAppContext } from '@/contexts/AppContext';
import MCPDataService from '@/services/mcpDataService';

// Interactive Typewriter Effect Component
const TypewriterEffect = ({ phrases }: { phrases: string[] }) => {
  const [currentPhraseIndex, setCurrentPhraseIndex] = useState(0);
  const [currentText, setCurrentText] = useState('');
  const [isDeleting, setIsDeleting] = useState(false);
  const [isPaused, setIsPaused] = useState(false);

  useEffect(() => {
    const currentPhrase = phrases[currentPhraseIndex];
    
    const timeout = setTimeout(() => {
      if (isPaused) {
        setIsPaused(false);
        setIsDeleting(true);
        return;
      }

      if (isDeleting) {
        setCurrentText(currentPhrase.substring(0, currentText.length - 1));
        if (currentText === '') {
          setIsDeleting(false);
          setCurrentPhraseIndex((prev) => (prev + 1) % phrases.length);
        }
      } else {
        setCurrentText(currentPhrase.substring(0, currentText.length + 1));
        if (currentText === currentPhrase) {
          setIsPaused(true);
        }
      }
    }, isDeleting ? 50 : isPaused ? 2000 : 100);

    return () => clearTimeout(timeout);
  }, [currentText, isDeleting, isPaused, currentPhraseIndex, phrases]);

  return (
    <span className="inline-block">
      {currentText}
      <span className="animate-pulse text-[rgb(0,184,153)]">|</span>
    </span>
  );
};

// Interactive Progress Ring Component
const ProgressRing = ({ progress, size = 120, strokeWidth = 8 }: { progress: number, size?: number, strokeWidth?: number }) => {
  const radius = (size - strokeWidth) / 2;
  const circumference = radius * 2 * Math.PI;
  const strokeDasharray = `${circumference} ${circumference}`;
  const strokeDashoffset = circumference - (progress / 100) * circumference;

  return (
    <div className="relative inline-flex items-center justify-center">
      <svg className="transform -rotate-90" width={size} height={size}>
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgba(0,184,153,0.2)"
          strokeWidth={strokeWidth}
          fill="transparent"
        />
        <circle
          cx={size / 2}
          cy={size / 2}
          r={radius}
          stroke="rgb(0,184,153)"
          strokeWidth={strokeWidth}
          fill="transparent"
          strokeDasharray={strokeDasharray}
          strokeDashoffset={strokeDashoffset}
          strokeLinecap="round"
          className="transition-all duration-1000 ease-out"
        />
      </svg>
      <div className="absolute inset-0 flex items-center justify-center">
        <span className="text-2xl font-bold text-[rgb(0,184,153)]">{Math.round(progress)}%</span>
      </div>
    </div>
  );
};

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

// Interactive Stats Card Component
const InteractiveStatsCard = ({ 
  value, 
  label, 
  prefix = '', 
  suffix = '', 
  decimals = 0,
  icon,
  color = 'rgb(0,184,153)',
  delay = 0 
}: {
  value: number,
  label: string,
  prefix?: string,
  suffix?: string,
  decimals?: number,
  icon: string,
  color?: string,
  delay?: number
}) => {
  const [isHovered, setIsHovered] = useState(false);
  
  return (
    <div 
      className="group cursor-pointer transform transition-all duration-500 hover:scale-105 animate-fade-in"
      style={{ animationDelay: `${delay}ms` }}
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
    >
      <div className="relative bg-gradient-to-br from-[rgba(24,25,27,0.8)] to-[rgba(30,32,34,0.8)] border border-[rgba(0,184,153,0.2)] rounded-2xl p-6 backdrop-blur-xl group-hover:border-[rgba(0,184,153,0.5)] group-hover:shadow-2xl group-hover:shadow-[rgba(0,184,153,0.1)] transition-all duration-500">
        {/* Icon */}
        <div className={`w-12 h-12 rounded-xl flex items-center justify-center mb-4 transition-all duration-300 group-hover:scale-110`} style={{ backgroundColor: `${color}20` }}>
          <svg className="w-6 h-6" style={{ color }} fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={icon} />
          </svg>
        </div>
        
        {/* Animated Counter */}
        <AnimatedCounter 
          end={value} 
          prefix={prefix} 
          suffix={suffix} 
          decimals={decimals}
        />
        
        {/* Label */}
        <div className="text-gray-300 font-semibold group-hover:text-white transition-colors duration-300">
          {label}
        </div>
        
        {/* Hover effect overlay */}
        {isHovered && (
          <div className="absolute inset-0 bg-gradient-to-br from-[rgba(0,184,153,0.05)] to-transparent rounded-2xl pointer-events-none" />
        )}
      </div>
    </div>
  );
};

// Interactive Testimonial Carousel Component
const InteractiveTestimonialCarousel = () => {
  const [currentTestimonial, setCurrentTestimonial] = useState(0);
  const [isAutoPlay, setIsAutoPlay] = useState(true);
  
  const testimonials = [
    {
      name: "Rajesh Kumar",
      role: "Investment Analyst",
      content: "Artha AI has transformed how I track my portfolio. The real-time insights are incredible!",
      rating: 5,
      avatar: "RK"
    },
    {
      name: "Priya Sharma",
      role: "Financial Advisor",
      content: "The AI-powered recommendations have helped my clients make better investment decisions.",
      rating: 5,
      avatar: "PS"
    },
    {
      name: "Amit Patel",
      role: "Retail Investor",
      content: "Simple, powerful, and reliable. Exactly what I needed for managing my investments.",
      rating: 5,
      avatar: "AP"
    }
  ];

  useEffect(() => {
    if (!isAutoPlay) return;
    
    const interval = setInterval(() => {
      setCurrentTestimonial((prev) => (prev + 1) % testimonials.length);
    }, 5000);
    
    return () => clearInterval(interval);
  }, [isAutoPlay]);

  return (
    <div className="relative max-w-4xl mx-auto mb-20">
      <div className="text-center mb-12">
        <h3 className="text-4xl font-bold text-white mb-4">
          What Our Users Say
        </h3>
        <p className="text-xl text-gray-300">
          Join thousands of satisfied investors
        </p>
      </div>
      
      <div className="relative bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 backdrop-blur-xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-500">
        <div className="text-center">
          {/* Avatar */}
          <div className="w-20 h-20 bg-gradient-to-br from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-full flex items-center justify-center mx-auto mb-6 shadow-lg transform hover:scale-110 transition-all duration-300">
            <span className="text-white font-bold text-xl">
              {testimonials[currentTestimonial].avatar}
            </span>
          </div>
          
          {/* Stars */}
          <div className="flex justify-center mb-4">
            {[...Array(testimonials[currentTestimonial].rating)].map((_, i) => (
              <svg key={i} className="w-5 h-5 text-yellow-400 animate-pulse" style={{ animationDelay: `${i * 100}ms` }} fill="currentColor" viewBox="0 0 20 20">
                <path d="M9.049 2.927c.3-.921 1.603-.921 1.902 0l1.07 3.292a1 1 0 00.95.69h3.462c.969 0 1.371 1.24.588 1.81l-2.8 2.034a1 1 0 00-.364 1.118l1.07 3.292c.3.921-.755 1.688-1.54 1.118l-2.8-2.034a1 1 0 00-1.175 0l-2.8 2.034c-.784.57-1.838-.197-1.539-1.118l1.07-3.292a1 1 0 00-.364-1.118L2.98 8.72c-.783-.57-.38-1.81.588-1.81h3.461a1 1 0 00.951-.69l1.07-3.292z" />
              </svg>
            ))}
          </div>
          
          {/* Content */}
          <blockquote className="text-xl text-gray-200 mb-6 italic leading-relaxed">
            "{testimonials[currentTestimonial].content}"
          </blockquote>
          
          {/* Author */}
          <div className="text-center">
            <p className="text-lg font-bold text-white">
              {testimonials[currentTestimonial].name}
            </p>
            <p className="text-[rgb(0,184,153)]">
              {testimonials[currentTestimonial].role}
            </p>
          </div>
        </div>
        
        {/* Navigation */}
        <div className="flex justify-center mt-8 space-x-2">
          {testimonials.map((_, index) => (
            <button
              key={index}
              onClick={() => {
                setCurrentTestimonial(index);
                setIsAutoPlay(false);
                setTimeout(() => setIsAutoPlay(true), 3000);
              }}
              className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 ${
                index === currentTestimonial 
                  ? 'bg-[rgb(0,184,153)] scale-125 shadow-lg shadow-[rgba(0,184,153,0.5)]' 
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};

// Interactive Demo Preview Component
const InteractiveDemoPreview = ({ onDemoClick }: { onDemoClick: () => void }) => {
  const [currentDemo, setCurrentDemo] = useState(0);
  const [isPlaying, setIsPlaying] = useState(true);
  const [isHovered, setIsHovered] = useState(false);
  
  const demos = [
    { 
      title: 'Portfolio Tracking', 
      description: 'Real-time portfolio monitoring with live updates',
      icon: "M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z",
      color: "from-blue-500 to-blue-600"
    },
    { 
      title: 'AI Chat Assistant', 
      description: 'Get instant financial advice from AI',
      icon: "M8 12h.01M12 12h.01M16 12h.01M21 12c0 4.418-4.03 8-9 8a9.863 9.863 0 01-4.255-.949L3 20l1.395-3.72C3.512 15.042 3 13.574 3 12c0-4.418 4.03-8 9-8s9 3.582 9 8z",
      color: "from-[#cca695] to-[#b8956a]"
    },
    { 
      title: 'Smart Analytics', 
      description: 'Advanced market insights and predictions',
      icon: "M16 8v8m-4-5v5m-4-2v2m-2 4h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z",
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
      <div 
        className="bg-gradient-to-r from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 backdrop-blur-xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-500 cursor-pointer group"
        onClick={onDemoClick}
      >
        <div className="flex items-center justify-center mb-6">
          <h3 className="text-3xl font-bold text-white group-hover:text-[rgb(0,184,153)] transition-colors duration-300">
            Experience Our Features
          </h3>
        </div>
        
        <div 
          className="relative h-64 bg-[rgba(24,25,27,0.5)] rounded-2xl overflow-hidden group-hover:bg-[rgba(24,25,27,0.7)] transition-all duration-500"
          onMouseEnter={() => setIsHovered(true)}
          onMouseLeave={() => setIsHovered(false)}
        >
          {/* Background particles */}
          <div className="absolute inset-0">
            {[...Array(8)].map((_, i) => (
              <div
                key={i}
                className="absolute w-1 h-1 bg-[rgb(0,184,153)] rounded-full animate-ping opacity-30"
                style={{
                  left: `${20 + i * 10}%`,
                  top: `${30 + (i % 3) * 20}%`,
                  animationDelay: `${i * 500}ms`,
                  animationDuration: '3s'
                }}
              />
            ))}
          </div>
          
          <div className="absolute inset-0 flex items-center justify-center">
            <div className={`relative w-32 h-32 bg-gradient-to-br ${demos[currentDemo].color} rounded-3xl flex items-center justify-center transform transition-all duration-1000 hover:scale-110 hover:rotate-3 shadow-2xl`}>
              {/* Icon */}
              <svg className="w-12 h-12 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d={demos[currentDemo].icon} />
              </svg>
              
              {/* Floating elements */}
              <div className="absolute -top-2 -right-2 w-4 h-4 bg-white rounded-full animate-bounce opacity-80" />
              <div className="absolute -bottom-2 -left-2 w-3 h-3 bg-white rounded-full animate-bounce opacity-60" style={{ animationDelay: '0.5s' }} />
            </div>
          </div>
          
          <div className="absolute bottom-6 left-6 right-6">
            <h4 className="text-xl font-bold text-white mb-2 group-hover:text-[rgb(0,184,153)] transition-colors duration-300">
              {demos[currentDemo].title}
            </h4>
            <p className="text-gray-300 group-hover:text-gray-200 transition-colors duration-300">
              {demos[currentDemo].description}
            </p>
          </div>
          
          {/* Progress bar */}
          <div className="absolute top-4 left-4 right-4 h-1 bg-[rgba(255,255,255,0.1)] rounded-full overflow-hidden">
            <div 
              className="h-full bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] rounded-full transition-all duration-4000 ease-linear"
              style={{ 
                width: isPlaying && !isHovered ? '100%' : '0%',
                transitionDuration: isPlaying && !isHovered ? '4000ms' : '300ms'
              }}
            />
          </div>
        </div>
        
        <div className="flex justify-center mt-6 space-x-2">
          {demos.map((_, index) => (
            <button
              key={index}
              onClick={() => setCurrentDemo(index)}
              className={`w-3 h-3 rounded-full transition-all duration-300 hover:scale-125 ${
                index === currentDemo 
                  ? 'bg-[rgb(0,184,153)] scale-125 shadow-lg shadow-[rgba(0,184,153,0.5)]' 
                  : 'bg-gray-600 hover:bg-gray-500'
              }`}
            />
          ))}
        </div>
      </div>
    </div>
  );
};



// Main Enhanced Landing Page Component
const EnhancedLandingPage = ({ 
  onDemoActivate, 
  setHasVisited 
}: { 
  onDemoActivate?: () => void;
  setHasVisited?: (visited: boolean) => void;
}) => {
  const { dispatch } = useAppContext();
  const mcpService = MCPDataService.getInstance();

  const handleDemoMode = async () => {
    console.log('🎭 DEMO MODE ACTIVATION - SETTING UP DEMO STATE');
    
    // Set demo mode in session storage
    sessionStorage.setItem('demoMode', 'true');
    sessionStorage.setItem('hasVisited', 'true');
    
    // Update parent component's hasVisited state
    setHasVisited?.(true);

    // Dispatch demo mode and authentication states
    dispatch({ type: 'SET_DEMO_MODE', payload: true });
    dispatch({ type: 'SET_AUTHENTICATED', payload: true });
    dispatch({ type: 'SET_LOGGED_IN', payload: false }); // Demo users are not logged in
    
    // Configure MCP service for demo mode
    mcpService.setDemoMode(true);
    
    // Make sure to update the parent state through the callback
    onDemoActivate?.();

    console.log('🎭 DEMO MODE FULLY ACTIVATED - SHOULD SHOW DASHBOARD');
  };

  const handleCreateProfile = () => {
    dispatch({ type: 'SET_SHOW_SIGNUP_FORM', payload: true });
  };

  const handleSignIn = () => {
    // Set auth mode to login and show the signup form in login mode
    dispatch({ type: 'SET_AUTH_MODE', payload: 'login' });
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
          <div className="flex flex-col sm:flex-row gap-4 justify-center items-center mb-16 animate-fade-in delay-500">
            <button
              onClick={handleDemoMode}
              className="group relative px-8 py-4 bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] text-white font-bold text-lg rounded-2xl overflow-hidden transition-all duration-500 transform hover:scale-105 hover:shadow-2xl hover:shadow-[rgba(0,184,153,0.3)]"
            >
              <div className="absolute inset-0 bg-gradient-to-r from-[rgb(0,164,133)] to-[rgb(0,144,113)] opacity-0 group-hover:opacity-100 transition-opacity duration-500"></div>
              <div className="absolute inset-0 bg-white opacity-0 group-hover:opacity-20 transition-opacity duration-300"></div>
              <span className="relative flex items-center">
                <span className="mr-3 text-xl">🎭</span>
                Experience Demo
              </span>
            </button>

            <button
              onClick={handleCreateProfile}
              className="group px-8 py-4 bg-transparent border-2 border-[rgb(0,184,153)] text-[rgb(0,184,153)] font-bold text-lg rounded-2xl transition-all duration-500 hover:bg-[rgba(0,184,153,0.1)] hover:border-[rgb(0,204,173)] hover:text-[rgb(0,204,173)] hover:shadow-lg hover:shadow-[rgba(0,184,153,0.2)]"
            >
              <span className="flex items-center">
                <span className="mr-3 text-xl">👤</span>
                Create Profile
              </span>
            </button>
            
            <button
              onClick={handleSignIn}
              className="group px-8 py-4 bg-transparent border-2 border-blue-400 text-blue-400 font-bold text-lg rounded-2xl transition-all duration-500 hover:bg-[rgba(59,130,246,0.1)] hover:border-blue-300 hover:text-blue-300 hover:shadow-lg hover:shadow-[rgba(59,130,246,0.2)]"
            >
              <span className="flex items-center">
                <span className="mr-3 text-xl">🔑</span>
                Sign In
              </span>
            </button>
          </div>

          {/* Enhanced Trust Indicators */}
          <div className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400 animate-fade-in delay-700">
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-[#cca695] rounded-full mr-2 animate-pulse group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-[#cca695] transition-colors duration-300">Real-time Data</span>
            </div>
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-blue-400 rounded-full mr-2 animate-pulse delay-200 group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-blue-400 transition-colors duration-300">Secure & Reliable</span>
            </div>
            <div className="flex items-center group cursor-pointer">
              <span className="w-2 h-2 bg-purple-400 rounded-full mr-2 animate-pulse delay-400 group-hover:scale-150 transition-transform duration-300"></span>
              <span className="group-hover:text-purple-400 transition-colors duration-300">AI-Powered</span>
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
          <div className="group relative bg-gradient-to-br from-[rgba(0,184,153,0.1)] to-[rgba(0,164,133,0.1)] border border-[rgba(0,184,153,0.2)] rounded-3xl p-8 backdrop-blur-xl hover:border-[rgba(0,184,153,0.4)] transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-[rgba(0,184,153,0.2)]">
            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-[rgb(0,184,153)] transition-colors duration-300">
              Real-Time Portfolio
            </h3>
            <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
              Live tracking of your investments, mutual funds, and bank accounts with Fi Money integration. Get instant updates and never miss a market movement.
            </p>
          </div>
          
          <div className="group relative bg-gradient-to-br from-purple-500/10 to-purple-600/10 border border-purple-500/20 rounded-3xl p-8 backdrop-blur-xl hover:border-purple-500/40 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-purple-500/20">
            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-purple-400 transition-colors duration-300">
              AI Financial Advisor
            </h3>
            <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
              Get personalized investment recommendations and financial planning advice powered by advanced AI. Your digital wealth manager that never sleeps.
            </p>
          </div>
          
          <div className="group relative bg-gradient-to-br from-blue-500/10 to-blue-600/10 border border-blue-500/20 rounded-3xl p-8 backdrop-blur-xl hover:border-blue-500/40 transition-all duration-500 hover:scale-105 hover:shadow-2xl hover:shadow-blue-500/20">
            <h3 className="text-2xl font-bold text-white mb-4 group-hover:text-blue-400 transition-colors duration-300">
              Smart Analytics
            </h3>
            <p className="text-gray-300 leading-relaxed group-hover:text-gray-200 transition-colors duration-300">
              Comprehensive insights into your financial health with performance tracking and goal monitoring. Turn data into actionable investment strategies.
            </p>
          </div>
        </div>
      </div>

      {/* Interactive Demo Preview */}
      <InteractiveDemoPreview onDemoClick={handleDemoMode} />

      {/* Artha AI Image Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div className="flex justify-center">
          <img 
            src="/ArthaAi.svg" 
            alt="Artha AI" 
            className="max-w-full h-auto rounded-3xl shadow-2xl hover:scale-105 transition-transform duration-500"
            style={{ maxHeight: '600px' }}
          />
        </div>
      </div>

      {/* About Artha Section */}
      <div className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32">
        <div className="text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black text-white mb-6">
            About 
            <span className="bg-gradient-to-r from-[rgb(0,184,153)] to-[rgb(0,164,133)] bg-clip-text text-transparent">
              Artha
            </span>
          </h2>
          <p className="text-xl text-gray-300 max-w-4xl mx-auto leading-relaxed">
            Artha AI is your intelligent financial companion that connects with Fi Money to provide real-time portfolio analysis, 
            personalized investment recommendations, and AI-powered financial insights. Get comprehensive wealth management 
            with automated portfolio tracking, risk assessment, and strategic investment guidance tailored to your goals.
          </p>
        </div>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
          <InteractiveStatsCard
            value={1}
            suffix=""
            label="Secure Platform"
            icon="M12 15v2m-6 4h12a2 2 0 002-2v-6a2 2 0 00-2-2H6a2 2 0 00-2 2v6a2 2 0 002 2zm10-10V7a4 4 0 00-8 0v4h8z"
            color="rgb(0,184,153)"
            delay={0}
          />
          <InteractiveStatsCard
            value={1}
            suffix=""
            label="Artha AI"
            icon="M9.75 17L9 20l-1 1h8l-1-1-.75-3M3 13h18M5 17h14a2 2 0 002-2V5a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"
            color="rgb(34,197,94)"
            delay={200}
          />
        </div>
      </div>
    </div>
  );
};

export default EnhancedLandingPage;