import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class ClientsScreen extends StatefulWidget {
  const ClientsScreen({super.key});

  @override
  State<ClientsScreen> createState() => _ClientsScreenState();
}

class _ClientsScreenState extends State<ClientsScreen> {
  final _searchController = TextEditingController();
  String _filter = 'All';

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
          children: [
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text('Clients', style: SanaTextStyles.heading2),
                      Text('48 total', style: SanaTextStyles.bodySmall),
                    ],
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  SanaSearchField(
                    controller: _searchController,
                    hint: 'Search clients...',
                  ),
                ],
              ),
            ),
            SizedBox(
              height: 40,
              child: ListView(
                scrollDirection: Axis.horizontal,
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                children: [
                  _FilterChip(label: 'All', isSelected: _filter == 'All', onTap: () => setState(() => _filter = 'All')),
                  _FilterChip(label: 'Active', isSelected: _filter == 'Active', onTap: () => setState(() => _filter = 'Active')),
                  _FilterChip(label: 'New', isSelected: _filter == 'New', onTap: () => setState(() => _filter = 'New')),
                  _FilterChip(label: 'Returning', isSelected: _filter == 'Returning', onTap: () => setState(() => _filter = 'Returning')),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.md),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                itemCount: 12,
                itemBuilder: (context, index) {
                  return Padding(
                    padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
                    child: _ClientItem(
                      name: ['Sarah Johnson', 'Michael Brown', 'Lisa Wang', 'James Kim', 'Anna Smith', 'Robert Davis', 'Jennifer Lee', 'David Park', 'Emily Chen', 'Thomas Moore', 'Maria Garcia', 'Kevin Wilson'][index],
                      email: 'client${index + 1}@email.com',
                      sessions: [8, 12, 3, 6, 15, 4, 9, 7, 11, 2, 5, 10][index],
                      lastVisit: ['2 days ago', '1 week ago', 'Yesterday', '3 days ago', '2 weeks ago', '5 days ago', '1 day ago', '4 days ago', '1 week ago', '3 weeks ago', '6 days ago', '2 days ago'][index],
                      onTap: () => context.push('/clients/$index'),
                    ),
                  );
                },
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: SanaColors.primaryDark,
        child: const Icon(Icons.person_add, color: SanaColors.white),
      ),
    );
  }
}

class _FilterChip extends StatelessWidget {
  final String label;
  final bool isSelected;
  final VoidCallback onTap;

  const _FilterChip({required this.label, required this.isSelected, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(right: SanaSpacing.sm),
      child: FilterChip(
        label: Text(label),
        selected: isSelected,
        onSelected: (_) => onTap(),
        selectedColor: SanaColors.primaryLightest,
        checkmarkColor: SanaColors.primaryDark,
      ),
    );
  }
}

class _ClientItem extends StatelessWidget {
  final String name;
  final String email;
  final int sessions;
  final String lastVisit;
  final VoidCallback onTap;

  const _ClientItem({
    required this.name,
    required this.email,
    required this.sessions,
    required this.lastVisit,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      onTap: onTap,
      child: Row(
        children: [
          SanaAvatar(name: name, size: SanaAvatarSize.md),
          const SizedBox(width: SanaSpacing.md),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(name, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                Text(email, style: SanaTextStyles.caption),
              ],
            ),
          ),
          Column(
            crossAxisAlignment: CrossAxisAlignment.end,
            children: [
              Text('$sessions sessions', style: SanaTextStyles.bodySmall.copyWith(fontWeight: FontWeight.w500)),
              Text(lastVisit, style: SanaTextStyles.caption),
            ],
          ),
        ],
      ),
    );
  }
}
