import 'package:flutter/material.dart';
import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:firebase_analytics/firebase_analytics.dart';
import 'package:glassmorphism/glassmorphism.dart';
import '../core/theme/app_theme.dart';
import '../core/theme/app_colors.dart';
import '../features/auth/presentation/bloc/auth_bloc.dart';
import '../features/dashboard/presentation/screens/dashboard_screen.dart';
import '../screens/splash_screen.dart';
import '../features/onboarding/presentation/screens/onboarding_screen.dart';
import '../core/services/navigation_service.dart';
import '../core/di/injection_container.dart';

class DocZenApp extends StatelessWidget {
  static FirebaseAnalytics analytics = FirebaseAnalytics.instance;
  static FirebaseAnalyticsObserver observer = 
      FirebaseAnalyticsObserver(analytics: analytics);

  const DocZenApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'DocZen',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.lightTheme,
      darkTheme: AppTheme.darkTheme,
      themeMode: ThemeMode.system,
      navigatorObservers: [observer],
      navigatorKey: getIt<NavigationService>().navigatorKey,
      home: BlocProvider(
        create: (context) => getIt<AuthBloc>()..add(AuthStarted()),
        child: const AppNavigator(),
      ),
      builder: (context, child) {
        return MediaQuery(
          data: MediaQuery.of(context).copyWith(
            textScaleFactor: 1.0,
          ),
          child: child!,
        );
      },
    );
  }
}

class AppNavigator extends StatelessWidget {
  const AppNavigator({super.key});

  @override
  Widget build(BuildContext context) {
    return BlocBuilder<AuthBloc, AuthState>(
      builder: (context, state) {
        if (state is AuthInitial) {
          return const SplashScreen();
        } else if (state is AuthLoading) {
          return const SplashScreen();
        } else if (state is OnboardingRequired) {
          return const OnboardingScreen();
        } else if (state is Authenticated) {
          return const DashboardScreen();
        } else if (state is Unauthenticated) {
          return const LoginScreen();
        }
        return const SplashScreen();
      },
    );
  }
}
