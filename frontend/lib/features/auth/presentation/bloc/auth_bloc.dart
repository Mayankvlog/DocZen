import 'package:flutter_bloc/flutter_bloc.dart';
import 'package:equatable/equatable.dart';

// Events
abstract class AuthEvent extends Equatable {
  const AuthEvent();
  
  @override
  List<Object> get props => [];
}

class AuthStarted extends AuthEvent {
  const AuthStarted();
}

class LoginRequested extends AuthEvent {
  final String email;
  final String password;

  const LoginRequested({
    required this.email,
    required this.password,
  });

  @override
  List<Object> get props => [email, password];
}

class RegisterRequested extends AuthEvent {
  final String email;
  final String password;
  final String fullName;

  const RegisterRequested({
    required this.email,
    required this.password,
    required this.fullName,
  });

  @override
  List<Object> get props => [email, password, fullName];
}

class LogoutRequested extends AuthEvent {
  const LogoutRequested();
}

class OnboardingCompleted extends AuthEvent {
  const OnboardingCompleted();
}

// States
abstract class AuthState extends Equatable {
  const AuthState();
  
  @override
  List<Object> get props => [];
}

class AuthInitial extends AuthState {
  const AuthInitial();
}

class AuthLoading extends AuthState {
  const AuthLoading();
}

class Authenticated extends AuthState {
  final String userId;
  final String email;
  final String fullName;

  const Authenticated({
    required this.userId,
    required this.email,
    required this.fullName,
  });

  @override
  List<Object> get props => [userId, email, fullName];
}

class Unauthenticated extends AuthState {
  const Unauthenticated();
}

class OnboardingRequired extends AuthState {
  final String userId;
  final String email;
  final String fullName;

  const OnboardingRequired({
    required this.userId,
    required this.email,
    required this.fullName,
  });

  @override
  List<Object> get props => [userId, email, fullName];
}

class AuthError extends AuthState {
  final String message;

  const AuthError(this.message);

  @override
  List<Object> get props => [message];
}

// BLoC
class AuthBloc extends Bloc<AuthEvent, AuthState> {
  AuthBloc() : super(AuthInitial()) {
    on<AuthStarted>(_onAuthStarted);
    on<LoginRequested>(_onLoginRequested);
    on<RegisterRequested>(_onRegisterRequested);
    on<LogoutRequested>(_onLogoutRequested);
    on<OnboardingCompleted>(_onOnboardingCompleted);
  }

  Future<void> _onAuthStarted(AuthStarted event, Emitter<AuthState> emit) async {
    // Check for stored tokens and validate them
    // For now, just emit unauthenticated state
    emit(const Unauthenticated());
  }

  Future<void> _onLoginRequested(LoginRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      
      // Mock successful login
      emit(const Authenticated(
        userId: 'user123',
        email: 'user@example.com',
        fullName: 'John Doe',
      ));
    } catch (e) {
      emit(AuthError('Login failed: ${e.toString()}'));
    }
  }

  Future<void> _onRegisterRequested(RegisterRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    
    try {
      // Simulate API call
      await Future.delayed(const Duration(seconds: 2));
      
      // Mock successful registration requiring onboarding
      emit(const OnboardingRequired(
        userId: 'user123',
        email: event.email,
        fullName: event.fullName,
      ));
    } catch (e) {
      emit(AuthError('Registration failed: ${e.toString()}'));
    }
  }

  Future<void> _onLogoutRequested(LogoutRequested event, Emitter<AuthState> emit) async {
    emit(AuthLoading());
    
    try {
      // Clear stored tokens
      await Future.delayed(const Duration(seconds: 1));
      
      emit(const Unauthenticated());
    } catch (e) {
      emit(AuthError('Logout failed: ${e.toString()}'));
    }
  }

  Future<void> _onOnboardingCompleted(OnboardingCompleted event, Emitter<AuthState> emit) async {
    // After onboarding, user is authenticated
    emit(const Authenticated(
      userId: 'user123',
      email: 'user@example.com',
      fullName: 'John Doe',
    ));
  }
}
