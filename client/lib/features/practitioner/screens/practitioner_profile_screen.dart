import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/practitioner_provider.dart';
import '../../../shared/widgets/sana_button.dart';

class PractitionerProfileScreen extends ConsumerWidget {
  final int practitionerId;

  const PractitionerProfileScreen({super.key, required this.practitionerId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final practitionerAsync = ref.watch(practitionerProvider(practitionerId));
    final servicesAsync = ref.watch(practitionerServicesProvider(practitionerId));
    final reviewsAsync = ref.watch(practitionerReviewsProvider(practitionerId));

    return Scaffold(
      backgroundColor: SanaColors.background,
      body: practitionerAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (practitioner) => CustomScrollView(
          slivers: [
            // App Bar with profile image
            SliverAppBar(
              expandedHeight: 200,
              pinned: true,
              flexibleSpace: FlexibleSpaceBar(
                background: Container(
                  decoration: BoxDecoration(
                    gradient: SanaColors.primaryGradient,
                  ),
                  child: Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        const SizedBox(height: 40),
                        CircleAvatar(
                          radius: 50,
                          backgroundColor: SanaColors.white,
                          backgroundImage: practitioner.avatar != null
                              ? NetworkImage(practitioner.avatar!)
                              : null,
                          child: practitioner.avatar == null
                              ? Text(
                                  practitioner.name[0],
                                  style: SanaTextStyles.heading1.copyWith(
                                    color: SanaColors.primaryDark,
                                  ),
                                )
                              : null,
                        ),
                      ],
                    ),
                  ),
                ),
              ),
            ),

            SliverToBoxAdapter(
              child: Padding(
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Name and verification
                    Row(
                      children: [
                        Expanded(
                          child: Text(practitioner.name, style: SanaTextStyles.heading2),
                        ),
                        if (practitioner.isVerified)
                          Container(
                            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                            decoration: BoxDecoration(
                              color: SanaColors.successLight,
                              borderRadius: BorderRadius.circular(4),
                            ),
                            child: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                const Icon(Icons.verified, size: 14, color: SanaColors.success),
                                const SizedBox(width: 4),
                                Text('Verified', style: SanaTextStyles.caption.copyWith(color: SanaColors.success)),
                              ],
                            ),
                          ),
                      ],
                    ),
                    if (practitioner.title != null)
                      Text(practitioner.title!, style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary)),
                    const SizedBox(height: 16),

                    // Stats
                    Row(
                      children: [
                        _StatItem(icon: Icons.star, value: practitioner.rating.toStringAsFixed(1), label: 'Rating'),
                        _StatItem(icon: Icons.reviews, value: practitioner.totalReviews.toString(), label: 'Reviews'),
                        _StatItem(icon: Icons.trending_up, value: '${practitioner.outcomeScore.round()}%', label: 'Outcomes'),
                      ],
                    ),
                    const SizedBox(height: 24),

                    // Bio
                    if (practitioner.bio != null) ...[
                      Text('About', style: SanaTextStyles.heading3),
                      const SizedBox(height: 8),
                      Text(practitioner.bio!, style: SanaTextStyles.body),
                      const SizedBox(height: 24),
                    ],

                    // Specialties
                    Text('Specialties', style: SanaTextStyles.heading3),
                    const SizedBox(height: 8),
                    Wrap(
                      spacing: 8,
                      runSpacing: 8,
                      children: practitioner.specialties.map((s) => Chip(
                        label: Text(s),
                        backgroundColor: SanaColors.primaryLightest,
                      )).toList(),
                    ),
                    const SizedBox(height: 24),

                    // Services
                    Text('Services', style: SanaTextStyles.heading3),
                    const SizedBox(height: 8),
                    servicesAsync.when(
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (e, _) => Text('Error loading services'),
                      data: (services) => Column(
                        children: services.map((service) => Card(
                          margin: const EdgeInsets.only(bottom: 8),
                          child: ListTile(
                            title: Text(service.name, style: SanaTextStyles.bodyBold),
                            subtitle: Text('${service.durationMinutes} min'),
                            trailing: Text(
                              '\$${service.price.round()}',
                              style: SanaTextStyles.bodyBold.copyWith(color: SanaColors.primaryDark),
                            ),
                          ),
                        )).toList(),
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Reviews
                    Text('Reviews', style: SanaTextStyles.heading3),
                    const SizedBox(height: 8),
                    reviewsAsync.when(
                      loading: () => const Center(child: CircularProgressIndicator()),
                      error: (e, _) => const Text('Error loading reviews'),
                      data: (reviews) => reviews.isEmpty
                          ? Text('No reviews yet', style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary))
                          : Column(
                              children: reviews.take(3).map((review) => _ReviewCard(review: review)).toList(),
                            ),
                    ),
                    const SizedBox(height: 100),
                  ],
                ),
              ),
            ),
          ],
        ),
      ),
      bottomNavigationBar: practitionerAsync.when(
        loading: () => null,
        error: (_, __) => null,
        data: (practitioner) => Container(
          padding: EdgeInsets.only(
            left: 20,
            right: 20,
            top: 16,
            bottom: MediaQuery.of(context).padding.bottom + 16,
          ),
          decoration: BoxDecoration(
            color: SanaColors.surface,
            boxShadow: [
              BoxShadow(
                color: Colors.black.withValues(alpha: 0.1),
                blurRadius: 10,
                offset: const Offset(0, -2),
              ),
            ],
          ),
          child: Row(
            children: [
              Column(
                mainAxisSize: MainAxisSize.min,
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('From', style: SanaTextStyles.caption),
                  Text(
                    '\$${practitioner.hourlyRate.round()}/hr',
                    style: SanaTextStyles.heading3.copyWith(color: SanaColors.primaryDark),
                  ),
                ],
              ),
              const SizedBox(width: 24),
              Expanded(
                child: SanaButton(
                  text: 'Book Session',
                  onPressed: () => context.push('/booking/$practitionerId'),
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _StatItem extends StatelessWidget {
  final IconData icon;
  final String value;
  final String label;

  const _StatItem({required this.icon, required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Column(
        children: [
          Icon(icon, color: SanaColors.accent, size: 20),
          const SizedBox(height: 4),
          Text(value, style: SanaTextStyles.bodyBold),
          Text(label, style: SanaTextStyles.caption),
        ],
      ),
    );
  }
}

class _ReviewCard extends StatelessWidget {
  final dynamic review;

  const _ReviewCard({required this.review});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: Padding(
        padding: const EdgeInsets.all(12),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Text(review.clientName, style: SanaTextStyles.bodyBold),
                const Spacer(),
                ...List.generate(5, (i) => Icon(
                  i < review.rating ? Icons.star : Icons.star_border,
                  size: 16,
                  color: SanaColors.accent,
                )),
              ],
            ),
            if (review.comment != null) ...[
              const SizedBox(height: 8),
              Text(review.comment, style: SanaTextStyles.body),
            ],
          ],
        ),
      ),
    );
  }
}
