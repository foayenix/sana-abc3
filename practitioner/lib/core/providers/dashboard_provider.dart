import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/dashboard_service.dart';

/// Dashboard state
class DashboardState {
  final DashboardStats? stats;
  final RevenueSummary? revenue;
  final List<SessionDto> todaySessions;
  final List<SessionDto> upcomingSessions;
  final List<ActivityItem> recentActivity;
  final bool isLoading;
  final String? error;

  const DashboardState({
    this.stats,
    this.revenue,
    this.todaySessions = const [],
    this.upcomingSessions = const [],
    this.recentActivity = const [],
    this.isLoading = false,
    this.error,
  });

  DashboardState copyWith({
    DashboardStats? stats,
    RevenueSummary? revenue,
    List<SessionDto>? todaySessions,
    List<SessionDto>? upcomingSessions,
    List<ActivityItem>? recentActivity,
    bool? isLoading,
    String? error,
  }) {
    return DashboardState(
      stats: stats ?? this.stats,
      revenue: revenue ?? this.revenue,
      todaySessions: todaySessions ?? this.todaySessions,
      upcomingSessions: upcomingSessions ?? this.upcomingSessions,
      recentActivity: recentActivity ?? this.recentActivity,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

/// Dashboard notifier
class DashboardNotifier extends StateNotifier<DashboardState> {
  final DashboardService _service;

  DashboardNotifier(this._service) : super(const DashboardState());

  Future<void> loadDashboard() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final results = await Future.wait([
        _service.getStats(),
        _service.getRevenueSummary(),
        _service.getTodaySessions(),
        _service.getUpcomingSessions(),
        _service.getRecentActivity(),
      ]);

      state = state.copyWith(
        stats: results[0] as DashboardStats,
        revenue: results[1] as RevenueSummary,
        todaySessions: results[2] as List<SessionDto>,
        upcomingSessions: results[3] as List<SessionDto>,
        recentActivity: results[4] as List<ActivityItem>,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  Future<void> refresh() async {
    await loadDashboard();
  }
}

/// Dashboard provider
final dashboardProvider =
    StateNotifierProvider<DashboardNotifier, DashboardState>((ref) {
  final service = ref.watch(dashboardServiceProvider);
  return DashboardNotifier(service);
});

/// Today's sessions provider
final todaySessionsProvider = Provider<List<SessionDto>>((ref) {
  return ref.watch(dashboardProvider).todaySessions;
});

/// Upcoming sessions provider
final upcomingSessionsProvider = Provider<List<SessionDto>>((ref) {
  return ref.watch(dashboardProvider).upcomingSessions;
});
