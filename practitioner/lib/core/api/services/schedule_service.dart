import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Calendar/Schedule API service
class ScheduleService {
  final ApiClient _client;

  ScheduleService(this._client);

  /// Get sessions for date range
  Future<List<ScheduledSession>> getSessions({
    required DateTime startDate,
    required DateTime endDate,
  }) async {
    final response = await _client.get(
      '/practitioners/me/schedule',
      queryParameters: {
        'start_date': startDate.toIso8601String(),
        'end_date': endDate.toIso8601String(),
      },
    );
    return (response.data as List)
        .map((json) => ScheduledSession.fromJson(json))
        .toList();
  }

  /// Get availability settings
  Future<List<AvailabilitySlot>> getAvailability() async {
    final response = await _client.get('/practitioners/me/availability');
    return (response.data as List)
        .map((json) => AvailabilitySlot.fromJson(json))
        .toList();
  }

  /// Set availability for a day
  Future<void> setAvailability({
    required int dayOfWeek,
    required String startTime,
    required String endTime,
    bool isAvailable = true,
  }) async {
    await _client.post(
      '/practitioners/me/availability',
      data: {
        'day_of_week': dayOfWeek,
        'start_time': startTime,
        'end_time': endTime,
        'is_available': isAvailable,
      },
    );
  }

  /// Block time off
  Future<void> blockTimeOff({
    required DateTime startTime,
    required DateTime endTime,
    String? reason,
  }) async {
    await _client.post(
      '/practitioners/me/time-off',
      data: {
        'start_time': startTime.toIso8601String(),
        'end_time': endTime.toIso8601String(),
        if (reason != null) 'reason': reason,
      },
    );
  }

  /// Get blocked time off
  Future<List<TimeOffBlock>> getTimeOff() async {
    final response = await _client.get('/practitioners/me/time-off');
    return (response.data as List)
        .map((json) => TimeOffBlock.fromJson(json))
        .toList();
  }

  /// Delete time off block
  Future<void> deleteTimeOff(int id) async {
    await _client.delete('/practitioners/me/time-off/$id');
  }

  /// Complete a session
  Future<void> completeSession(int sessionId, {String? notes}) async {
    await _client.post(
      '/practitioners/me/sessions/$sessionId/complete',
      data: {if (notes != null) 'notes': notes},
    );
  }

  /// Cancel a session
  Future<void> cancelSession(int sessionId, {String? reason}) async {
    await _client.post(
      '/practitioners/me/sessions/$sessionId/cancel',
      data: {if (reason != null) 'reason': reason},
    );
  }

  /// Start session (generate meeting link)
  Future<String> startSession(int sessionId) async {
    final response = await _client.post(
      '/practitioners/me/sessions/$sessionId/start',
    );
    return response.data['meeting_link'];
  }
}

/// Scheduled session DTO
class ScheduledSession {
  final int id;
  final int clientId;
  final String clientName;
  final String? clientAvatar;
  final String serviceName;
  final DateTime scheduledAt;
  final int durationMinutes;
  final String status;
  final String? notes;

  ScheduledSession({
    required this.id,
    required this.clientId,
    required this.clientName,
    this.clientAvatar,
    required this.serviceName,
    required this.scheduledAt,
    required this.durationMinutes,
    required this.status,
    this.notes,
  });

  factory ScheduledSession.fromJson(Map<String, dynamic> json) {
    return ScheduledSession(
      id: json['id'],
      clientId: json['client_id'],
      clientName: json['client_name'] ?? '',
      clientAvatar: json['client_avatar'],
      serviceName: json['service_name'] ?? '',
      scheduledAt: DateTime.parse(json['scheduled_at']),
      durationMinutes: json['duration_minutes'] ?? 60,
      status: json['status'],
      notes: json['notes'],
    );
  }

  DateTime get endTime => scheduledAt.add(Duration(minutes: durationMinutes));
}

/// Availability slot DTO
class AvailabilitySlot {
  final int id;
  final int dayOfWeek;
  final String startTime;
  final String endTime;
  final bool isAvailable;

  AvailabilitySlot({
    required this.id,
    required this.dayOfWeek,
    required this.startTime,
    required this.endTime,
    required this.isAvailable,
  });

  factory AvailabilitySlot.fromJson(Map<String, dynamic> json) {
    return AvailabilitySlot(
      id: json['id'],
      dayOfWeek: json['day_of_week'],
      startTime: json['start_time'],
      endTime: json['end_time'],
      isAvailable: json['is_available'] ?? true,
    );
  }

  String get dayName {
    const days = ['Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat', 'Sun'];
    return days[dayOfWeek % 7];
  }
}

/// Time off block DTO
class TimeOffBlock {
  final int id;
  final DateTime startTime;
  final DateTime endTime;
  final String? reason;

  TimeOffBlock({
    required this.id,
    required this.startTime,
    required this.endTime,
    this.reason,
  });

  factory TimeOffBlock.fromJson(Map<String, dynamic> json) {
    return TimeOffBlock(
      id: json['id'],
      startTime: DateTime.parse(json['start_time']),
      endTime: DateTime.parse(json['end_time']),
      reason: json['reason'],
    );
  }
}

/// Provider for schedule service
final scheduleServiceProvider = Provider<ScheduleService>((ref) {
  final client = ref.watch(apiClientProvider);
  return ScheduleService(client);
});
