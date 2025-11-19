import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/practitioner_provider.dart';
import '../../../core/api/services/practitioner_service.dart';

/// Search screen connected to real data
class SearchScreenConnected extends ConsumerStatefulWidget {
  const SearchScreenConnected({super.key});

  @override
  ConsumerState<SearchScreenConnected> createState() => _SearchScreenConnectedState();
}

class _SearchScreenConnectedState extends ConsumerState<SearchScreenConnected> {
  final _searchController = TextEditingController();
  final _scrollController = ScrollController();

  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(practitionersProvider.notifier).loadPractitioners(refresh: true);
    });

    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _searchController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent - 200) {
      ref.read(practitionersProvider.notifier).loadMore();
    }
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(practitionersProvider);
    final practitioners = ref.watch(filteredPractitionersProvider);
    final selectedSpecialty = ref.watch(selectedSpecialtyProvider);
    final specialtiesAsync = ref.watch(specialtiesProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          children: [
            // Search header
            Padding(
              padding: const EdgeInsets.all(20),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Find a Practitioner', style: SanaTextStyles.heading2),
                  const SizedBox(height: 16),

                  // Search bar
                  TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search practitioners...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                ref.read(searchQueryProvider.notifier).state = '';
                              },
                            )
                          : null,
                      filled: true,
                      fillColor: SanaColors.surface,
                      border: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: SanaColors.grey200),
                      ),
                      enabledBorder: OutlineInputBorder(
                        borderRadius: BorderRadius.circular(12),
                        borderSide: BorderSide(color: SanaColors.grey200),
                      ),
                    ),
                    onChanged: (value) {
                      ref.read(searchQueryProvider.notifier).state = value;
                    },
                  ),

                  const SizedBox(height: 12),

                  // Specialty filters
                  specialtiesAsync.when(
                    data: (specialties) => SizedBox(
                      height: 36,
                      child: ListView(
                        scrollDirection: Axis.horizontal,
                        children: [
                          FilterChip(
                            label: const Text('All'),
                            selected: selectedSpecialty == null,
                            onSelected: (selected) {
                              ref.read(selectedSpecialtyProvider.notifier).state = null;
                            },
                            selectedColor: SanaColors.primaryLightest,
                          ),
                          const SizedBox(width: 8),
                          ...specialties.map((specialty) => Padding(
                            padding: const EdgeInsets.only(right: 8),
                            child: FilterChip(
                              label: Text(specialty),
                              selected: selectedSpecialty == specialty,
                              onSelected: (selected) {
                                ref.read(selectedSpecialtyProvider.notifier).state =
                                    selected ? specialty : null;
                              },
                              selectedColor: SanaColors.primaryLightest,
                            ),
                          )),
                        ],
                      ),
                    ),
                    loading: () => const SizedBox(height: 36),
                    error: (_, __) => const SizedBox(height: 36),
                  ),
                ],
              ),
            ),

            // Results
            Expanded(
              child: state.isLoading && practitioners.isEmpty
                  ? const Center(child: CircularProgressIndicator())
                  : state.error != null && practitioners.isEmpty
                      ? Center(
                          child: Column(
                            mainAxisAlignment: MainAxisAlignment.center,
                            children: [
                              Icon(
                                Icons.error_outline,
                                size: 48,
                                color: SanaColors.grey400,
                              ),
                              const SizedBox(height: 12),
                              Text(
                                'Failed to load practitioners',
                                style: SanaTextStyles.body.copyWith(
                                  color: SanaColors.textSecondary,
                                ),
                              ),
                              const SizedBox(height: 8),
                              TextButton(
                                onPressed: () {
                                  ref.read(practitionersProvider.notifier)
                                      .loadPractitioners(refresh: true);
                                },
                                child: const Text('Retry'),
                              ),
                            ],
                          ),
                        )
                      : practitioners.isEmpty
                          ? Center(
                              child: Column(
                                mainAxisAlignment: MainAxisAlignment.center,
                                children: [
                                  Icon(
                                    Icons.search_off,
                                    size: 48,
                                    color: SanaColors.grey400,
                                  ),
                                  const SizedBox(height: 12),
                                  Text(
                                    'No practitioners found',
                                    style: SanaTextStyles.body.copyWith(
                                      color: SanaColors.textSecondary,
                                    ),
                                  ),
                                ],
                              ),
                            )
                          : RefreshIndicator(
                              onRefresh: () async {
                                await ref.read(practitionersProvider.notifier)
                                    .loadPractitioners(refresh: true);
                              },
                              child: ListView.builder(
                                controller: _scrollController,
                                padding: const EdgeInsets.symmetric(horizontal: 20),
                                itemCount: practitioners.length +
                                    (state.hasMore ? 1 : 0),
                                itemBuilder: (context, index) {
                                  if (index == practitioners.length) {
                                    return const Padding(
                                      padding: EdgeInsets.all(16),
                                      child: Center(
                                        child: CircularProgressIndicator(),
                                      ),
                                    );
                                  }
                                  return _PractitionerCard(
                                    practitioner: practitioners[index],
                                  );
                                },
                              ),
                            ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PractitionerCard extends StatelessWidget {
  final PractitionerDto practitioner;

  const _PractitionerCard({required this.practitioner});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(12)),
      child: InkWell(
        onTap: () => context.push('/practitioner/${practitioner.id}'),
        borderRadius: BorderRadius.circular(12),
        child: Padding(
          padding: const EdgeInsets.all(16),
          child: Row(
            children: [
              // Avatar
              CircleAvatar(
                radius: 32,
                backgroundColor: SanaColors.primaryLightest,
                backgroundImage: practitioner.avatar != null
                    ? NetworkImage(practitioner.avatar!)
                    : null,
                child: practitioner.avatar == null
                    ? Text(
                        practitioner.name[0],
                        style: SanaTextStyles.heading3.copyWith(
                          color: SanaColors.primaryDark,
                        ),
                      )
                    : null,
              ),
              const SizedBox(width: 16),

              // Info
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Row(
                      children: [
                        Expanded(
                          child: Text(
                            practitioner.name,
                            style: SanaTextStyles.bodyBold,
                          ),
                        ),
                        if (practitioner.isVerified)
                          Icon(
                            Icons.verified,
                            size: 18,
                            color: SanaColors.primaryDark,
                          ),
                      ],
                    ),
                    if (practitioner.title != null)
                      Text(
                        practitioner.title!,
                        style: SanaTextStyles.bodySmall.copyWith(
                          color: SanaColors.textSecondary,
                        ),
                      ),
                    const SizedBox(height: 4),
                    Wrap(
                      spacing: 4,
                      children: practitioner.specialties.take(2).map((s) =>
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: SanaColors.primaryLightest,
                            borderRadius: BorderRadius.circular(4),
                          ),
                          child: Text(
                            s,
                            style: SanaTextStyles.caption.copyWith(
                              color: SanaColors.primaryDark,
                            ),
                          ),
                        ),
                      ).toList(),
                    ),
                    const SizedBox(height: 8),
                    Row(
                      children: [
                        Icon(Icons.star, size: 16, color: SanaColors.accent),
                        const SizedBox(width: 4),
                        Text(
                          practitioner.rating.toStringAsFixed(1),
                          style: SanaTextStyles.bodySmall,
                        ),
                        const SizedBox(width: 8),
                        Text(
                          '(${practitioner.totalReviews})',
                          style: SanaTextStyles.caption.copyWith(
                            color: SanaColors.textSecondary,
                          ),
                        ),
                        const Spacer(),
                        Text(
                          '\$${practitioner.hourlyRate.round()}/hr',
                          style: SanaTextStyles.bodyBold.copyWith(
                            color: SanaColors.primaryDark,
                          ),
                        ),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
