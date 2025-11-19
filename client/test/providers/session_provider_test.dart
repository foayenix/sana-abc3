import 'package:flutter_test/flutter_test.dart';
import 'package:mockito/mockito.dart';
import 'package:mockito/annotations.dart';
import 'package:sana_client/core/providers/session_provider.dart';
import 'package:sana_client/core/api/services/session_service.dart';

@GenerateMocks([SessionService])
import 'session_provider_test.mocks.dart';

void main() {
  late MockSessionService mockService;

  setUp(() {
    mockService = MockSessionService();
  });

  group('SessionsNotifier', () {
    test('initial state is correct', () {
      final notifier = SessionsNotifier(mockService);

      expect(notifier.state.sessions, isEmpty);
      expect(notifier.state.isLoading, isFalse);
      expect(notifier.state.error, isNull);
    });

    test('loadSessions updates state with sessions', () async {
      final sessions = [
        SessionDto(
          id: 1,
          practitionerId: 1,
          practitionerName: 'Dr. Smith',
          serviceName: 'Consultation',
          scheduledAt: DateTime.now().add(Duration(days: 1)),
          duration: 60,
          status: 'scheduled',
          price: 100.0,
        ),
        SessionDto(
          id: 2,
          practitionerId: 2,
          practitionerName: 'Dr. Johnson',
          serviceName: 'Follow-up',
          scheduledAt: DateTime.now().subtract(Duration(days: 1)),
          duration: 30,
          status: 'completed',
          price: 50.0,
        ),
      ];

      when(mockService.getSessions(status: anyNamed('status')))
          .thenAnswer((_) async => sessions);

      final notifier = SessionsNotifier(mockService);
      await notifier.loadSessions();

      expect(notifier.state.sessions.length, 2);
      expect(notifier.state.isLoading, isFalse);
      expect(notifier.state.error, isNull);
    });

    test('loadSessions handles errors', () async {
      when(mockService.getSessions(status: anyNamed('status')))
          .thenThrow(Exception('Network error'));

      final notifier = SessionsNotifier(mockService);
      await notifier.loadSessions();

      expect(notifier.state.sessions, isEmpty);
      expect(notifier.state.isLoading, isFalse);
      expect(notifier.state.error, isNotNull);
    });

    test('createBooking adds session to state', () async {
      final newSession = SessionDto(
        id: 3,
        practitionerId: 1,
        practitionerName: 'Dr. Smith',
        serviceName: 'New Session',
        scheduledAt: DateTime.now().add(Duration(days: 2)),
        duration: 60,
        status: 'scheduled',
        price: 100.0,
      );

      when(mockService.createBooking(
        practitionerId: anyNamed('practitionerId'),
        serviceId: anyNamed('serviceId'),
        scheduledAt: anyNamed('scheduledAt'),
        notes: anyNamed('notes'),
      )).thenAnswer((_) async => newSession);

      final notifier = SessionsNotifier(mockService);
      final result = await notifier.createBooking(
        practitionerId: 1,
        serviceId: 1,
        scheduledAt: DateTime.now().add(Duration(days: 2)),
        notes: 'Test notes',
      );

      expect(result.id, 3);
      expect(notifier.state.sessions.contains(result), isTrue);
    });

    test('cancelSession updates session status', () async {
      final session = SessionDto(
        id: 1,
        practitionerId: 1,
        practitionerName: 'Dr. Smith',
        serviceName: 'Consultation',
        scheduledAt: DateTime.now().add(Duration(days: 1)),
        duration: 60,
        status: 'scheduled',
        price: 100.0,
      );

      final cancelledSession = SessionDto(
        id: 1,
        practitionerId: 1,
        practitionerName: 'Dr. Smith',
        serviceName: 'Consultation',
        scheduledAt: DateTime.now().add(Duration(days: 1)),
        duration: 60,
        status: 'cancelled',
        price: 100.0,
      );

      when(mockService.getSessions(status: anyNamed('status')))
          .thenAnswer((_) async => [session]);
      when(mockService.cancelSession(1, reason: anyNamed('reason')))
          .thenAnswer((_) async => cancelledSession);

      final notifier = SessionsNotifier(mockService);
      await notifier.loadSessions();
      await notifier.cancelSession(1, reason: 'Cannot attend');

      final updatedSession =
          notifier.state.sessions.firstWhere((s) => s.id == 1);
      expect(updatedSession.status, 'cancelled');
    });
  });

  group('SessionsState', () {
    test('upcomingSessions filters correctly', () {
      final state = SessionsState(
        sessions: [
          SessionDto(
            id: 1,
            practitionerId: 1,
            practitionerName: 'Dr. Smith',
            serviceName: 'Session 1',
            scheduledAt: DateTime.now().add(Duration(days: 1)),
            duration: 60,
            status: 'scheduled',
            price: 100.0,
          ),
          SessionDto(
            id: 2,
            practitionerId: 2,
            practitionerName: 'Dr. Johnson',
            serviceName: 'Session 2',
            scheduledAt: DateTime.now().subtract(Duration(days: 1)),
            duration: 30,
            status: 'completed',
            price: 50.0,
          ),
        ],
      );

      expect(state.upcomingSessions.length, 1);
      expect(state.upcomingSessions.first.id, 1);
    });

    test('pastSessions filters correctly', () {
      final state = SessionsState(
        sessions: [
          SessionDto(
            id: 1,
            practitionerId: 1,
            practitionerName: 'Dr. Smith',
            serviceName: 'Session 1',
            scheduledAt: DateTime.now().add(Duration(days: 1)),
            duration: 60,
            status: 'scheduled',
            price: 100.0,
          ),
          SessionDto(
            id: 2,
            practitionerId: 2,
            practitionerName: 'Dr. Johnson',
            serviceName: 'Session 2',
            scheduledAt: DateTime.now().subtract(Duration(days: 1)),
            duration: 30,
            status: 'completed',
            price: 50.0,
          ),
        ],
      );

      expect(state.pastSessions.length, 1);
      expect(state.pastSessions.first.id, 2);
    });
  });

  group('BookingState', () {
    test('isComplete returns true when all fields filled', () {
      final state = BookingState(
        practitionerId: 1,
        serviceId: 1,
        selectedDate: DateTime.now(),
        selectedTime: '09:00',
      );

      expect(state.isComplete, isTrue);
    });

    test('isComplete returns false when missing fields', () {
      final state = BookingState(
        practitionerId: 1,
        serviceId: 1,
      );

      expect(state.isComplete, isFalse);
    });
  });
}
