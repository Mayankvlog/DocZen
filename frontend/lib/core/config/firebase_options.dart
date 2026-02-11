import 'package:firebase_core/firebase_core.dart' show FirebaseOptions;

// Default Firebase configuration for development
// In production, this should be replaced with actual Firebase configuration
class DefaultFirebaseOptions {
  static FirebaseOptions get currentPlatform {
    // Return a placeholder configuration
    return const FirebaseOptions(
      apiKey: 'your-api-key',
      appId: 'your-app-id',
      messagingSenderId: 'your-sender-id',
      projectId: 'doczen-app',
      authDomain: 'doczen-app.firebaseapp.com',
      storageBucket: 'doczen-app.appspot.com',
    );
  }
}
