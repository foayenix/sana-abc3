import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Session/Booking API service
class SessionService {
  final ApiClient _client;

  SessionService(this._client);

  /// Create a new booking
  Future<SessionDto> createBooking({
    required int practitionerId,
    required int serviceId,
    required DateTime scheduledAt,
    String? notes,
  }) async {
    final response = await _client.post(
      '/sessions/book',
      data: {
        'practitioner_id': practitionerId,
        'service_id': serviceId,
        'scheduled_at': scheduledAt.toIso8601String(),
        if (notes != null) 'notes': notes,
      },
    );
    return SessionDto.fromJson(response.data);
  }

  /// Get user's sessions
  Future<List<SessionDto>> getSessions({
    String? status,
    DateTime? fromDate,
    DateTime? toDate,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/sessions',
      queryParameters: {
        if (status != null) 'status': status,
        if (fromDate != null) 'from_date': fromDate.toIso8601String(),
        if (toDate != null) 'to_date': toDate.toIso8601String(),
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => SessionDto.fromJson(json))
        .toList();
  }

  /// Get session by ID
  Future<SessionDto> getSession(int id) async {
    final response = await _client.get('/sessions/$id');
    return SessionDto.fromJson(response.data);
  }

  /// Cancel a session
  Future<SessionDto> cancelSession(int id, {String? reason}) async {
    final response = await _client.post(
      '/sessions/$id/cancel',
      data: {
        if (reason != null) 'reason': reason,
      },
    );
    return SessionDto.fromJson(response.data);
  }

  /// Reschedule a session
  Future<SessionDto> rescheduleSession(int id, DateTime newTime) async {
    final response = await _client.post(
      '/sessions/$id/reschedule',
      data: {
        'new_time': newTime.toIso8601String(),
      },
    );
    return SessionDto.fromJson(response.data);
  }

  /// Submit session review
  Future<void> submitReview(
    int sessionId, {
    required int rating,
    String? comment,
    bool? wouldRecommend,
  }) async {
    await _client.post(
      '/sessions/$sessionId/review',
      data: {
        'rating': rating,
        if (comment != null) 'comment': comment,
        if (wouldRecommend != null) 'would_recommend': wouldRecommend,
      },
    );
  }

  /// Get upcoming sessions count
  Future<int> getUpcomingCount() async {
    final response = await _client.get('/sessions/upcoming/count');
    return response.data['count'] ?? 0;
  }

  /// Get session payment info
  Future<PaymentInfo> getPaymentInfo(int sessionId) async {
    final response = await _client.get('/sessions/$sessionId/payment');
    return PaymentInfo.fromJson(response.data);
  }

  /// Process payment for session
  Future<PaymentResult> processPayment(
    int sessionId, {
    required String paymentMethodId,
  }) async {
    final response = await _client.post(
      '/sessions/$sessionId/payment',
      data: {
        'payment_method_id': paymentMethodId,
      },
    );
    return PaymentResult.fromJson(response.data);
  }
}

/// Session DTO
class SessionDto {
  final int id;
  final int practitionerId;
  final String practitionerName;
  final String? practitionerAvatar;
  final int serviceId;
  final String serviceName;
  final DateTime scheduledAt;
  final int durationMinutes;
  final double price;
  final String status;
  final String? notes;
  final String? meetingLink;
  final DateTime createdAt;

  SessionDto({
    required this.id,
    required this.practitionerId,
    required this.practitionerName,
    this.practitionerAvatar,
    required this.serviceId,
    required this.serviceName,
    required this.scheduledAt,
    required this.durationMinutes,
    required this.price,
    required this.status,
    this.notes,
    this.meetingLink,
    required this.createdAt,
  });

  factory SessionDto.fromJson(Map<String, dynamic> json) {
    return SessionDto(
      id: json['id'],
      practitionerId: json['practitioner_id'],
      practitionerName: json['practitioner']?['name'] ?? json['practitioner_name'] ?? '',
      practitionerAvatar: json['practitioner']?['avatar'],
      serviceId: json['service_id'],
      serviceName: json['service']?['name'] ?? json['service_name'] ?? '',
      scheduledAt: DateTime.parse(json['scheduled_at']),
      durationMinutes: json['duration_minutes'] ?? 60,
      price: (json['price'] ?? 0).toDouble(),
      status: json['status'] ?? 'scheduled',
      notes: json['notes'],
      meetingLink: json['meeting_link'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  bool get isUpcoming => scheduledAt.isAfter(DateTime.now());
  bool get isPast => scheduledAt.isBefore(DateTime.now());
  bool get canCancel => status == 'scheduled' && isUpcoming;
  bool get canReschedule => status == 'scheduled' && isUpcoming;
}

/// Payment info DTO
class PaymentInfo {
  final double amount;
  final String currency;
  final String? clientSecret;

  PaymentInfo({
    required this.amount,
    required this.currency,
    this.clientSecret,
  });

  factory PaymentInfo.fromJson(Map<String, dynamic> json) {
    return PaymentInfo(
      amount: (json['amount'] ?? 0).toDouble(),
      currency: json['currency'] ?? 'USD',
      clientSecret: json['client_secret'],
    );
  }
}

/// Payment result DTO
class PaymentResult {
  final bool success;
  final String? transactionId;
  final String? errorMessage;

  PaymentResult({
    required this.success,
    this.transactionId,
    this.errorMessage,
  });

  factory PaymentResult.fromJson(Map<String, dynamic> json) {
    return PaymentResult(
      success: json['success'] ?? false,
      transactionId: json['transaction_id'],
      errorMessage: json['error_message'],
    );
  }
}

/// Provider for session service
final sessionServiceProvider = Provider<SessionService>((ref) {
  final client = ref.watch(apiClientProvider);
  return SessionService(client);
});
