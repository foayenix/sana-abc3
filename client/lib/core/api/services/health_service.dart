import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Health tracking API service
class HealthService {
  final ApiClient _client;

  HealthService(this._client);

  // Health Score
  Future<HealthScoreDto> getHealthScore() async {
    final response = await _client.get('/health/score');
    return HealthScoreDto.fromJson(response.data);
  }

  Future<List<HealthScoreDto>> getHealthScoreHistory({
    int days = 30,
  }) async {
    final response = await _client.get(
      '/health/score/history',
      queryParameters: {'days': days},
    );
    return (response.data as List)
        .map((json) => HealthScoreDto.fromJson(json))
        .toList();
  }

  Future<Map<String, double>> getHealthDimensions() async {
    final response = await _client.get('/health/dimensions');
    return Map<String, double>.from(response.data);
  }

  // Health Journal
  Future<JournalEntryDto> createJournalEntry({
    required String entryType,
    required String title,
    String? description,
    int? severity,
    List<String>? tags,
  }) async {
    final response = await _client.post(
      '/health/journal',
      data: {
        'entry_type': entryType,
        'title': title,
        if (description != null) 'description': description,
        if (severity != null) 'severity': severity,
        if (tags != null) 'tags': tags,
      },
    );
    return JournalEntryDto.fromJson(response.data);
  }

  Future<List<JournalEntryDto>> getJournalEntries({
    String? entryType,
    DateTime? fromDate,
    DateTime? toDate,
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/health/journal',
      queryParameters: {
        if (entryType != null) 'entry_type': entryType,
        if (fromDate != null) 'from_date': fromDate.toIso8601String(),
        if (toDate != null) 'to_date': toDate.toIso8601String(),
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => JournalEntryDto.fromJson(json))
        .toList();
  }

  Future<JournalEntryDto> updateJournalEntry(
    int id, {
    String? title,
    String? description,
    int? severity,
    List<String>? tags,
  }) async {
    final response = await _client.patch(
      '/health/journal/$id',
      data: {
        if (title != null) 'title': title,
        if (description != null) 'description': description,
        if (severity != null) 'severity': severity,
        if (tags != null) 'tags': tags,
      },
    );
    return JournalEntryDto.fromJson(response.data);
  }

  Future<void> deleteJournalEntry(int id) async {
    await _client.delete('/health/journal/$id');
  }

  // Mood Tracking
  Future<MoodEntryDto> logMood({
    required int moodScore,
    int? energyLevel,
    int? stressLevel,
    String? notes,
  }) async {
    final response = await _client.post(
      '/health/mood',
      data: {
        'mood_score': moodScore,
        if (energyLevel != null) 'energy_level': energyLevel,
        if (stressLevel != null) 'stress_level': stressLevel,
        if (notes != null) 'notes': notes,
      },
    );
    return MoodEntryDto.fromJson(response.data);
  }

  Future<List<MoodEntryDto>> getMoodHistory({
    int days = 30,
  }) async {
    final response = await _client.get(
      '/health/mood',
      queryParameters: {'days': days},
    );
    return (response.data as List)
        .map((json) => MoodEntryDto.fromJson(json))
        .toList();
  }

  Future<MoodAnalytics> getMoodAnalytics({
    String period = 'week',
  }) async {
    final response = await _client.get(
      '/health/mood/analytics',
      queryParameters: {'period': period},
    );
    return MoodAnalytics.fromJson(response.data);
  }

  // Questionnaire
  Future<QuestionnaireResult> submitQuestionnaire(
    Map<String, dynamic> responses,
  ) async {
    final response = await _client.post(
      '/health/questionnaire',
      data: {'responses': responses},
    );
    return QuestionnaireResult.fromJson(response.data);
  }
}

/// Health score DTO
class HealthScoreDto {
  final int score;
  final DateTime date;
  final Map<String, double>? dimensions;

  HealthScoreDto({
    required this.score,
    required this.date,
    this.dimensions,
  });

