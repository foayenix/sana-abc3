import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class PractitionerProfileScreen extends StatelessWidget {
  final String practitionerId;

  const PractitionerProfileScreen({
    super.key,
    required this.practitionerId,
  });

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: CustomScrollView(
        slivers: [
          // App Bar
          SliverAppBar(
            expandedHeight: 280,
            pinned: true,
            backgroundColor: SanaColors.surface,
            leading: IconButton(
              icon: Container(
                padding: const EdgeInsets.all(8),
                decoration: BoxDecoration(
                  color: SanaColors.surface,
                  shape: BoxShape.circle,
                ),
                child: const Icon(Icons.arrow_back, size: 20),
              ),
              onPressed: () => context.pop(),
            ),
            actions: [
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: SanaColors.surface,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.favorite_border, size: 20),
                ),
                onPressed: () {},
              ),
              IconButton(
                icon: Container(
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: SanaColors.surface,
                    shape: BoxShape.circle,
                  ),
                  child: const Icon(Icons.share, size: 20),
                ),
                onPressed: () {},
              ),
            ],
            flexibleSpace: FlexibleSpaceBar(
              background: Container(
                decoration: const BoxDecoration(
                  gradient: SanaColors.primaryGradient,
                ),
                child: SafeArea(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const SizedBox(height: 40),
                      const SanaAvatar(
                        name: 'Dr. Emily Chen',
                        size: SanaAvatarSize.xxl,
                        showBorder: true,
                      ),
                      const SizedBox(height: SanaSpacing.md),
                      const Text(
                        'Dr. Emily Chen',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.w700,
                          color: SanaColors.white,
                        ),
                      ),
                      const SizedBox(height: 4),
                      const Text(
                        'Licensed Acupuncturist',
                        style: TextStyle(
                          fontSize: 16,
                          color: SanaColors.white,
                        ),
                      ),
                      const SizedBox(height: SanaSpacing.md),
                      Row(
                        mainAxisAlignment: MainAxisAlignment.center,
                        children: [
                          _StatBadge(value: '4.9', label: 'Rating'),
                          const SizedBox(width: SanaSpacing.lg),
                          _StatBadge(value: '92%', label: 'Outcomes'),
                          const SizedBox(width: SanaSpacing.lg),
                          _StatBadge(value: '8+', label: 'Years'),
                        ],
                      ),
                    ],
                  ),
                ),
              ),
            ),
          ),

          // Content
          SliverToBoxAdapter(
            child: Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  // Quick Info
                  Row(
                    children: [
                      _InfoChip(icon: Icons.location_on, label: 'San Francisco, CA'),
                      const SizedBox(width: SanaSpacing.sm),
                      _InfoChip(icon: Icons.access_time, label: 'Available Today'),
                    ],
                  ),

                  const SizedBox(height: SanaSpacing.lg),

                  // About
                  Text('About', style: SanaTextStyles.heading3),
                  const SizedBox(height: SanaSpacing.sm),
                  Text(
                    'Dr. Emily Chen is a licensed acupuncturist with over 8 years of experience in Traditional Chinese Medicine. She specializes in pain management, stress relief, and women\'s health. Her evidence-based approach combines ancient wisdom with modern research.',
                    style: SanaTextStyles.body.copyWith(
                      color: SanaColors.textSecondary,
                      height: 1.6,
                    ),
                  ),

                  const SizedBox(height: SanaSpacing.lg),

                  // Outcome Metrics
                  Text('Outcome Metrics', style: SanaTextStyles.heading3),
                  const SizedBox(height: SanaSpacing.md),
                  SanaCard(
                    child: Column(
                      children: [
                        _OutcomeMetric(
                          label: 'Pain Reduction',
                          value: 94,
                          color: SanaColors.success,
                        ),
                        const SizedBox(height: SanaSpacing.md),
                        _OutcomeMetric(
                          label: 'Stress Relief',
                          value: 89,
                          color: SanaColors.primaryMedium,
                        ),
                        const SizedBox(height: SanaSpacing.md),
                        _OutcomeMetric(
                          label: 'Sleep Improvement',
                          value: 85,
                          color: SanaColors.info,
                        ),
                      ],
                    ),
                  ),

                  const SizedBox(height: SanaSpacing.lg),

                  // Services
                  Text('Services', style: SanaTextStyles.heading3),
                  const SizedBox(height: SanaSpacing.md),
                  _ServiceItem(
                    name: 'Initial Consultation',
                    duration: '90 min',
                    price: '\$150',
                    description: 'Comprehensive health assessment and first treatment',
                  ),
                  const SizedBox(height: SanaSpacing.sm),
                  _ServiceItem(
                    name: 'Follow-up Session',
                    duration: '60 min',
                    price: '\$100',
                    description: 'Regular acupuncture treatment',
                  ),
                  const SizedBox(height: SanaSpacing.sm),
                  _ServiceItem(
                    name: 'Cupping Therapy',
                    duration: '45 min',
                    price: '\$80',
                    description: 'Traditional cupping for muscle tension',
                  ),

                  const SizedBox(height: SanaSpacing.lg),

                  // Reviews
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Reviews', style: SanaTextStyles.heading3),
                      TextButton(
                        onPressed: () {},
                        child: Text('See All (124)', style: SanaTextStyles.link),
                      ),
                    ],
                  ),
                  const SizedBox(height: SanaSpacing.sm),
                  _ReviewItem(
                    name: 'Sarah M.',
                    rating: 5,
                    date: '2 weeks ago',
                    comment: 'Dr. Chen is amazing! After just 3 sessions, my chronic back pain has significantly improved. Highly recommend!',
                  ),
                  const SizedBox(height: SanaSpacing.sm),
                  _ReviewItem(
                    name: 'James K.',
                    rating: 5,
                    date: '1 month ago',
                    comment: 'Very professional and knowledgeable. She takes time to explain everything and really listens to your concerns.',
                  ),

                  const SizedBox(height: SanaSpacing.xxl),
                ],
              ),
            ),
          ),
        ],
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          boxShadow: [
            BoxShadow(
              color: SanaColors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          child: SanaButton(
            text: 'Book Appointment',
            onPressed: () => context.push('/booking/$practitionerId'),
          ),
        ),
      ),
    );
  }
}

