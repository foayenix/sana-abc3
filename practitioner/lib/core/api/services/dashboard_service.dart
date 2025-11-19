import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Practitioner dashboard API service
class DashboardService {
  final ApiClient _client;

  DashboardService(this._client);

  /// Get dashboard stats
  Future<DashboardStats> getStats() async {
    final response = await _client.get('/practitioners/me/dashboard');
    return DashboardStats.fromJson(response.data);
  }

  /// Get today's sessions
  Future<List<SessionDto>> getTodaySessions() async {
    final response = await _client.get('/practitioners/me/sessions/today');
    return (response.data as List)
        .map((json) => SessionDto.fromJson(json))
        .toList();
  }

  /// Get upcoming sessions
  Future<List<SessionDto>> getUpcomingSessions({int limit = 5}) async {
    final response = await _client.get(
      '/practitioners/me/sessions/upcoming',
      queryParameters: {'limit': limit},
    );
    return (response.data as List)
        .map((json) => SessionDto.fromJson(json))
        .toList();
  }

  /// Get revenue summary
  Future<RevenueSummary> getRevenueSummary({String period = 'month'}) async {
    final response = await _client.get(
      '/practitioners/me/revenue',
      queryParameters: {'period': period},
    );
    return RevenueSummary.fromJson(response.data);
  }

  /// Get recent activity
  Future<List<ActivityItem>> getRecentActivity({int limit = 10}) async {
    final response = await _client.get(
      '/practitioners/me/activity',
      queryParameters: {'limit': limit},
    );
    return (response.data as List)
        .map((json) => ActivityItem.fromJson(json))
        .toList();
  }
}

/// Dashboard stats DTO
class DashboardStats {
  final int todaySessions;
  final int weekSessions;
  final int monthSessions;
  final int totalClients;
  final int newClientsThisMonth;
  final double avgRating;
  final double outcomeScore;

  DashboardStats({
    required this.todaySessions,
    required this.weekSessions,
    required this.monthSessions,
    required this.totalClients,
    required this.newClientsThisMonth,
    required this.avgRating,
    required this.outcomeScore,
  });

  factory DashboardStats.fromJson(Map<String, dynamic> json) {
    return DashboardStats(
      todaySessions: json['today_sessions'] ?? 0,
      weekSessions: json['week_sessions'] ?? 0,
      monthSessions: json['month_sessions'] ?? 0,
      totalClients: json['total_clients'] ?? 0,
      newClientsThisMonth: json['new_clients_this_month'] ?? 0,
      avgRating: (json['avg_rating'] ?? 0).toDouble(),
      outcomeScore: (json['outcome_score'] ?? 0).toDouble(),
    );
  }
}

/// Session DTO
class SessionDto {
  final int id;
  final int clientId;
  final String clientName;
  final String? clientAvatar;
  final int serviceId;
  final String serviceName;
  final DateTime scheduledAt;
  final int durationMinutes;
  final double price;
  final String status;
  final String? notes;
  final String? meetingLink;

  SessionDto({
    required this.id,
    required this.clientId,
    required this.clientName,
    this.clientAvatar,
    required this.serviceId,
    required this.serviceName,
    required this.scheduledAt,
    required this.durationMinutes,
    required this.price,
    required this.status,
    this.notes,
    this.meetingLink,
  });

  factory SessionDto.fromJson(Map<String, dynamic> json) {
    return SessionDto(
      id: json['id'],
      clientId: json['client_id'],
      clientName: json['client']?['name'] ?? json['client_name'] ?? '',
      clientAvatar: json['client']?['avatar'],
      serviceId: json['service_id'],
      serviceName: json['service']?['name'] ?? json['service_name'] ?? '',
      scheduledAt: DateTime.parse(json['scheduled_at']),
      durationMinutes: json['duration_minutes'] ?? 60,
      price: (json['price'] ?? 0).toDouble(),
      status: json['status'] ?? 'scheduled',
      notes: json['notes'],
      meetingLink: json['meeting_link'],
    );
  }
}

/// Revenue summary DTO
class RevenueSummary {
  final double totalRevenue;
  final double pendingPayout;
  final double lastPayout;
  final List<RevenueDataPoint> chartData;

  RevenueSummary({
    required this.totalRevenue,
    required this.pendingPayout,
    required this.lastPayout,
    required this.chartData,
  });

  factory RevenueSummary.fromJson(Map<String, dynamic> json) {
    return RevenueSummary(
      totalRevenue: (json['total_revenue'] ?? 0).toDouble(),
      pendingPayout: (json['pending_payout'] ?? 0).toDouble(),
      lastPayout: (json['last_payout'] ?? 0).toDouble(),
      chartData: (json['chart_data'] as List? ?? [])
          .map((d) => RevenueDataPoint.fromJson(d))
          .toList(),
    );
  }
}

/// Revenue data point
class RevenueDataPoint {
  final DateTime date;
  final double amount;

  RevenueDataPoint({required this.date, required this.amount});

  factory RevenueDataPoint.fromJson(Map<String, dynamic> json) {
    return RevenueDataPoint(
      date: DateTime.parse(json['date']),
      amount: (json['amount'] ?? 0).toDouble(),
    );
  }
}

/// Activity item DTO
class ActivityItem {
  final String type;
  final String message;
  final DateTime timestamp;
  final Map<String, dynamic>? metadata;

  ActivityItem({
    required this.type,
    required this.message,
    required this.timestamp,
    this.metadata,
  });

  factory ActivityItem.fromJson(Map<String, dynamic> json) {
    return ActivityItem(
      type: json['type'],
      message: json['message'],
      timestamp: DateTime.parse(json['timestamp']),
      metadata: json['metadata'],
    );
  }
}

/// Provider for dashboard service
final dashboardServiceProvider = Provider<DashboardService>((ref) {
  final client = ref.watch(apiClientProvider);
  return DashboardService(client);
});
