import 'package:flutter/material.dart';

class AppColors {
  // Primary Colors - Modern Professional Gradient
  static const Color primaryBlue = Color(0xFF2563EB); // Blue-600 (more professional)
  static const Color primaryDark = Color(0xFF1D4ED8); // Blue-700
  static const Color primaryLight = Color(0xFF3B82F6); // Blue-500
  static const Color primaryAccent = Color(0xFF7C3AED); // Violet-600 (more sophisticated)
  static const Color primarySurface = Color(0xFFEFF6FF); // Blue-50
  static const Color primaryContainer = Color(0xFFDBEAFE); // Blue-100
  
  // Agent Colors - Modern Vibrant Palette
  static const Color pastAgentColor = Color(0xFFEF4444); // Red-500 (Past/Historical)
  static const Color presentAgentColor = Color(0xFF10B981); // Emerald-500 (Present/Current)
  static const Color futureAgentColor = Color(0xFF8B5CF6); // Violet-500 (Future/Predictions)
  
  // Neutral Colors - Modern Gray Scale
  static const Color white = Color(0xFFFFFFFF);
  static const Color black = Color(0xFF000000);
  static const Color grey900 = Color(0xFF111827); // Gray-900
  static const Color grey800 = Color(0xFF1F2937); // Gray-800
  static const Color grey700 = Color(0xFF374151); // Gray-700
  static const Color grey600 = Color(0xFF4B5563); // Gray-600
  static const Color grey500 = Color(0xFF6B7280); // Gray-500
  static const Color grey400 = Color(0xFF9CA3AF); // Gray-400
  static const Color grey300 = Color(0xFFD1D5DB); // Gray-300
  static const Color grey200 = Color(0xFFE5E7EB); // Gray-200
  static const Color grey100 = Color(0xFFF3F4F6); // Gray-100
  static const Color grey50 = Color(0xFFF9FAFB); // Gray-50
  
  // Background Colors - Modern Glass-morphism Surfaces
  static const Color surface = Color(0xFFFFFFFF);
  static const Color surfaceVariant = Color(0xFFF8FAFC); // Slate-50
  static const Color surfaceContainer = Color(0xFFF1F5F9); // Slate-100
  static const Color surfaceElevated = Color(0xFFFAFAFA); // Elevated surface
  static const Color surfaceGlass = Color(0xFFFBFBFB); // Glass effect
  static const Color background = Color(0xFFFFFFFF);
  static const Color backgroundSecondary = Color(0xFFF8FAFC);
  static const Color backgroundTertiary = Color(0xFFF1F5F9); // Additional layer
  
  // Status Colors - Modern Semantic Colors
  static const Color success = Color(0xFF10B981); // Emerald-500
  static const Color successLight = Color(0xFF6EE7B7); // Emerald-300
  static const Color warning = Color(0xFFF59E0B); // Amber-500
  static const Color warningLight = Color(0xFFFCD34D); // Amber-300
  static const Color error = Color(0xFFEF4444); // Red-500
  static const Color errorLight = Color(0xFFFCA5A5); // Red-300
  static const Color info = Color(0xFF3B82F6); // Blue-500
  static const Color infoLight = Color(0xFF93C5FD); // Blue-300
  
  // Financial Colors - Professional Finance UI
  static const Color profit = Color(0xFF10B981); // Emerald-500
  static const Color profitLight = Color(0xFF34D399); // Emerald-400
  static const Color loss = Color(0xFFEF4444); // Red-500
  static const Color lossLight = Color(0xFFF87171); // Red-400
  static const Color neutral = Color(0xFF6B7280); // Gray-500
  
  // Card & Component Colors
  static const Color cardBackground = Color(0xFFFFFFFF);
  static const Color cardBorder = Color(0xFFE2E8F0); // Slate-200
  static const Color divider = Color(0xFFE2E8F0); // Slate-200
  
  // Interactive Colors
  static const Color buttonPrimary = Color(0xFF6366F1); // Indigo-500
  static const Color buttonSecondary = Color(0xFFF1F5F9); // Slate-100
  static const Color buttonDanger = Color(0xFFEF4444); // Red-500
  static const Color buttonSuccess = Color(0xFF10B981); // Emerald-500
  
  // Shadow Colors - Enhanced depth system
  static const Color shadowLight = Color(0x0A000000); // 4% opacity
  static const Color shadowMedium = Color(0x14000000); // 8% opacity
  static const Color shadowDark = Color(0x29000000); // 16% opacity
  static const Color shadowElevated = Color(0x1A000000); // 10% opacity
  static const Color shadowGlass = Color(0x08000000); // 3% opacity for glass effect
  
  // Gradient Colors - Modern sophisticated gradients
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [Color(0xFF2563EB), Color(0xFF7C3AED)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient surfaceGradient = LinearGradient(
    colors: [Color(0xFFFFFFFF), Color(0xFFF8FAFC)],
    begin: Alignment.topCenter,
    end: Alignment.bottomCenter,
  );
  
  static const LinearGradient glassGradient = LinearGradient(
    colors: [Color(0xFFFBFBFB), Color(0xFFF8FAFC)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient heroGradient = LinearGradient(
    colors: [Color(0xFF1E40AF), Color(0xFF3B82F6), Color(0xFF6366F1)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient profitGradient = LinearGradient(
    colors: [Color(0xFF10B981), Color(0xFF34D399)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient lossGradient = LinearGradient(
    colors: [Color(0xFFEF4444), Color(0xFFF87171)],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  // Modern gradient arrays and additional effects
  static const List<Color> agentGradient = [
    Color(0xFFEF4444), // Past
    Color(0xFF10B981), // Present
    Color(0xFF7C3AED), // Future
  ];
  
  // Glassmorphism effect colors
  static const Color glassWhite = Color(0xFFFFFFFF);
  static const Color glassBlur = Color(0x40FFFFFF);
  static const Color glassBorder = Color(0x20FFFFFF);
  
  // Modern accent colors for variety
  static const Color accentTeal = Color(0xFF14B8A6); // Teal-500
  static const Color accentOrange = Color(0xFFF97316); // Orange-500
  static const Color accentPink = Color(0xFFEC4899); // Pink-500
  static const Color accentPurple = Color(0xFF8B5CF6); // Purple-500
  
  // Enhanced interactive states
  static const Color hoverOverlay = Color(0x08000000); // 3% black
  static const Color pressedOverlay = Color(0x12000000); // 7% black
  static const Color focusOverlay = Color(0x14000000); // 8% black
}