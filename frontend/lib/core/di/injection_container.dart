import 'package:flutter/material.dart';
import 'package:get_it/get_it.dart';
import 'package:injectable/injectable.dart';
import '../features/auth/presentation/bloc/auth_bloc.dart';
import 'injection_container.config.dart';

final getIt = GetIt.instance;

@injectable
class NavigationService {
  final GlobalKey<NavigatorState> navigatorKey = GlobalKey<NavigatorState>();

  BuildContext? get context => navigatorKey.currentContext;

  Future<dynamic> navigateTo(String routeName, {Object? arguments}) {
    return navigatorKey.currentState!.pushNamed(routeName, arguments: arguments);
  }

  void goBack() {
    return navigatorKey.currentState!.pop();
  }

  Future<dynamic> navigateAndClearStack(String routeName, {Object? arguments}) {
    return navigatorKey.currentState!.pushNamedAndRemoveUntil(
      routeName,
      (Route<dynamic> route) => false,
      arguments: arguments,
    );
  }
}

Future<void> initializeDependencies() async {
  await configureInjection();
  
  // Register services manually for now
  getIt.registerLazySingleton<NavigationService>(() => NavigationService());
  getIt.registerFactory<AuthBloc>(() => AuthBloc());
}
