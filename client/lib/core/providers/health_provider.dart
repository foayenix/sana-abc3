import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/health_service.dart';

/// Health state
class HealthState {
  final HealthScoreDto? currentScore;
  final List<HealthScoreDto> scoreHistory;
  final Map<String, double> dimensions;
  final List<JournalEntryDto> journalEntries;
  final List<MoodEntryDto> moodHistory;
  final bool isLoading;
  final String? error;

  const HealthState({
    this.currentScore,
    this.scoreHistory = const [],
    this.dimensions = const {},
    this.journalEntries = const [],
    this.moodHistory = const [],
    this.isLoading = false,
    this.error,
  });

  HealthState copyWith({
    HealthScoreDto? currentScore,
    List<HealthScoreDto>? scoreHistory,
    Map<String, double>? dimensions,
    List<JournalEntryDto>? journalEntries,
    List<MoodEntryDto>? moodHistory,
    bool? isLoading,
    String? error,
  }) {
    return HealthState(
      currentScore: currentScore ?? this.currentScore,
      scoreHistory: scoreHistory ?? this.scoreHistory,
      dimensions: dimensions ?? this.dimensions,
      journalEntries: journalEntries ?? this.journalEntries,
      moodHistory: moodHistory ?? this.moodHistory,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Health notifier
class HealthNotifier extends StateNotifier<HealthState> {
  final HealthService _service;

  HealthNotifier(this._service) : super(const HealthState());

  /// Load all health data
  Future<void> loadHealthData() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final results = await Future.wait([
        _service.getHealthScore(),
        _service.getHealthScoreHistory(),
        _service.getHealthDimensions(),
        _service.getJournalEntries(),
        _service.getMoodHistory(),
      ]);

      state = state.copyWith(
        currentScore: results[0] as HealthScoreDto,
        scoreHistory: results[1] as List<HealthScoreDto>,
        dimensions: results[2] as Map<String, double>,
        journalEntries: results[3] as List<JournalEntryDto>,
        moodHistory: results[4] as List<MoodEntryDto>,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Create journal entry
  Future<void> createJournalEntry({
    required String entryType,
    required String title,
    String? description,
    int? severity,
    List<String>? tags,
  }) async {
    final entry = await _service.createJournalEntry(
      entryType: entryType,
      title: title,
      description: description,
      severity: severity,
      tags: tags,
    );

    state = state.copyWith(
      journalEntries: [entry, ...state.journalEntries],
    );
  }

  /// Update journal entry
  Future<void> updateJournalEntry(
    int id, {
    String? title,
    String? description,
    int? severity,
    List<String>? tags,
  }) async {
    final entry = await _service.updateJournalEntry(
      id,
      title: title,
      description: description,
      severity: severity,
      tags: tags,
    );

    state = state.copyWith(
      journalEntries: state.journalEntries
          .map((e) => e.id == id ? entry : e)
          .toList(),
    );
  }

  /// Delete journal entry
  Future<void> deleteJournalEntry(int id) async {
    await _service.deleteJournalEntry(id);

    state = state.copyWith(
      journalEntries: state.journalEntries.where((e) => e.id != id).toList(),
    );
  }

  /// Log mood
  Future<void> logMood({
    required int moodScore,
    int? energyLevel,
    int? stressLevel,
    String? notes,
  }) async {
    final entry = await _service.logMood(
      moodScore: moodScore,
      energyLevel: energyLevel,
      stressLevel: stressLevel,
      notes: notes,
    );

    state = state.copyWith(
      moodHistory: [entry, ...state.moodHistory],
    );
  }

  /// Submit questionnaire
  Future<QuestionnaireResult> submitQuestionnaire(
    Map<String, dynamic> responses,
  ) async {
    final result = await _service.submitQuestionnaire(responses);

    // Refresh health data after questionnaire
    await loadHealthData();

    return result;
  }

  /// Refresh health data
  Future<void> refresh() async {
    await loadHealthData();
  }
}

/// Health provider
final healthProvider =
    StateNotifierProvider<HealthNotifier, HealthState>((ref) {
  final service = ref.watch(healthServiceProvider);
  return HealthNotifier(service);
});

/// Current health score provider
final currentHealthScoreProvider = Provider<int>((ref) {
  return ref.watch(healthProvider).currentScore?.score ?? 0;
});

/// Health dimensions provider
final healthDimensionsProvider = Provider<Map<String, double>>((ref) {
  return ref.watch(healthProvider).dimensions;
});

/// Journal entries provider
final journalEntriesProvider = Provider<List<JournalEntryDto>>((ref) {
  return ref.watch(healthProvider).journalEntries;
});

/// Mood history provider
final moodHistoryProvider = Provider<List<MoodEntryDto>>((ref) {
  return ref.watch(healthProvider).moodHistory;
});

/// Today's mood provider
final todaysMoodProvider = Provider<MoodEntryDto?>((ref) {
  final history = ref.watch(moodHistoryProvider);
  final today = DateTime.now();

  for (final entry in history) {
    if (entry.createdAt.year == today.year &&
        entry.createdAt.month == today.month &&
        entry.createdAt.day == today.day) {
      return entry;
    }
  }
  return null;
});

/// Mood analytics provider
final moodAnalyticsProvider =
    FutureProvider.family<MoodAnalytics, String>((ref, period) async {
  final service = ref.watch(healthServiceProvider);
  return service.getMoodAnalytics(period: period);
});
