import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';
import '../../../features/auth/models/user.dart';

/// Authentication API service
class AuthService {
  final ApiClient _client;

  AuthService(this._client);

  /// Register a new user
  Future<User> register({
    required String email,
    required String password,
    required String fullName,
  }) async {
    final response = await _client.post(
      '/auth/register',
      data: {
        'email': email,
        'password': password,
        'full_name': fullName,
      },
    );
    return User.fromJson(response.data);
  }

  /// Login with email and password
  Future<AuthResponse> login({
    required String email,
    required String password,
  }) async {
    final response = await _client.post(
      '/auth/login',
      data: {
        'username': email,
        'password': password,
      },
    );
    return AuthResponse.fromJson(response.data);
  }

  /// Get current user profile
  Future<User> getCurrentUser() async {
    final response = await _client.get('/auth/me');
    return User.fromJson(response.data);
  }

  /// Refresh access token
  Future<AuthResponse> refreshToken(String refreshToken) async {
    final response = await _client.post(
      '/auth/refresh',
      data: {'refresh_token': refreshToken},
    );
    return AuthResponse.fromJson(response.data);
  }

  /// Logout
  Future<void> logout() async {
    await _client.post('/auth/logout');
  }

  /// Request password reset
  Future<void> requestPasswordReset(String email) async {
    await _client.post(
      '/auth/password-reset/request',
      data: {'email': email},
    );
  }

  /// Reset password with token
  Future<void> resetPassword({
    required String token,
    required String newPassword,
  }) async {
    await _client.post(
      '/auth/password-reset/confirm',
      data: {
        'token': token,
        'new_password': newPassword,
      },
    );
  }

  /// Change password
  Future<void> changePassword({
    required String currentPassword,
    required String newPassword,
  }) async {
    await _client.post(
      '/auth/change-password',
      data: {
        'current_password': currentPassword,
        'new_password': newPassword,
      },
    );
  }

  /// Verify email with token
  Future<void> verifyEmail(String token) async {
    await _client.post(
      '/auth/verify-email',
      data: {'token': token},
    );
  }

  /// Resend verification email
  Future<void> resendVerificationEmail() async {
    await _client.post('/auth/resend-verification');
  }

  /// Update user profile
  Future<User> updateProfile({
    String? fullName,
    String? phone,
    String? dateOfBirth,
    String? address,
    List<String>? healthGoals,
  }) async {
    final response = await _client.patch(
      '/auth/profile',
      data: {
        if (fullName != null) 'full_name': fullName,
        if (phone != null) 'phone': phone,
        if (dateOfBirth != null) 'date_of_birth': dateOfBirth,
        if (address != null) 'address': address,
        if (healthGoals != null) 'health_goals': healthGoals,
      },
    );
    return User.fromJson(response.data);
  }

  /// Delete account
  Future<void> deleteAccount() async {
    await _client.delete('/auth/account');
  }
}

/// Auth response model
class AuthResponse {
  final String accessToken;
  final String? refreshToken;
  final String tokenType;
  final int? expiresIn;

  AuthResponse({
    required this.accessToken,
    this.refreshToken,
    this.tokenType = 'bearer',
    this.expiresIn,
  });

  factory AuthResponse.fromJson(Map<String, dynamic> json) {
    return AuthResponse(
      accessToken: json['access_token'],
      refreshToken: json['refresh_token'],
      tokenType: json['token_type'] ?? 'bearer',
      expiresIn: json['expires_in'],
    );
  }
}

/// Provider for auth service
final authServiceProvider = Provider<AuthService>((ref) {
  final client = ref.watch(apiClientProvider);
  return AuthService(client);
});
