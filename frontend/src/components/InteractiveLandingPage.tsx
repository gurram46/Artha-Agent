'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence, useInView, useMotionValue, useSpring } from 'framer-motion';
import { ArthaLogo } from './ui/ArthaLogo';

interface InteractiveLandingPageProps {
  onDemoClick: () => void;
  onCreateProfileClick: () => void;
}

const InteractiveLandingPage: React.FC<InteractiveLandingPageProps> = ({
  onDemoClick,
  onCreateProfileClick
}) => {
  const [mousePosition, setMousePosition] = useState({ x: 0, y: 0 });
  const [isHovering, setIsHovering] = useState(false);
  const [currentFeature, setCurrentFeature] = useState(0);
  const [typedText, setTypedText] = useState('');
  const heroRef = useRef(null);
  const featuresRef = useRef(null);
  const statsRef = useRef(null);
  
  const isHeroInView = useInView(heroRef, { once: true });
  const isFeaturesInView = useInView(featuresRef, { once: true });
  const isStatsInView = useInView(statsRef, { once: true });

  const mouseX = useMotionValue(0);
  const mouseY = useMotionValue(0);
  const springX = useSpring(mouseX, { stiffness: 100, damping: 10 });
  const springY = useSpring(mouseY, { stiffness: 100, damping: 10 });

  // Typewriter effect
  const phrases = [
    "AI-Powered Financial Intelligence",
    "Real-Time Portfolio Tracking", 
    "Smart Investment Strategies",
    "Personalized Wealth Management"
  ];

  useEffect(() => {
    let currentPhrase = 0;
    let currentChar = 0;
    let isDeleting = false;

    const typeWriter = () => {
      const phrase = phrases[currentPhrase];
      
      if (!isDeleting && currentChar < phrase.length) {
        setTypedText(phrase.substring(0, currentChar + 1));
        currentChar++;
        setTimeout(typeWriter, 100);
      } else if (isDeleting && currentChar > 0) {
        setTypedText(phrase.substring(0, currentChar - 1));
        currentChar--;
        setTimeout(typeWriter, 50);
      } else if (!isDeleting && currentChar === phrase.length) {
        setTimeout(() => {
          isDeleting = true;
          typeWriter();
        }, 2000);
      } else if (isDeleting && currentChar === 0) {
        isDeleting = false;
        currentPhrase = (currentPhrase + 1) % phrases.length;
        setTimeout(typeWriter, 500);
      }
    };

    typeWriter();
  }, []);

  // Mouse tracking
  useEffect(() => {
    const handleMouseMove = (e: MouseEvent) => {
      setMousePosition({ x: e.clientX, y: e.clientY });
      mouseX.set(e.clientX);
      mouseY.set(e.clientY);
    };

    window.addEventListener('mousemove', handleMouseMove);
    return () => window.removeEventListener('mousemove', handleMouseMove);
  }, [mouseX, mouseY]);

  // Auto-rotate features
  useEffect(() => {
    const interval = setInterval(() => {
      setCurrentFeature((prev) => (prev + 1) % 3);
    }, 4000);
    return () => clearInterval(interval);
  }, []);

  const features = [
    {
      title: "Real-Time Portfolio",
      description: "Live tracking with instant updates",
      color: "from-blue-500 to-cyan-500"
    },
    {
      title: "AI Financial Advisor", 
      description: "Personalized investment recommendations",
      color: "from-purple-500 to-pink-500"
    },
    {
      title: "Smart Analytics",
      description: "Comprehensive financial insights",
      color: "from-[#cca695] to-[#b8956a]"
    }
  ];

  const stats = [
    { value: "10K+", label: "Active Users" },
    { value: "₹50Cr+", label: "Assets Tracked" },
    { value: "99.9%", label: "Uptime" },
    { value: "24/7", label: "AI Support" }
  ];

  return (
    <div className="min-h-screen bg-[rgb(0,26,30)] relative overflow-hidden">
      {/* Interactive Background */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        {/* Animated gradient orbs */}
        <motion.div
          className="absolute w-96 h-96 bg-gradient-to-br from-[#cca695] to-[#b8956a] rounded-full opacity-10 blur-3xl"
          animate={{
            x: [0, 100, 0],
            y: [0, -50, 0],
            scale: [1, 1.2, 1],
          }}
          transition={{
            duration: 8,
            repeat: Infinity,
            ease: "easeInOut"
          }}
          style={{
            top: '10%',
            right: '10%',
          }}
        />
        
        <motion.div
          className="absolute w-80 h-80 bg-gradient-to-tr from-[#cca695] to-[#b8956a] rounded-full opacity-5 blur-3xl"
          animate={{
            x: [0, -80, 0],
            y: [0, 60, 0],
            scale: [1, 0.8, 1],
          }}
          transition={{
            duration: 10,
            repeat: Infinity,
            ease: "easeInOut",
            delay: 2
          }}
          style={{
            bottom: '10%',
            left: '10%',
          }}
        />

        {/* Floating particles */}
        {Array.from({ length: 20 }).map((_, i) => (
          <motion.div
            key={i}
            className="absolute w-2 h-2 bg-[#cca695] rounded-full opacity-30"
            animate={{
              y: [0, -100, 0],
              opacity: [0.3, 0.8, 0.3],
            }}
            transition={{
              duration: 3 + Math.random() * 2,
              repeat: Infinity,
              delay: Math.random() * 2,
            }}
            style={{
              left: `${Math.random() * 100}%`,
              top: `${Math.random() * 100}%`,
            }}
          />
        ))}
      </div>

      {/* Interactive cursor follower */}
      <motion.div
        className="fixed w-6 h-6 bg-[#cca695] rounded-full pointer-events-none z-50 mix-blend-difference"
        style={{
          x: springX,
          y: springY,
          translateX: '-50%',
          translateY: '-50%',
        }}
        animate={{
          scale: isHovering ? 2 : 1,
          opacity: isHovering ? 0.8 : 0.5,
        }}
      />

      {/* Header */}
      <motion.header
        className="bg-[rgba(0,0,0,0.95)] backdrop-blur-2xl border-b border-[rgba(204,166,149,0.3)] sticky top-0 z-40 shadow-2xl"
        initial={{ y: -100 }}
        animate={{ y: 0 }}
        transition={{ duration: 0.8, ease: "easeOut" }}
      >
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex items-center justify-between h-20">
            <motion.div 
              className="flex items-center space-x-4 group cursor-pointer"
              whileHover={{ scale: 1.05 }}
              onHoverStart={() => setIsHovering(true)}
              onHoverEnd={() => setIsHovering(false)}
            >
              <motion.div
                className="relative w-14 h-14 bg-gradient-to-br from-[#cca695] to-[#b8956a] rounded-2xl flex items-center justify-center shadow-xl"
                whileHover={{ rotate: 360 }}
                transition={{ duration: 0.8 }}
              >
                <ArthaLogo className="text-white" size="lg" />
              </motion.div>
              <div>
                <h1 className="text-2xl font-black bg-gradient-to-r from-white to-gray-200 bg-clip-text text-transparent tracking-tight">
                  Artha AI
                </h1>
                <p className="text-xs text-[#cca695] font-semibold tracking-wide">
                  {typedText}<span className="animate-pulse">|</span>
                </p>
              </div>
            </motion.div>
            
            <div className="flex items-center space-x-4">
              <motion.button
                onClick={onDemoClick}
                className="group relative px-6 py-3 bg-transparent border-2 border-[#cca695] text-[#cca695] font-semibold rounded-xl overflow-hidden"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onHoverStart={() => setIsHovering(true)}
                onHoverEnd={() => setIsHovering(false)}
              >
                <motion.div
                  className="absolute inset-0 bg-[#cca695]"
                  initial={{ x: "-100%" }}
                  whileHover={{ x: 0 }}
                  transition={{ duration: 0.3 }}
                />
                <span className="relative z-10 flex items-center group-hover:text-white transition-colors">
                  <span className="mr-2 text-lg">Demo</span>
                  Try Demo
                </span>
              </motion.button>
              
              <motion.button
                onClick={onCreateProfileClick}
                className="group relative px-6 py-3 bg-gradient-to-r from-[#cca695] to-[#b8956a] text-white font-semibold rounded-xl overflow-hidden"
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onHoverStart={() => setIsHovering(true)}
                onHoverEnd={() => setIsHovering(false)}
              >
                <motion.div
                  className="absolute inset-0 bg-gradient-to-r from-[#b8956a] to-[#a8855a]"
                  initial={{ opacity: 0 }}
                  whileHover={{ opacity: 1 }}
                />
                <span className="relative z-10 flex items-center">
                  <span className="mr-3 text-xl">User</span>
                  Create Profile
                </span>
              </motion.button>
            </div>
          </div>
        </div>
      </motion.header>

      {/* Hero Section */}
      <motion.section
        ref={heroRef}
        className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-20 pb-32"
        initial={{ opacity: 0 }}
        animate={isHeroInView ? { opacity: 1 } : {}}
        transition={{ duration: 1 }}
      >
        <div className="text-center">
          <motion.div
            className="inline-flex items-center px-6 py-3 mb-8 bg-gradient-to-r from-[rgba(204,166,149,0.1)] to-[rgba(184,149,106,0.1)] border border-[rgba(204,166,149,0.3)] rounded-full backdrop-blur-sm"
            initial={{ y: 50, opacity: 0 }}
            animate={isHeroInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.2 }}
          >
            <motion.span
              className="w-2 h-2 bg-[#cca695] rounded-full mr-3"
              animate={{ scale: [1, 1.2, 1] }}
              transition={{ duration: 2, repeat: Infinity }}
            />
            <span className="text-sm font-semibold text-[#cca695]">AI-Powered Financial Intelligence</span>
          </motion.div>

          <motion.h1
            className="text-6xl md:text-7xl lg:text-8xl font-black mb-8 leading-tight"
            initial={{ y: 100, opacity: 0 }}
            animate={isHeroInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.4, duration: 0.8 }}
          >
            <span className="block text-white">Your Future</span>
            <motion.span
              className="block bg-gradient-to-r from-[#cca695] via-[#d4b5a4] to-[#b8956a] bg-clip-text text-transparent"
              animate={{
                backgroundPosition: ["0% 50%", "100% 50%", "0% 50%"],
              }}
              transition={{
                duration: 3,
                repeat: Infinity,
                ease: "linear"
              }}
            >
              Wealth Engine
            </motion.span>
          </motion.h1>

          <motion.p
            className="text-xl md:text-2xl text-gray-300 max-w-4xl mx-auto leading-relaxed mb-12"
            initial={{ y: 50, opacity: 0 }}
            animate={isHeroInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.6 }}
          >
            Experience the next generation of financial intelligence with{' '}
            <motion.span
              className="text-[#cca695] font-semibold"
              whileHover={{ scale: 1.1 }}
            >
              AI-powered insights
            </motion.span>
            , real-time tracking, and personalized strategies.
          </motion.p>

          <motion.div
            className="flex flex-col sm:flex-row gap-6 justify-center items-center mb-16"
            initial={{ y: 50, opacity: 0 }}
            animate={isHeroInView ? { y: 0, opacity: 1 } : {}}
            transition={{ delay: 0.8 }}
          >
            <motion.button
              onClick={onDemoClick}
              className="group relative px-10 py-5 bg-gradient-to-r from-[#cca695] to-[#b8956a] text-white font-bold text-lg rounded-2xl overflow-hidden"
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.95 }}
              onHoverStart={() => setIsHovering(true)}
              onHoverEnd={() => setIsHovering(false)}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-r from-[#b8956a] to-[#a8855a]"
                initial={{ opacity: 0 }}
                whileHover={{ opacity: 1 }}
              />
              <span className="relative z-10 flex items-center">
                <span className="mr-3 text-2xl">Launch</span>
                Experience Demo
              </span>
            </motion.button>
            
            <motion.button
              onClick={onCreateProfileClick}
              className="group relative px-6 py-3 bg-transparent border-2 border-[#cca695] text-[#cca695] font-bold text-lg rounded-2xl relative overflow-hidden"
              whileHover={{ scale: 1.05, y: -5 }}
              whileTap={{ scale: 0.95 }}
              onHoverStart={() => setIsHovering(true)}
              onHoverEnd={() => setIsHovering(false)}
            >
              <motion.div
                className="absolute inset-0 bg-[#cca695]"
                initial={{ x: "-100%" }}
                whileHover={{ x: 0 }}
                transition={{ duration: 0.3 }}
              />
              <span className="relative z-10 flex items-center group-hover:text-white transition-colors">
                <span className="mr-3 text-xl">Profile</span>
                Create Profile
              </span>
            </motion.button>
          </motion.div>

          {/* Trust indicators with animations */}
          <motion.div
            className="flex flex-wrap justify-center items-center gap-8 text-sm text-gray-400"
            initial={{ opacity: 0 }}
            animate={isHeroInView ? { opacity: 1 } : {}}
            transition={{ delay: 1 }}
          >
            {[
              { color: "bg-[#cca695]", text: "Real-time Data" },
              { color: "bg-blue-400", text: "Bank-grade Security" },
              { color: "bg-purple-400", text: "AI-Powered Insights" }
            ].map((item, index) => (
              <motion.div
                key={index}
                className="flex items-center"
                whileHover={{ scale: 1.1 }}
              >
                <motion.span
                  className={`w-2 h-2 ${item.color} rounded-full mr-2`}
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: index * 0.2
                  }}
                />
                <span>{item.text}</span>
              </motion.div>
            ))}
          </motion.div>
        </div>
      </motion.section>

      {/* Interactive Features Section */}
      <motion.section
        ref={featuresRef}
        className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32"
        initial={{ opacity: 0 }}
        animate={isFeaturesInView ? { opacity: 1 } : {}}
      >
        <div className="text-center mb-20">
          <motion.h2
            className="text-4xl md:text-5xl font-black text-white mb-6"
            initial={{ y: 50, opacity: 0 }}
            animate={isFeaturesInView ? { y: 0, opacity: 1 } : {}}
          >
            Powerful Features for{' '}
            <span className="block bg-gradient-to-r from-[#cca695] to-[#b8956a] bg-clip-text text-transparent">
              Smart Investors
            </span>
          </motion.h2>
        </div>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-8">
          {features.map((feature, index) => (
            <motion.div
              key={index}
              className={`group relative bg-gradient-to-br from-[rgba(24,25,27,0.9)] to-[rgba(30,32,34,0.9)] border rounded-3xl p-8 backdrop-blur-xl cursor-pointer ${
                currentFeature === index 
                  ? 'border-[rgba(204,166,149,0.5)] shadow-2xl shadow-[rgba(204,166,149,0.1)]' 
                  : 'border-[rgba(204,166,149,0.2)]'
              }`}
              initial={{ y: 50, opacity: 0 }}
              animate={isFeaturesInView ? { y: 0, opacity: 1 } : {}}
              transition={{ delay: index * 0.2 }}
              whileHover={{ y: -10, scale: 1.02 }}
              onClick={() => setCurrentFeature(index)}
              onHoverStart={() => setIsHovering(true)}
              onHoverEnd={() => setIsHovering(false)}
            >
              <motion.div
                className="absolute inset-0 bg-gradient-to-br from-[rgba(204,166,149,0.05)] to-transparent rounded-3xl"
                initial={{ opacity: 0 }}
                animate={{ opacity: currentFeature === index ? 1 : 0 }}
                transition={{ duration: 0.3 }}
              />
              
              <div className="relative">
                <motion.div
                  className={`w-20 h-20 bg-gradient-to-br ${feature.color} rounded-2xl flex items-center justify-center mx-auto mb-6 shadow-lg`}
                  whileHover={{ scale: 1.1 }}
                  transition={{ duration: 0.8 }}
                >
                  <span className="text-white font-bold text-lg">{feature.title.split(' ')[0]}</span>
                </motion.div>
                
                <motion.h3
                  className="text-2xl font-bold text-white mb-4 group-hover:text-[#cca695] transition-colors duration-300"
                  animate={{
                    color: currentFeature === index ? '#cca695' : 'white'
                  }}
                >
                  {feature.title}
                </motion.h3>
                
                <p className="text-gray-300 leading-relaxed">
                  {feature.description}
                </p>
              </div>
            </motion.div>
          ))}
        </div>
      </motion.section>

      {/* Animated Stats Section */}
      <motion.section
        ref={statsRef}
        className="relative max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pb-32"
        initial={{ opacity: 0 }}
        animate={isStatsInView ? { opacity: 1 } : {}}
      >
        <motion.div
          className="bg-gradient-to-r from-[rgba(204,166,149,0.1)] to-[rgba(184,149,106,0.1)] border border-[rgba(204,166,149,0.2)] rounded-3xl p-12 backdrop-blur-xl"
          initial={{ y: 100, opacity: 0 }}
          animate={isStatsInView ? { y: 0, opacity: 1 } : {}}
          transition={{ duration: 0.8 }}
        >
          <div className="grid grid-cols-1 md:grid-cols-4 gap-8 text-center">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                className="group cursor-pointer"
                initial={{ scale: 0 }}
                animate={isStatsInView ? { scale: 1 } : {}}
                transition={{ delay: index * 0.1, type: "spring", stiffness: 200 }}
                whileHover={{ scale: 1.1, y: -5 }}
                onHoverStart={() => setIsHovering(true)}
                onHoverEnd={() => setIsHovering(false)}
              >
                <div className="text-2xl font-bold text-[#cca695] mb-2">{stat.label}</div>
                <motion.div
                  className="text-4xl font-black text-[#cca695] mb-2"
                  animate={{
                    scale: [1, 1.05, 1],
                  }}
                  transition={{
                    duration: 2,
                    repeat: Infinity,
                    delay: index * 0.5
                  }}
                >
                  {stat.value}
                </motion.div>
                <div className="text-gray-300 font-semibold">{stat.label}</div>
              </motion.div>
            ))}
          </div>
        </motion.div>
      </motion.section>
    </div>
  );
};

export default InteractiveLandingPage;