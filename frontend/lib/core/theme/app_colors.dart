import 'package:flutter/material.dart';

class AppColors {
  static const Color emerald = Color(0xFF10B981);
  static const Color cyan = Color(0xFF06B6D4);
  static const Color deepBlue = Color(0xFF1E40AF);
  
  static const LinearGradient primaryGradient = LinearGradient(
    colors: [emerald, cyan, deepBlue],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const LinearGradient cardGradient = LinearGradient(
    colors: [
      Color(0x33FFFFFF),
      Color(0x1AFFFFFF),
    ],
    begin: Alignment.topLeft,
    end: Alignment.bottomRight,
  );
  
  static const Color surface = Color(0xFFF8FAFC);
  static const Color surfaceDark = Color(0xFF0F172A);
  static const Color onSurface = Color(0xFF1E293B);
  static const Color onSurfaceDark = Color(0xFFF8FAFC);
  
  static const Color primary = emerald;
  static const Color secondary = cyan;
  static const Color tertiary = deepBlue;
  
  static const Color success = Color(0xFF22C55E);
  static const Color warning = Color(0xFFF59E0B);
  static const Color error = Color(0xFFEF4444);
  static const Color info = Color(0xFF3B82F6);
  
  static const Color glassWhite = Color(0x33FFFFFF);
  static const Color glassDark = Color(0x19000000);
  static const Color glassBorder = Color(0x1AFFFFFF);
}
