import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:sana_client/core/providers/health_provider.dart';
import 'package:sana_client/core/api/services/health_service.dart';

@GenerateMocks([HealthService])
import 'health_provider_test.mocks.dart';

void main() {
  late MockHealthService mockService;

  setUp(() {
    mockService = MockHealthService();
  });

  group('HealthNotifier', () {
    test('initial state is correct', () {
      final notifier = HealthNotifier(mockService);

      expect(notifier.state.currentScore, isNull);
      expect(notifier.state.journalEntries, isEmpty);
      expect(notifier.state.moodHistory, isEmpty);
      expect(notifier.state.isLoading, isFalse);
    });

    test('loadHealthData fetches all health data', () async {
      final healthScore = HealthScoreDto(
        id: 1,
        score: 75,
        calculatedAt: DateTime.now(),
      );

      when(mockService.getHealthScore()).thenAnswer((_) async => healthScore);
      when(mockService.getHealthScoreHistory())
          .thenAnswer((_) async => [healthScore]);
      when(mockService.getHealthDimensions()).thenAnswer((_) async => {
            'physical': 80.0,
            'mental': 70.0,
            'nutrition': 75.0,
          });
      when(mockService.getJournalEntries()).thenAnswer((_) async => []);
      when(mockService.getMoodHistory()).thenAnswer((_) async => []);

      final notifier = HealthNotifier(mockService);
      await notifier.loadHealthData();

      expect(notifier.state.currentScore, healthScore);
      expect(notifier.state.dimensions['physical'], 80.0);
      expect(notifier.state.isLoading, isFalse);
    });

    test('createJournalEntry adds entry to state', () async {
      final entry = JournalEntryDto(
        id: 1,
        entryType: 'symptom',
        title: 'Headache',
        description: 'Mild headache in the morning',
        severity: 3,
        createdAt: DateTime.now(),
      );

      when(mockService.createJournalEntry(
        entryType: anyNamed('entryType'),
        title: anyNamed('title'),
        description: anyNamed('description'),
        severity: anyNamed('severity'),
        tags: anyNamed('tags'),
      )).thenAnswer((_) async => entry);

      final notifier = HealthNotifier(mockService);
      await notifier.createJournalEntry(
        entryType: 'symptom',
        title: 'Headache',
        description: 'Mild headache in the morning',
        severity: 3,
      );

      expect(notifier.state.journalEntries.length, 1);
      expect(notifier.state.journalEntries.first.title, 'Headache');
    });

    test('deleteJournalEntry removes entry from state', () async {
      final entry = JournalEntryDto(
        id: 1,
        entryType: 'symptom',
        title: 'Headache',
        createdAt: DateTime.now(),
      );

      when(mockService.createJournalEntry(
        entryType: anyNamed('entryType'),
        title: anyNamed('title'),
        description: anyNamed('description'),
        severity: anyNamed('severity'),
        tags: anyNamed('tags'),
      )).thenAnswer((_) async => entry);
      when(mockService.deleteJournalEntry(1)).thenAnswer((_) async {});

      final notifier = HealthNotifier(mockService);
      await notifier.createJournalEntry(
        entryType: 'symptom',
        title: 'Headache',
      );
      expect(notifier.state.journalEntries.length, 1);

      await notifier.deleteJournalEntry(1);
      expect(notifier.state.journalEntries, isEmpty);
    });

    test('logMood adds mood entry to state', () async {
      final moodEntry = MoodEntryDto(
        id: 1,
        moodScore: 4,
        energyLevel: 3,
        stressLevel: 2,
        createdAt: DateTime.now(),
      );

      when(mockService.logMood(
        moodScore: anyNamed('moodScore'),
        energyLevel: anyNamed('energyLevel'),
        stressLevel: anyNamed('stressLevel'),
        notes: anyNamed('notes'),
      )).thenAnswer((_) async => moodEntry);

      final notifier = HealthNotifier(mockService);
      await notifier.logMood(
        moodScore: 4,
        energyLevel: 3,
        stressLevel: 2,
      );

      expect(notifier.state.moodHistory.length, 1);
      expect(notifier.state.moodHistory.first.moodScore, 4);
    });
  });
}
