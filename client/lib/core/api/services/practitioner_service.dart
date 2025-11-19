import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Practitioner API service
class PractitionerService {
  final ApiClient _client;

  PractitionerService(this._client);

  /// Get list of practitioners
  Future<List<PractitionerDto>> getPractitioners({
    String? specialty,
    double? minRating,
    bool? verifiedOnly,
    String? searchQuery,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/practitioners',
      queryParameters: {
        if (specialty != null) 'specialty': specialty,
        if (minRating != null) 'min_rating': minRating,
        if (verifiedOnly != null) 'verified_only': verifiedOnly,
        if (searchQuery != null) 'q': searchQuery,
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => PractitionerDto.fromJson(json))
        .toList();
  }

  /// Get practitioner by ID
  Future<PractitionerDto> getPractitioner(int id) async {
    final response = await _client.get('/practitioners/$id');
    return PractitionerDto.fromJson(response.data);
  }

  /// Get practitioner's services
  Future<List<ServiceDto>> getServices(int practitionerId) async {
    final response = await _client.get('/practitioners/$practitionerId/services');
    return (response.data as List)
        .map((json) => ServiceDto.fromJson(json))
        .toList();
  }

  /// Get practitioner's availability
  Future<List<TimeSlotDto>> getAvailability(
    int practitionerId, {
    required DateTime date,
  }) async {
    final response = await _client.get(
      '/practitioners/$practitionerId/availability',
      queryParameters: {
        'date': date.toIso8601String().split('T')[0],
      },
    );
    return (response.data as List)
        .map((json) => TimeSlotDto.fromJson(json))
        .toList();
  }

  /// Get practitioner's reviews
  Future<List<ReviewDto>> getReviews(
    int practitionerId, {
    int page = 1,
    int limit = 10,
  }) async {
    final response = await _client.get(
      '/practitioners/$practitionerId/reviews',
      queryParameters: {
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => ReviewDto.fromJson(json))
        .toList();
  }

  /// Get specialties list
  Future<List<String>> getSpecialties() async {
    final response = await _client.get('/practitioners/specialties');
    return List<String>.from(response.data);
  }
}

/// Practitioner DTO
class PractitionerDto {
  final int id;
  final String name;
  final String? title;
  final String? avatar;
  final List<String> specialties;
  final String? bio;
  final double hourlyRate;
  final double rating;
  final int totalReviews;
  final double outcomeScore;
  final bool isVerified;

  PractitionerDto({
    required this.id,
    required this.name,
    this.title,
    this.avatar,
    required this.specialties,
    this.bio,
    required this.hourlyRate,
    required this.rating,
    required this.totalReviews,
    required this.outcomeScore,
    required this.isVerified,
  });

  factory PractitionerDto.fromJson(Map<String, dynamic> json) {
    return PractitionerDto(
      id: json['id'],
      name: json['name'] ?? json['user']?['full_name'] ?? '',
      title: json['title'],
      avatar: json['avatar'] ?? json['user']?['avatar'],
      specialties: List<String>.from(json['specialties'] ?? []),
      bio: json['bio'],
      hourlyRate: (json['hourly_rate'] ?? 0).toDouble(),
      rating: (json['rating'] ?? 0).toDouble(),
      totalReviews: json['total_reviews'] ?? 0,
      outcomeScore: (json['outcome_score'] ?? 0).toDouble(),
      isVerified: json['verification_status'] == 'verified',
    );
  }
}

/// Service DTO
class ServiceDto {
  final int id;
  final String name;
  final String? description;
  final int durationMinutes;
  final double price;

  ServiceDto({
    required this.id,
    required this.name,
    this.description,
    required this.durationMinutes,
    required this.price,
  });

  factory ServiceDto.fromJson(Map<String, dynamic> json) {
    return ServiceDto(
      id: json['id'],
      name: json['name'],
      description: json['description'],
      durationMinutes: json['duration_minutes'] ?? 60,
      price: (json['price'] ?? 0).toDouble(),
    );
  }
}

/// Time slot DTO
class TimeSlotDto {
  final String time;
  final bool isAvailable;

  TimeSlotDto({
    required this.time,
    required this.isAvailable,
  });

  factory TimeSlotDto.fromJson(Map<String, dynamic> json) {
    return TimeSlotDto(
      time: json['time'],
      isAvailable: json['is_available'] ?? true,
    );
  }
}

/// Review DTO
class ReviewDto {
  final int id;
  final int rating;
  final String? comment;
  final String clientName;
  final DateTime createdAt;

  ReviewDto({
    required this.id,
    required this.rating,
    this.comment,
    required this.clientName,
    required this.createdAt,
  });

  factory ReviewDto.fromJson(Map<String, dynamic> json) {
    return ReviewDto(
      id: json['id'],
      rating: json['rating'],
      comment: json['comment'],
      clientName: json['client_name'] ?? 'Anonymous',
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Provider for practitioner service
final practitionerServiceProvider = Provider<PractitionerService>((ref) {
  final client = ref.watch(apiClientProvider);
  return PractitionerService(client);
});