  factory HealthScoreDto.fromJson(Map<String, dynamic> json) {
    return HealthScoreDto(
      score: json['score'] ?? 0,
      date: json['date'] != null
          ? DateTime.parse(json['date'])
          : DateTime.now(),
      dimensions: json['dimensions'] != null
          ? Map<String, double>.from(json['dimensions'])
          : null,
    );
  }
}

/// Journal entry DTO
class JournalEntryDto {
  final int id;
  final String entryType;
  final String title;
  final String? description;
  final int? severity;
  final List<String> tags;
  final DateTime createdAt;

  JournalEntryDto({
    required this.id,
    required this.entryType,
    required this.title,
    this.description,
    this.severity,
    required this.tags,
    required this.createdAt,
  });

  factory JournalEntryDto.fromJson(Map<String, dynamic> json) {
    return JournalEntryDto(
      id: json['id'],
      entryType: json['entry_type'],
      title: json['title'],
      description: json['description'],
      severity: json['severity'],
      tags: List<String>.from(json['tags'] ?? []),
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Mood entry DTO
class MoodEntryDto {
  final int id;
  final int moodScore;
  final int? energyLevel;
  final int? stressLevel;
  final String? notes;
  final DateTime createdAt;

  MoodEntryDto({
    required this.id,
    required this.moodScore,
    this.energyLevel,
    this.stressLevel,
    this.notes,
    required this.createdAt,
  });

  factory MoodEntryDto.fromJson(Map<String, dynamic> json) {
    return MoodEntryDto(
      id: json['id'],
      moodScore: json['mood_score'],
      energyLevel: json['energy_level'],
      stressLevel: json['stress_level'],
      notes: json['notes'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Mood analytics DTO
class MoodAnalytics {
  final double averageMood;
  final double averageEnergy;
  final double averageStress;
  final String trend;
  final List<DailyMoodData> dailyData;

  MoodAnalytics({
    required this.averageMood,
    required this.averageEnergy,
    required this.averageStress,
    required this.trend,
    required this.dailyData,
  });

  factory MoodAnalytics.fromJson(Map<String, dynamic> json) {
    return MoodAnalytics(
      averageMood: (json['average_mood'] ?? 0).toDouble(),
      averageEnergy: (json['average_energy'] ?? 0).toDouble(),
      averageStress: (json['average_stress'] ?? 0).toDouble(),
      trend: json['trend'] ?? 'stable',
      dailyData: (json['daily_data'] as List? ?? [])
          .map((d) => DailyMoodData.fromJson(d))
          .toList(),
    );
  }
}

/// Daily mood data
class DailyMoodData {
  final DateTime date;
  final double mood;
  final double energy;
  final double stress;

  DailyMoodData({
    required this.date,
    required this.mood,
    required this.energy,
    required this.stress,
  });

  factory DailyMoodData.fromJson(Map<String, dynamic> json) {
    return DailyMoodData(
      date: DateTime.parse(json['date']),
      mood: (json['mood'] ?? 0).toDouble(),
      energy: (json['energy'] ?? 0).toDouble(),
      stress: (json['stress'] ?? 0).toDouble(),
    );
  }
}

/// Questionnaire result
class QuestionnaireResult {
  final int newScore;
  final Map<String, double> dimensions;
  final List<String> recommendations;

  QuestionnaireResult({
    required this.newScore,
    required this.dimensions,
    required this.recommendations,
  });

  factory QuestionnaireResult.fromJson(Map<String, dynamic> json) {
    return QuestionnaireResult(
      newScore: json['new_score'] ?? 0,
      dimensions: Map<String, double>.from(json['dimensions'] ?? {}),
      recommendations: List<String>.from(json['recommendations'] ?? []),
    );
  }
}

/// Provider for health service
final healthServiceProvider = Provider<HealthService>((ref) {
  final client = ref.watch(apiClientProvider);
  return HealthService(client);
});
