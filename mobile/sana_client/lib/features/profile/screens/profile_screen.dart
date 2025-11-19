import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';

class ProfileScreen extends StatelessWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Profile'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings_outlined),
            onPressed: () => context.push(AppRoutes.settings),
          ),
        ],
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          children: [
            // Profile Header
            SanaCard(
              child: Column(
                children: [
                  const SanaAvatar(
                    name: 'Sarah Johnson',
                    size: SanaAvatarSize.xxl,
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  Text(
                    'Sarah Johnson',
                    style: SanaTextStyles.heading2,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    'sarah.johnson@email.com',
                    style: SanaTextStyles.bodySmall,
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  OutlinedButton(
                    onPressed: () => context.push(AppRoutes.editProfile),
                    child: const Text('Edit Profile'),
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Stats
            Row(
              children: [
                Expanded(
                  child: _StatCard(
                    value: '12',
                    label: 'Sessions',
                  ),
                ),
                const SizedBox(width: SanaSpacing.sm),
                Expanded(
                  child: _StatCard(
                    value: '4',
                    label: 'Practitioners',
                  ),
                ),
                const SizedBox(width: SanaSpacing.sm),
                Expanded(
                  child: _StatCard(
                    value: '78',
                    label: 'Health Score',
                  ),
                ),
              ],
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Menu Items
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuItem(
                    icon: Icons.person_outline,
                    label: 'Personal Information',
                    onTap: () => context.push(AppRoutes.editProfile),
                  ),
                  const Divider(height: 1),
                  _MenuItem(
                    icon: Icons.payment,
                    label: 'Payment Methods',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _MenuItem(
                    icon: Icons.history,
                    label: 'Booking History',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _MenuItem(
                    icon: Icons.favorite_outline,
                    label: 'Saved Practitioners',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.md),

            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuItem(
                    icon: Icons.notifications_outlined,
                    label: 'Notifications',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _MenuItem(
                    icon: Icons.security,
                    label: 'Privacy & Security',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _MenuItem(
                    icon: Icons.help_outline,
                    label: 'Help & Support',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.md),

            SanaCard(
              padding: EdgeInsets.zero,
              child: _MenuItem(
                icon: Icons.logout,
                label: 'Sign Out',
                color: SanaColors.error,
                onTap: () {
                  // TODO: Implement logout
                  context.go(AppRoutes.login);
                },
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String value;
  final String label;

  const _StatCard({required this.value, required this.label});

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        children: [
          Text(
            value,
            style: SanaTextStyles.heading2.copyWith(
              color: SanaColors.primaryDark,
            ),
          ),
          Text(label, style: SanaTextStyles.caption),
        ],
      ),
    );
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onTap;
  final Color? color;

  const _MenuItem({
    required this.icon,
    required this.label,
    required this.onTap,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(SanaSpacing.md),
        child: Row(
          children: [
            Icon(icon, color: color ?? SanaColors.textSecondary),
            const SizedBox(width: SanaSpacing.md),
            Expanded(
              child: Text(
                label,
                style: SanaTextStyles.body.copyWith(
                  color: color ?? SanaColors.textPrimary,
                ),
              ),
            ),
            Icon(
              Icons.chevron_right,
              color: color ?? SanaColors.textTertiary,
            ),
          ],
        ),
      ),
    );
  }
}