class _StatBadge extends StatelessWidget {
  final String value;
  final String label;

  const _StatBadge({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        Text(
          value,
          style: const TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.w700,
            color: SanaColors.white,
          ),
        ),
        Text(
          label,
          style: TextStyle(
            fontSize: 12,
            color: SanaColors.white.withOpacity(0.8),
          ),
        ),
      ],
    );
  }
}

class _InfoChip extends StatelessWidget {
  final IconData icon;
  final String label;

  const _InfoChip({required this.icon, required this.label});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: SanaColors.grey100,
        borderRadius: BorderRadius.circular(20),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: SanaColors.textSecondary),
          const SizedBox(width: 4),
          Text(label, style: SanaTextStyles.caption),
        ],
      ),
    );
  }
}

class _OutcomeMetric extends StatelessWidget {
  final String label;
  final int value;
  final Color color;

  const _OutcomeMetric({
    required this.label,
    required this.value,
    required this.color,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: SanaTextStyles.bodySmall),
            Text(
              '$value%',
              style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
            ),
          ],
        ),
        const SizedBox(height: 8),
        ClipRRect(
          borderRadius: BorderRadius.circular(4),
          child: LinearProgressIndicator(
            value: value / 100,
            backgroundColor: SanaColors.grey200,
            valueColor: AlwaysStoppedAnimation<Color>(color),
            minHeight: 8,
          ),
        ),
      ],
    );
  }
}

class _ServiceItem extends StatelessWidget {
  final String name;
  final String duration;
  final String price;
  final String description;

  const _ServiceItem({
    required this.name,
    required this.duration,
    required this.price,
    required this.description,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Expanded(
                child: Text(
                  name,
                  style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
                ),
              ),
              Text(
                price,
                style: SanaTextStyles.body.copyWith(
                  fontWeight: FontWeight.w700,
                  color: SanaColors.primaryDark,
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(description, style: SanaTextStyles.caption),
          const SizedBox(height: 8),
          Row(
            children: [
              Icon(Icons.timer_outlined, size: 14, color: SanaColors.textTertiary),
              const SizedBox(width: 4),
              Text(duration, style: SanaTextStyles.caption),
            ],
          ),
        ],
      ),
    );
  }
}

class _ReviewItem extends StatelessWidget {
  final String name;
  final int rating;
  final String date;
  final String comment;

  const _ReviewItem({
    required this.name,
    required this.rating,
    required this.date,
    required this.comment,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              SanaAvatar(name: name, size: SanaAvatarSize.sm),
              const SizedBox(width: SanaSpacing.sm),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(name, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                    Row(
                      children: [
                        ...List.generate(
                          5,
                          (i) => Icon(
                            i < rating ? Icons.star : Icons.star_border,
                            size: 14,
                            color: SanaColors.accent,
                          ),
                        ),
                        const SizedBox(width: 8),
                        Text(date, style: SanaTextStyles.caption),
                      ],
                    ),
                  ],
                ),
              ),
            ],
          ),
          const SizedBox(height: SanaSpacing.sm),
          Text(
            comment,
            style: SanaTextStyles.bodySmall.copyWith(height: 1.5),
          ),
        ],
      ),
    );
  }
}
