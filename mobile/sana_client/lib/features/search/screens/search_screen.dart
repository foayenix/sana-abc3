import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class SearchScreen extends StatefulWidget {
  const SearchScreen({super.key});

  @override
  State<SearchScreen> createState() => _SearchScreenState();
}

class _SearchScreenState extends State<SearchScreen> {
  final _searchController = TextEditingController();
  String _selectedCategory = 'All';

  final List<String> _categories = [
    'All',
    'Acupuncture',
    'Massage',
    'Chiropractic',
    'Naturopathy',
    'Herbalist',
    'Nutrition',
    'Yoga',
  ];

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Find Practitioners',
                    style: SanaTextStyles.heading2,
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  SanaSearchField(
                    controller: _searchController,
                    hint: 'Search by name, specialty, or location',
                    onChanged: (value) {
                      setState(() {});
                    },
                  ),
                ],
              ),
            ),

            // Categories
            SizedBox(
              height: 40,
              child: ListView.builder(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                itemCount: _categories.length,
                itemBuilder: (context, index) {
                  final category = _categories[index];
                  final isSelected = category == _selectedCategory;
                  return Padding(
                    padding: const EdgeInsets.only(right: SanaSpacing.sm),
                    child: FilterChip(
                      label: Text(category),
                      selected: isSelected,
                      onSelected: (selected) {
                        setState(() {
                          _selectedCategory = category;
                        });
                      },
                      selectedColor: SanaColors.primaryLightest,
                      checkmarkColor: SanaColors.primaryDark,
                      labelStyle: TextStyle(
                        color: isSelected
                            ? SanaColors.primaryDark
                            : SanaColors.textSecondary,
                        fontWeight:
                            isSelected ? FontWeight.w600 : FontWeight.w400,
                      ),
                    ),
                  );
                },
              ),
            ),

            const SizedBox(height: SanaSpacing.md),

            // Filters row
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              child: Row(
                children: [
                  _FilterButton(
                    icon: Icons.tune,
                    label: 'Filters',
                    onTap: () => _showFiltersSheet(context),
                  ),
                  const SizedBox(width: SanaSpacing.sm),
                  _FilterButton(
                    icon: Icons.sort,
                    label: 'Sort',
                    onTap: () => _showSortSheet(context),
                  ),
                  const SizedBox(width: SanaSpacing.sm),
                  _FilterButton(
                    icon: Icons.location_on_outlined,
                    label: 'Near Me',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.md),

            // Results count
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              child: Text(
                '24 practitioners found',
                style: SanaTextStyles.bodySmall.copyWith(
                  color: SanaColors.textSecondary,
                ),
              ),
            ),

            const SizedBox(height: SanaSpacing.sm),

            // Results list
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                itemCount: 10,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: SanaSpacing.md),
                    child: _PractitionerListItem(
                      name: 'Dr. ${['Emily Chen', 'Michael Park', 'Sarah Lee', 'James Wilson', 'Lisa Wang', 'David Kim', 'Anna Smith', 'Robert Brown', 'Jennifer Davis', 'Thomas Moore'][index]}',
                      specialty: ['Acupuncture', 'Massage Therapy', 'Naturopathy', 'Chiropractic', 'Herbalist', 'Nutrition', 'Yoga Therapy', 'Acupuncture', 'Massage', 'Naturopathy'][index],
                      rating: [4.9, 4.8, 4.7, 4.9, 4.6, 4.8, 4.7, 4.9, 4.8, 4.6][index],
                      reviewCount: [124, 89, 67, 156, 45, 92, 78, 203, 112, 56][index],
                      outcomeScore: [92, 88, 85, 90, 82, 87, 84, 94, 89, 81][index],
                      distance: '${(index + 1) * 0.5} mi',
                      nextAvailable: index % 3 == 0 ? 'Today' : index % 3 == 1 ? 'Tomorrow' : 'This Week',
                      onTap: () => context.push('/practitioner/$index'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showFiltersSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      backgroundColor: SanaColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const _FiltersSheet(),
    );
  }

  void _showSortSheet(BuildContext context) {
    showModalBottomSheet(
      context: context,
      backgroundColor: SanaColors.surface,
      shape: const RoundedRectangleBorder(
        borderRadius: BorderRadius.vertical(top: Radius.circular(20)),
      ),
      builder: (context) => const _SortSheet(),
    );
  }
}

