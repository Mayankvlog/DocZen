import 'package:flutter_test/flutter_test.dart';
import 'package:doczen/features/auth/presentation/bloc/auth_bloc.dart';

void main() {
  group('AuthBloc Tests', () {
    late AuthBloc authBloc;

    setUp(() {
      authBloc = AuthBloc();
    });

    tearDown(() {
      authBloc.close();
    });

    test('initial state is AuthInitial', () {
      expect(authBloc.state, isA<AuthInitial>());
    });

    test('emits AuthLoading when LoginRequested is added', () {
      authBloc.emit(const AuthInitial());
      
      authBloc.add(const LoginRequested(
        email: 'test@example.com',
        password: 'password123',
      ));

      expectLater(authBloc.stream, emitsInOrder([
        isA<AuthLoading>(),
      ]));
    });

    test('emits AuthLoading when RegisterRequested is added', () {
      authBloc.emit(const AuthInitial());
      
      authBloc.add(const RegisterRequested(
        email: 'test@example.com',
        password: 'password123',
        fullName: 'Test User',
      ));

      expectLater(authBloc.stream, emitsInOrder([
        isA<AuthLoading>(),
      ]));
    });

    test('emits AuthLoading when LogoutRequested is added', () {
      authBloc.emit(const Authenticated(
        userId: '123',
        email: 'test@example.com',
        fullName: 'Test User',
      ));
      
      authBloc.add(const LogoutRequested());

      expectLater(authBloc.stream, emitsInOrder([
        isA<AuthLoading>(),
      ]));
    });
  });
}
