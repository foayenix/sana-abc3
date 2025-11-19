import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:sana_client/core/providers/auth_provider.dart';
import 'package:sana_client/core/api/services/auth_service.dart';
import 'package:sana_client/core/storage/secure_storage.dart';
import 'package:sana_client/features/auth/models/user.dart';

@GenerateMocks([AuthService, SecureStorage])
import 'auth_provider_test.mocks.dart';

void main() {
  late MockAuthService mockAuthService;
  late MockSecureStorage mockStorage;
  late ProviderContainer container;

  setUp(() {
    mockAuthService = MockAuthService();
    mockStorage = MockSecureStorage();
  });

  tearDown(() {
    container.dispose();
  });

  group('AuthNotifier', () {
    test('initial state is correct', () {
      when(mockStorage.isLoggedIn()).thenAnswer((_) async => false);

      final notifier = AuthNotifier(mockAuthService, mockStorage);

      expect(notifier.state.status, AuthStatus.initial);
      expect(notifier.state.user, isNull);
      expect(notifier.state.error, isNull);
    });

    test('login success updates state correctly', () async {
      final user = User(
        id: 1,
        email: 'test@example.com',
        fullName: 'Test User',
        createdAt: DateTime.now(),
      );

      when(mockStorage.isLoggedIn()).thenAnswer((_) async => false);
      when(mockAuthService.login(
        email: 'test@example.com',
        password: 'password123',
      )).thenAnswer((_) async => AuthResponse(
            accessToken: 'token123',
            refreshToken: 'refresh123',
          ));
      when(mockAuthService.getCurrentUser()).thenAnswer((_) async => user);
      when(mockStorage.saveToken(any)).thenAnswer((_) async {});
      when(mockStorage.saveRefreshToken(any)).thenAnswer((_) async {});
      when(mockStorage.saveUserId(any)).thenAnswer((_) async {});

      final notifier = AuthNotifier(mockAuthService, mockStorage);
      await notifier.login('test@example.com', 'password123');

      expect(notifier.state.status, AuthStatus.authenticated);
      expect(notifier.state.user, user);
      expect(notifier.state.isAuthenticated, isTrue);
    });

    test('login failure updates state with error', () async {
      when(mockStorage.isLoggedIn()).thenAnswer((_) async => false);
      when(mockAuthService.login(
        email: 'test@example.com',
        password: 'wrong',
      )).thenThrow(Exception('Invalid credentials'));

      final notifier = AuthNotifier(mockAuthService, mockStorage);

      expect(
        () => notifier.login('test@example.com', 'wrong'),
        throwsException,
      );
    });

    test('logout clears state and storage', () async {
      when(mockStorage.isLoggedIn()).thenAnswer((_) async => false);
      when(mockAuthService.logout()).thenAnswer((_) async {});
      when(mockStorage.clearAll()).thenAnswer((_) async {});

      final notifier = AuthNotifier(mockAuthService, mockStorage);
      await notifier.logout();

      expect(notifier.state.status, AuthStatus.unauthenticated);
      expect(notifier.state.user, isNull);
      verify(mockStorage.clearAll()).called(1);
    });

    test('register calls login after success', () async {
      final user = User(
        id: 1,
        email: 'new@example.com',
        fullName: 'New User',
        createdAt: DateTime.now(),
      );

      when(mockStorage.isLoggedIn()).thenAnswer((_) async => false);
      when(mockAuthService.register(
        email: 'new@example.com',
        password: 'password123',
        fullName: 'New User',
      )).thenAnswer((_) async {});
      when(mockAuthService.login(
        email: 'new@example.com',
        password: 'password123',
      )).thenAnswer((_) async => AuthResponse(
            accessToken: 'token123',
            refreshToken: 'refresh123',
          ));
      when(mockAuthService.getCurrentUser()).thenAnswer((_) async => user);
      when(mockStorage.saveToken(any)).thenAnswer((_) async {});
      when(mockStorage.saveRefreshToken(any)).thenAnswer((_) async {});
      when(mockStorage.saveUserId(any)).thenAnswer((_) async {});

      final notifier = AuthNotifier(mockAuthService, mockStorage);
      await notifier.register('new@example.com', 'password123', 'New User');

      expect(notifier.state.status, AuthStatus.authenticated);
      verify(mockAuthService.register(
        email: 'new@example.com',
        password: 'password123',
        fullName: 'New User',
      )).called(1);
    });
  });

  group('AuthState', () {
    test('isAuthenticated returns true when authenticated', () {
      final state = AuthState(status: AuthStatus.authenticated);
      expect(state.isAuthenticated, isTrue);
    });

    test('isAuthenticated returns false when not authenticated', () {
      final state = AuthState(status: AuthStatus.unauthenticated);
      expect(state.isAuthenticated, isFalse);
    });

    test('isLoading returns true when loading', () {
      final state = AuthState(status: AuthStatus.loading);
      expect(state.isLoading, isTrue);
    });

    test('copyWith creates new instance with updated values', () {
      final state = AuthState(status: AuthStatus.initial);
      final newState = state.copyWith(status: AuthStatus.loading);

      expect(state.status, AuthStatus.initial);
      expect(newState.status, AuthStatus.loading);
    });
  });
}

// Mock classes for AuthResponse
class AuthResponse {
  final String accessToken;
  final String? refreshToken;

  AuthResponse({required this.accessToken, this.refreshToken});
}