class _FilterButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;

  const _FilterButton({
    required this.icon,
    required this.label,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: onTap,
      child: Container(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          borderRadius: BorderRadius.circular(8),
          border: Border.all(color: SanaColors.grey200),
        ),
        child: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            Icon(icon, size: 16, color: SanaColors.textSecondary),
            const SizedBox(width: 4),
            Text(
              label,
              style: SanaTextStyles.caption.copyWith(
                fontWeight: FontWeight.w500,
                color: SanaColors.textPrimary,
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _PractitionerListItem extends StatelessWidget {
  final String name;
  final String specialty;
  final double rating;
  final int reviewCount;
  final int outcomeScore;
  final String distance;
  final String nextAvailable;
  final VoidCallback onTap;

  const _PractitionerListItem({
    required this.name,
    required this.specialty,
    required this.rating,
    required this.reviewCount,
    required this.outcomeScore,
    required this.distance,
    required this.nextAvailable,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      onTap: onTap,
      child: Column(
        children: [
          Row(
            children: [
              SanaAvatar(
                name: name,
                size: SanaAvatarSize.lg,
              ),
              const SizedBox(width: SanaSpacing.md),
              Expanded(
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(
                      name,
                      style: SanaTextStyles.body.copyWith(
                        fontWeight: FontWeight.w600,
                      ),
                    ),
                    const SizedBox(height: 2),
                    Text(
                      specialty,
                      style: SanaTextStyles.bodySmall,
                    ),
                    const SizedBox(height: 4),
                    Row(
                      children: [
                        const Icon(
                          Icons.star,
                          size: 14,
                          color: SanaColors.accent,
                        ),
                        const SizedBox(width: 4),
                        Text(
                          '$rating ($reviewCount)',
                          style: SanaTextStyles.caption.copyWith(
                            fontWeight: FontWeight.w500,
                          ),
                        ),
                        const SizedBox(width: 12),
                        Icon(
                          Icons.location_on,
                          size: 14,
                          color: SanaColors.textTertiary,
                        ),
                        const SizedBox(width: 2),
                        Text(
                          distance,
                          style: SanaTextStyles.caption,
                        ),
                      ],
                    ),
                  ],
                ),
              ),
              Column(
                crossAxisAlignment: CrossAxisAlignment.end,
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(
                      horizontal: 8,
                      vertical: 4,
                    ),
                    decoration: BoxDecoration(
                      color: SanaColors.primaryLightest,
                      borderRadius: BorderRadius.circular(6),
                    ),
                    child: Text(
                      '$outcomeScore%',
                      style: const TextStyle(
                        fontSize: 12,
                        fontWeight: FontWeight.w700,
                        color: SanaColors.primaryDark,
                      ),
                    ),
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'Outcomes',
                    style: SanaTextStyles.caption.copyWith(
                      fontSize: 10,
                    ),
                  ),
                ],
              ),
            ],
          ),
          const SizedBox(height: SanaSpacing.md),
          Container(
            padding: const EdgeInsets.all(SanaSpacing.sm),
            decoration: BoxDecoration(
              color: SanaColors.grey50,
              borderRadius: BorderRadius.circular(8),
            ),
            child: Row(
              children: [
                Icon(
                  Icons.access_time,
                  size: 16,
                  color: SanaColors.success,
                ),
                const SizedBox(width: 8),
                Text(
                  'Next available: ',
                  style: SanaTextStyles.caption,
                ),
                Text(
                  nextAvailable,
                  style: SanaTextStyles.caption.copyWith(
                    fontWeight: FontWeight.w600,
                    color: SanaColors.success,
                  ),
                ),
                const Spacer(),
                Text(
                  'Book Now',
                  style: SanaTextStyles.caption.copyWith(
                    fontWeight: FontWeight.w600,
                    color: SanaColors.primaryDark,
                  ),
                ),
                const Icon(
                  Icons.chevron_right,
                  size: 16,
                  color: SanaColors.primaryDark,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}

class _FiltersSheet extends StatelessWidget {
  const _FiltersSheet();

  @override
  Widget build(BuildContext context) {
    return DraggableScrollableSheet(
      initialChildSize: 0.7,
      minChildSize: 0.5,
      maxChildSize: 0.9,
      expand: false,
      builder: (context, scrollController) {
        return Padding(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Center(
                child: Container(
                  width: 40,
                  height: 4,
                  decoration: BoxDecoration(
                    color: SanaColors.grey300,
                    borderRadius: BorderRadius.circular(2),
                  ),
                ),
              ),
              const SizedBox(height: SanaSpacing.lg),
              Text(
                'Filters',
                style: SanaTextStyles.heading3,
              ),
              const SizedBox(height: SanaSpacing.lg),
              // Add filter options here
              Text('Distance', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
              const SizedBox(height: SanaSpacing.sm),
              Slider(
                value: 10,
                min: 1,
                max: 50,
                divisions: 49,
                label: '10 mi',
                activeColor: SanaColors.primaryDark,
                onChanged: (value) {},
              ),
              const SizedBox(height: SanaSpacing.md),
              Text('Outcome Score', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
              const SizedBox(height: SanaSpacing.sm),
              RangeSlider(
                values: const RangeValues(60, 100),
                min: 0,
                max: 100,
                divisions: 20,
                labels: const RangeLabels('60%', '100%'),
                activeColor: SanaColors.primaryDark,
                onChanged: (values) {},
              ),
            ],
          ),
        );
      },
    );
  }
}

class _SortSheet extends StatelessWidget {
  const _SortSheet();

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(SanaSpacing.lg),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Center(
            child: Container(
              width: 40,
              height: 4,
              decoration: BoxDecoration(
                color: SanaColors.grey300,
                borderRadius: BorderRadius.circular(2),
              ),
            ),
          ),
          const SizedBox(height: SanaSpacing.lg),
          Text(
            'Sort By',
            style: SanaTextStyles.heading3,
          ),
          const SizedBox(height: SanaSpacing.md),
          _SortOption(label: 'Relevance', isSelected: true),
          _SortOption(label: 'Highest Rated'),
          _SortOption(label: 'Best Outcomes'),
          _SortOption(label: 'Nearest'),
          _SortOption(label: 'Soonest Available'),
          const SizedBox(height: SanaSpacing.lg),
        ],
      ),
    );
  }
}

class _SortOption extends StatelessWidget {
  final String label;
  final bool isSelected;

  const _SortOption({
    required this.label,
    this.isSelected = false,
  });

  @override
  Widget build(BuildContext context) {
    return ListTile(
      contentPadding: EdgeInsets.zero,
      title: Text(
        label,
        style: SanaTextStyles.body.copyWith(
          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
          color: isSelected ? SanaColors.primaryDark : SanaColors.textPrimary,
        ),
      ),
      trailing: isSelected
          ? const Icon(Icons.check, color: SanaColors.primaryDark)
          : null,
      onTap: () => Navigator.pop(context),
    );
  }
}
