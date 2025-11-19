import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/auth_service.dart';
import '../storage/secure_storage.dart';
import '../../features/auth/models/user.dart';

/// Auth state
enum AuthStatus {
  initial,
  loading,
  authenticated,
  unauthenticated,
  error,
}

/// Auth state class
class AuthState {
  final AuthStatus status;
  final User? user;
  final String? error;

  const AuthState({
    this.status = AuthStatus.initial,
    this.user,
    this.error,
  });

  AuthState copyWith({
    AuthStatus? status,
    User? user,
    String? error,
  }) {
    return AuthState(
      status: status ?? this.status,
      user: user ?? this.user,
      error: error,
    );
  }

  bool get isAuthenticated => status == AuthStatus.authenticated;
  bool get isLoading => status == AuthStatus.loading;
}

/// Auth notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthService _authService;
  final SecureStorage _storage;

  AuthNotifier(this._authService, this._storage) : super(const AuthState()) {
    _checkAuthStatus();
  }

  /// Check if user is already logged in
  Future<void> _checkAuthStatus() async {
    try {
      final isLoggedIn = await _storage.isLoggedIn();
      if (isLoggedIn) {
        state = state.copyWith(status: AuthStatus.loading);
        final user = await _authService.getCurrentUser();
        state = AuthState(
          status: AuthStatus.authenticated,
          user: user,
        );
      } else {
        state = state.copyWith(status: AuthStatus.unauthenticated);
      }
    } catch (e) {
      state = state.copyWith(status: AuthStatus.unauthenticated);
    }
  }

  /// Login
  Future<void> login(String email, String password) async {
    try {
      state = state.copyWith(status: AuthStatus.loading, error: null);

      final response = await _authService.login(
        email: email,
        password: password,
      );

      await _storage.saveToken(response.accessToken);
      if (response.refreshToken != null) {
        await _storage.saveRefreshToken(response.refreshToken!);
      }

      final user = await _authService.getCurrentUser();
      await _storage.saveUserId(user.id.toString());

      state = AuthState(
        status: AuthStatus.authenticated,
        user: user,
      );
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Register
  Future<void> register(String email, String password, String fullName) async {
    try {
      state = state.copyWith(status: AuthStatus.loading, error: null);

      await _authService.register(
        email: email,
        password: password,
        fullName: fullName,
      );

      // Auto-login after registration
      await login(email, password);
    } catch (e) {
      state = state.copyWith(
        status: AuthStatus.error,
        error: e.toString(),
      );
      rethrow;
    }
  }

  /// Logout
  Future<void> logout() async {
    try {
      await _authService.logout();
    } catch (_) {
      // Ignore logout errors
    } finally {
      await _storage.clearAll();
      state = const AuthState(status: AuthStatus.unauthenticated);
    }
  }

  /// Update user profile
  Future<void> updateProfile({
    String? fullName,
    String? phone,
    String? dateOfBirth,
    String? address,
    List<String>? healthGoals,
  }) async {
    try {
      final updatedUser = await _authService.updateProfile(
        fullName: fullName,
        phone: phone,
        dateOfBirth: dateOfBirth,
        address: address,
        healthGoals: healthGoals,
      );
      state = state.copyWith(user: updatedUser);
    } catch (e) {
      rethrow;
    }
  }

  /// Change password
  Future<void> changePassword(String currentPassword, String newPassword) async {
    await _authService.changePassword(
      currentPassword: currentPassword,
      newPassword: newPassword,
    );
  }

  /// Request password reset
  Future<void> requestPasswordReset(String email) async {
    await _authService.requestPasswordReset(email);
  }

  /// Refresh user data
  Future<void> refreshUser() async {
    try {
      final user = await _authService.getCurrentUser();
      state = state.copyWith(user: user);
    } catch (_) {
      // If refresh fails, logout
      await logout();
    }
  }
}

/// Auth provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authService = ref.watch(authServiceProvider);
  final storage = ref.watch(secureStorageProvider);
  return AuthNotifier(authService, storage);
});

/// Current user provider
final currentUserProvider = Provider<User?>((ref) {
  return ref.watch(authProvider).user;
});

/// Is authenticated provider
final isAuthenticatedProvider = Provider<bool>((ref) {
  return ref.watch(authProvider).isAuthenticated;
});
