class AppConfig {
  // API Configuration
  static const String baseUrl = 'http://localhost:8000';
  static const String apiVersion = '/api/v1';
  
  // App Information
  static const String appName = 'DocZen';
  static const String appVersion = '1.0.0';
  
  // Firebase Configuration (placeholder)
  static const String firebaseProjectId = 'doczen-app';
  
  // Storage Configuration
  static const int maxFileSize = 100 * 1024 * 1024; // 100MB
  static const List<String> allowedFileTypes = [
    'pdf', 'doc', 'docx', 'txt', 'jpg', 'jpeg', 'png', 'gif', 'bmp', 'tiff'
  ];
  
  // UI Configuration
  static const double defaultPadding = 16.0;
  static const double defaultBorderRadius = 12.0;
  static const Duration defaultAnimationDuration = Duration(milliseconds: 300);
  
  // Cache Configuration
  static const Duration cacheExpiration = Duration(hours: 24);
  static const int maxCacheSize = 100 * 1024 * 1024; // 100MB
}
