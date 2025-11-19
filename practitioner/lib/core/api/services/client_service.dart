import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Client management API service
class ClientService {
  final ApiClient _client;

  ClientService(this._client);

  /// Get practitioner's clients
  Future<List<ClientDto>> getClients({
    String? searchQuery,
    String? sortBy,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/practitioners/me/clients',
      queryParameters: {
        if (searchQuery != null) 'q': searchQuery,
        if (sortBy != null) 'sort_by': sortBy,
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => ClientDto.fromJson(json))
        .toList();
  }

  /// Get client details
  Future<ClientDto> getClient(int clientId) async {
    final response = await _client.get('/practitioners/me/clients/$clientId');
    return ClientDto.fromJson(response.data);
  }

  /// Get client's session history
  Future<List<ClientSessionDto>> getClientSessions(int clientId) async {
    final response = await _client.get(
      '/practitioners/me/clients/$clientId/sessions',
    );
    return (response.data as List)
        .map((json) => ClientSessionDto.fromJson(json))
        .toList();
  }

  /// Add notes for client
  Future<void> addClientNote(int clientId, String note) async {
    await _client.post(
      '/practitioners/me/clients/$clientId/notes',
      data: {'note': note},
    );
  }

  /// Get client notes
  Future<List<ClientNote>> getClientNotes(int clientId) async {
    final response = await _client.get(
      '/practitioners/me/clients/$clientId/notes',
    );
    return (response.data as List)
        .map((json) => ClientNote.fromJson(json))
        .toList();
  }
}

/// Client DTO
class ClientDto {
  final int id;
  final String name;
  final String email;
  final String? phone;
  final String? avatar;
  final DateTime? dateOfBirth;
  final List<String> healthGoals;
  final int totalSessions;
  final DateTime? lastSessionAt;
  final DateTime createdAt;

  ClientDto({
    required this.id,
    required this.name,
    required this.email,
    this.phone,
    this.avatar,
    this.dateOfBirth,
    required this.healthGoals,
    required this.totalSessions,
    this.lastSessionAt,
    required this.createdAt,
  });

  factory ClientDto.fromJson(Map<String, dynamic> json) {
    return ClientDto(
      id: json['id'],
      name: json['name'] ?? json['user']?['full_name'] ?? '',
      email: json['email'] ?? json['user']?['email'] ?? '',
      phone: json['phone'],
      avatar: json['avatar'] ?? json['user']?['avatar'],
      dateOfBirth: json['date_of_birth'] != null
          ? DateTime.parse(json['date_of_birth'])
          : null,
      healthGoals: List<String>.from(json['health_goals'] ?? []),
      totalSessions: json['total_sessions'] ?? 0,
      lastSessionAt: json['last_session_at'] != null
          ? DateTime.parse(json['last_session_at'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  String get initials {
    final parts = name.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return name.isNotEmpty ? name[0].toUpperCase() : '?';
  }
}

/// Client session DTO
class ClientSessionDto {
  final int id;
  final String serviceName;
  final DateTime scheduledAt;
  final String status;
  final String? notes;
  final int? rating;

  ClientSessionDto({
    required this.id,
    required this.serviceName,
    required this.scheduledAt,
    required this.status,
    this.notes,
    this.rating,
  });

  factory ClientSessionDto.fromJson(Map<String, dynamic> json) {
    return ClientSessionDto(
      id: json['id'],
      serviceName: json['service_name'] ?? '',
      scheduledAt: DateTime.parse(json['scheduled_at']),
      status: json['status'],
      notes: json['notes'],
      rating: json['rating'],
    );
  }
}

/// Client note DTO
class ClientNote {
  final int id;
  final String note;
  final DateTime createdAt;

  ClientNote({
    required this.id,
    required this.note,
    required this.createdAt,
  });

  factory ClientNote.fromJson(Map<String, dynamic> json) {
    return ClientNote(
      id: json['id'],
      note: json['note'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Provider for client service
final clientServiceProvider = Provider<ClientService>((ref) {
  final client = ref.watch(apiClientProvider);
  return ClientService(client);
});
