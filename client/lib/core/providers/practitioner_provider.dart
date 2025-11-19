import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/practitioner_service.dart';

/// Practitioners list state
class PractitionersState {
  final List<PractitionerDto> practitioners;
  final bool isLoading;
  final bool hasMore;
  final String? error;
  final int currentPage;

  const PractitionersState({
    this.practitioners = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.error,
    this.currentPage = 1,
  });

  PractitionersState copyWith({
    List<PractitionerDto>? practitioners,
    bool? isLoading,
    bool? hasMore,
    String? error,
    int? currentPage,
  }) {
    return PractitionersState(
      practitioners: practitioners ?? this.practitioners,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      error: error,
      currentPage: currentPage ?? this.currentPage,
    );
  }
}

/// Practitioners notifier
class PractitionersNotifier extends StateNotifier<PractitionersState> {
  final PractitionerService _service;

  PractitionersNotifier(this._service) : super(const PractitionersState());

  /// Load practitioners
  Future<void> loadPractitioners({
    String? specialty,
    double? minRating,
    bool? verifiedOnly,
    String? searchQuery,
    bool refresh = false,
  }) async {
    if (state.isLoading) return;

    final page = refresh ? 1 : state.currentPage;

    state = state.copyWith(
      isLoading: true,
      error: null,
      practitioners: refresh ? [] : state.practitioners,
    );

    try {
      final practitioners = await _service.getPractitioners(
        specialty: specialty,
        minRating: minRating,
        verifiedOnly: verifiedOnly,
        searchQuery: searchQuery,
        page: page,
      );

      state = state.copyWith(
        practitioners: refresh
            ? practitioners
            : [...state.practitioners, ...practitioners],
        isLoading: false,
        hasMore: practitioners.length >= 20,
        currentPage: page + 1,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Load more practitioners
  Future<void> loadMore() async {
    if (!state.hasMore || state.isLoading) return;
    await loadPractitioners();
  }

  /// Refresh practitioners
  Future<void> refresh() async {
    await loadPractitioners(refresh: true);
  }
}

/// Practitioners provider
final practitionersProvider =
    StateNotifierProvider<PractitionersNotifier, PractitionersState>((ref) {
  final service = ref.watch(practitionerServiceProvider);
  return PractitionersNotifier(service);
});

/// Single practitioner provider
final practitionerProvider =
    FutureProvider.family<PractitionerDto, int>((ref, id) async {
  final service = ref.watch(practitionerServiceProvider);
  return service.getPractitioner(id);
});

/// Practitioner services provider
final practitionerServicesProvider =
    FutureProvider.family<List<ServiceDto>, int>((ref, practitionerId) async {
  final service = ref.watch(practitionerServiceProvider);
  return service.getServices(practitionerId);
});

/// Practitioner availability provider
final practitionerAvailabilityProvider =
    FutureProvider.family<List<TimeSlotDto>, ({int id, DateTime date})>(
        (ref, params) async {
  final service = ref.watch(practitionerServiceProvider);
  return service.getAvailability(params.id, date: params.date);
});

/// Practitioner reviews provider
final practitionerReviewsProvider =
    FutureProvider.family<List<ReviewDto>, int>((ref, practitionerId) async {
  final service = ref.watch(practitionerServiceProvider);
  return service.getReviews(practitionerId);
});

/// Specialties provider
final specialtiesProvider = FutureProvider<List<String>>((ref) async {
  final service = ref.watch(practitionerServiceProvider);
  return service.getSpecialties();
});

/// Search query provider
final searchQueryProvider = StateProvider<String>((ref) => '');

/// Selected specialty provider
final selectedSpecialtyProvider = StateProvider<String?>((ref) => null);

/// Filtered practitioners provider
final filteredPractitionersProvider = Provider<List<PractitionerDto>>((ref) {
  final practitioners = ref.watch(practitionersProvider).practitioners;
  final query = ref.watch(searchQueryProvider).toLowerCase();
  final specialty = ref.watch(selectedSpecialtyProvider);

  return practitioners.where((p) {
    final matchesQuery = query.isEmpty ||
        p.name.toLowerCase().contains(query) ||
        p.specialties.any((s) => s.toLowerCase().contains(query));
    final matchesSpecialty =
        specialty == null || p.specialties.contains(specialty);
    return matchesQuery && matchesSpecialty;
  }).toList();
});
