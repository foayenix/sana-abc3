import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Admin API service for dashboard and platform management
class AdminService {
  final ApiClient _client;

  AdminService(this._client);

  // Dashboard
  Future<AdminDashboardStats> getDashboardStats() async {
    final response = await _client.get('/admin/dashboard');
    return AdminDashboardStats.fromJson(response.data);
  }

  // Users
  Future<PaginatedResponse<UserDto>> getUsers({
    String? role,
    bool? isActive,
    String? search,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get('/admin/users', queryParameters: {
      if (role != null) 'role': role,
      if (isActive != null) 'is_active': isActive,
      if (search != null) 'search': search,
      'page': page,
      'limit': limit,
    });
    return PaginatedResponse.fromJson(
      response.data,
      (json) => UserDto.fromJson(json),
    );
  }

  Future<UserDto> getUser(int id) async {
    final response = await _client.get('/admin/users/$id');
    return UserDto.fromJson(response.data);
  }

  Future<UserDto> updateUser(int id, Map<String, dynamic> data) async {
    final response = await _client.patch('/admin/users/$id', data: data);
    return UserDto.fromJson(response.data);
  }

  Future<void> deleteUser(int id) async {
    await _client.delete('/admin/users/$id');
  }

  // Practitioners
  Future<PaginatedResponse<PractitionerDto>> getPractitioners({
    String? verificationStatus,
    String? search,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get('/admin/practitioners', queryParameters: {
      if (verificationStatus != null) 'verification_status': verificationStatus,
      if (search != null) 'search': search,
      'page': page,
      'limit': limit,
    });
    return PaginatedResponse.fromJson(
      response.data,
      (json) => PractitionerDto.fromJson(json),
    );
  }

  Future<List<PractitionerDto>> getPendingVerifications() async {
    final response = await _client.get('/admin/practitioners/pending-verification');
    return (response.data as List).map((j) => PractitionerDto.fromJson(j)).toList();
  }

  Future<void> verifyPractitioner(int id, {required String status, String? reason}) async {
    await _client.post('/admin/practitioners/$id/verify', data: {
      'status': status,
      if (reason != null) 'reason': reason,
    });
  }

  // Analytics
  Future<RevenueAnalytics> getRevenueAnalytics({String period = 'month'}) async {
    final response = await _client.get('/admin/analytics/revenue', queryParameters: {'period': period});
    return RevenueAnalytics.fromJson(response.data);
  }

  Future<UserAnalytics> getUserAnalytics() async {
    final response = await _client.get('/admin/analytics/users');
    return UserAnalytics.fromJson(response.data);
  }

  Future<SessionAnalytics> getSessionAnalytics() async {
    final response = await _client.get('/admin/analytics/sessions');
    return SessionAnalytics.fromJson(response.data);
  }

  // Settings
  Future<PlatformSettings> getSettings() async {
    final response = await _client.get('/admin/settings');
    return PlatformSettings.fromJson(response.data);
  }

  Future<void> updateSettings(Map<String, dynamic> settings) async {
    await _client.patch('/admin/settings', data: settings);
  }
}

// DTOs
class AdminDashboardStats {
  final int totalUsers, totalPractitioners, totalSessions;
  final double totalRevenue, monthlyRevenue;
  final int pendingVerifications;

  AdminDashboardStats({
    required this.totalUsers, required this.totalPractitioners,
    required this.totalSessions, required this.totalRevenue,
    required this.monthlyRevenue, required this.pendingVerifications,
  });

  factory AdminDashboardStats.fromJson(Map<String, dynamic> json) => AdminDashboardStats(
    totalUsers: json['total_users'] ?? 0,
    totalPractitioners: json['total_practitioners'] ?? 0,
    totalSessions: json['total_sessions'] ?? 0,
    totalRevenue: (json['total_revenue'] ?? 0).toDouble(),
    monthlyRevenue: (json['monthly_revenue'] ?? 0).toDouble(),
    pendingVerifications: json['pending_verifications'] ?? 0,
  );
}

class UserDto {
  final int id;
  final String email, fullName, role;
  final bool isActive, isVerified;
  final DateTime createdAt;

  UserDto({required this.id, required this.email, required this.fullName,
    required this.role, required this.isActive, required this.isVerified, required this.createdAt});

  factory UserDto.fromJson(Map<String, dynamic> json) => UserDto(
    id: json['id'], email: json['email'], fullName: json['full_name'],
    role: json['role'], isActive: json['is_active'] ?? true,
    isVerified: json['is_verified'] ?? false,
    createdAt: DateTime.parse(json['created_at']),
  );
}

class PractitionerDto {
  final int id;
  final String name, email, verificationStatus;
  final double rating;
  final int totalSessions;

  PractitionerDto({required this.id, required this.name, required this.email,
    required this.verificationStatus, required this.rating, required this.totalSessions});

  factory PractitionerDto.fromJson(Map<String, dynamic> json) => PractitionerDto(
    id: json['id'], name: json['user']?['full_name'] ?? json['name'] ?? '',
    email: json['user']?['email'] ?? json['email'] ?? '',
    verificationStatus: json['verification_status'] ?? 'pending',
    rating: (json['rating'] ?? 0).toDouble(),
    totalSessions: json['total_sessions'] ?? 0,
  );
}

class PaginatedResponse<T> {
  final List<T> items;
  final int total, page, limit;

  PaginatedResponse({required this.items, required this.total, required this.page, required this.limit});

  factory PaginatedResponse.fromJson(Map<String, dynamic> json, T Function(Map<String, dynamic>) fromJson) =>
    PaginatedResponse(
      items: (json['items'] as List).map((e) => fromJson(e)).toList(),
      total: json['total'] ?? 0, page: json['page'] ?? 1, limit: json['limit'] ?? 20,
    );
}

class RevenueAnalytics {
  final double total, growth;
  final List<DataPoint> chartData;

  RevenueAnalytics({required this.total, required this.growth, required this.chartData});

  factory RevenueAnalytics.fromJson(Map<String, dynamic> json) => RevenueAnalytics(
    total: (json['total'] ?? 0).toDouble(),
    growth: (json['growth'] ?? 0).toDouble(),
    chartData: (json['chart_data'] as List? ?? []).map((d) => DataPoint.fromJson(d)).toList(),
  );
}

class UserAnalytics {
  final int total, newThisMonth, activeThisMonth;

  UserAnalytics({required this.total, required this.newThisMonth, required this.activeThisMonth});

  factory UserAnalytics.fromJson(Map<String, dynamic> json) => UserAnalytics(
    total: json['total'] ?? 0,
    newThisMonth: json['new_this_month'] ?? 0,
    activeThisMonth: json['active_this_month'] ?? 0,
  );
}

class SessionAnalytics {
  final int total, completed, cancelled;
  final double completionRate;

  SessionAnalytics({required this.total, required this.completed, required this.cancelled, required this.completionRate});

  factory SessionAnalytics.fromJson(Map<String, dynamic> json) => SessionAnalytics(
    total: json['total'] ?? 0, completed: json['completed'] ?? 0,
    cancelled: json['cancelled'] ?? 0,
    completionRate: (json['completion_rate'] ?? 0).toDouble(),
  );
}

class DataPoint {
  final DateTime date;
  final double value;

  DataPoint({required this.date, required this.value});

  factory DataPoint.fromJson(Map<String, dynamic> json) => DataPoint(
    date: DateTime.parse(json['date']),
    value: (json['value'] ?? 0).toDouble(),
  );
}

class PlatformSettings {
  final double platformFeePercent;
  final bool requireEmailVerification, maintenanceMode;

  PlatformSettings({required this.platformFeePercent, required this.requireEmailVerification, required this.maintenanceMode});

  factory PlatformSettings.fromJson(Map<String, dynamic> json) => PlatformSettings(
    platformFeePercent: (json['platform_fee_percent'] ?? 10).toDouble(),
    requireEmailVerification: json['require_email_verification'] ?? true,
    maintenanceMode: json['maintenance_mode'] ?? false,
  );
}

final adminServiceProvider = Provider<AdminService>((ref) {
  final client = ref.watch(apiClientProvider);
  return AdminService(client);
});
