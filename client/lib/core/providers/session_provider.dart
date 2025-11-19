import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/session_service.dart';

/// Sessions state
class SessionsState {
  final List<SessionDto> sessions;
  final bool isLoading;
  final String? error;

  const SessionsState({
    this.sessions = const [],
    this.isLoading = false,
    this.error,
  });

  SessionsState copyWith({
    List<SessionDto>? sessions,
    bool? isLoading,
    String? error,
  }) {
    return SessionsState(
      sessions: sessions ?? this.sessions,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  List<SessionDto> get upcomingSessions =>
      sessions.where((s) => s.isUpcoming && s.status == 'scheduled').toList()
        ..sort((a, b) => a.scheduledAt.compareTo(b.scheduledAt));

  List<SessionDto> get pastSessions =>
      sessions.where((s) => s.isPast || s.status == 'completed').toList()
        ..sort((a, b) => b.scheduledAt.compareTo(a.scheduledAt));
}

/// Sessions notifier
class SessionsNotifier extends StateNotifier<SessionsState> {
  final SessionService _service;

  SessionsNotifier(this._service) : super(const SessionsState());

  /// Load sessions
  Future<void> loadSessions({String? status}) async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final sessions = await _service.getSessions(status: status);
      state = state.copyWith(
        sessions: sessions,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Create booking
  Future<SessionDto> createBooking({
    required int practitionerId,
    required int serviceId,
    required DateTime scheduledAt,
    String? notes,
  }) async {
    final session = await _service.createBooking(
      practitionerId: practitionerId,
      serviceId: serviceId,
      scheduledAt: scheduledAt,
      notes: notes,
    );

    state = state.copyWith(
      sessions: [session, ...state.sessions],
    );

    return session;
  }

  /// Cancel session
  Future<void> cancelSession(int id, {String? reason}) async {
    final updatedSession = await _service.cancelSession(id, reason: reason);

    state = state.copyWith(
      sessions: state.sessions
          .map((s) => s.id == id ? updatedSession : s)
          .toList(),
    );
  }

  /// Reschedule session
  Future<void> rescheduleSession(int id, DateTime newTime) async {
    final updatedSession = await _service.rescheduleSession(id, newTime);

    state = state.copyWith(
      sessions: state.sessions
          .map((s) => s.id == id ? updatedSession : s)
          .toList(),
    );
  }

  /// Submit review
  Future<void> submitReview(
    int sessionId, {
    required int rating,
    String? comment,
  }) async {
    await _service.submitReview(
      sessionId,
      rating: rating,
      comment: comment,
    );

    // Refresh sessions to get updated status
    await loadSessions();
  }

  /// Refresh sessions
  Future<void> refresh() async {
    await loadSessions();
  }
}

/// Sessions provider
final sessionsProvider =
    StateNotifierProvider<SessionsNotifier, SessionsState>((ref) {
  final service = ref.watch(sessionServiceProvider);
  return SessionsNotifier(service);
});

/// Upcoming sessions provider
final upcomingSessionsProvider = Provider<List<SessionDto>>((ref) {
  return ref.watch(sessionsProvider).upcomingSessions;
});

/// Past sessions provider
final pastSessionsProvider = Provider<List<SessionDto>>((ref) {
  return ref.watch(sessionsProvider).pastSessions;
});

/// Single session provider
final sessionProvider =
    FutureProvider.family<SessionDto, int>((ref, id) async {
  final service = ref.watch(sessionServiceProvider);
  return service.getSession(id);
});

/// Upcoming sessions count provider
final upcomingCountProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(sessionServiceProvider);
  return service.getUpcomingCount();
});

/// Booking state for wizard
class BookingState {
  final int? practitionerId;
  final int? serviceId;
  final DateTime? selectedDate;
  final String? selectedTime;
  final String? notes;

  const BookingState({
    this.practitionerId,
    this.serviceId,
    this.selectedDate,
    this.selectedTime,
    this.notes,
  });

  BookingState copyWith({
    int? practitionerId,
    int? serviceId,
    DateTime? selectedDate,
    String? selectedTime,
    String? notes,
  }) {
    return BookingState(
      practitionerId: practitionerId ?? this.practitionerId,
      serviceId: serviceId ?? this.serviceId,
      selectedDate: selectedDate ?? this.selectedDate,
      selectedTime: selectedTime ?? this.selectedTime,
      notes: notes ?? this.notes,
    );
  }

  bool get isComplete =>
      practitionerId != null &&
      serviceId != null &&
      selectedDate != null &&
      selectedTime != null;

  void reset() {}
}

/// Booking state provider
final bookingStateProvider = StateProvider<BookingState>((ref) {
  return const BookingState();
});
