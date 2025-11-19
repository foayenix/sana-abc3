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
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          children: [
            SanaCard(
              child: Column(
                children: [
                  const SanaAvatar(name: 'Dr. Emily Chen', size: SanaAvatarSize.xxl),
                  const SizedBox(height: SanaSpacing.md),
                  Text('Dr. Emily Chen', style: SanaTextStyles.heading2),
                  Text('Licensed Acupuncturist', style: SanaTextStyles.bodySmall),
                  const SizedBox(height: SanaSpacing.md),
                  Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      _StatBadge(value: '4.9', label: 'Rating'),
                      const SizedBox(width: SanaSpacing.lg),
                      _StatBadge(value: '92%', label: 'Outcomes'),
                      const SizedBox(width: SanaSpacing.lg),
                      _StatBadge(value: '48', label: 'Clients'),
                    ],
                  ),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.lg),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuItem(icon: Icons.person_outline, label: 'Edit Profile', onTap: () => context.push(AppRoutes.editProfile)),
                  const Divider(height: 1),
                  _MenuItem(icon: Icons.store, label: 'Practice Settings', onTap: () => context.push(AppRoutes.practiceSettings)),
                  const Divider(height: 1),
                  _MenuItem(icon: Icons.medical_services, label: 'Services & Pricing', onTap: () => context.push(AppRoutes.services)),
                  const Divider(height: 1),
                  _MenuItem(icon: Icons.account_balance_wallet, label: 'Earnings', onTap: () => context.push(AppRoutes.earnings)),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _MenuItem(icon: Icons.notifications_outlined, label: 'Notifications', onTap: () {}),
                  const Divider(height: 1),
                  _MenuItem(icon: Icons.help_outline, label: 'Help & Support', onTap: () {}),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: _MenuItem(icon: Icons.logout, label: 'Sign Out', color: SanaColors.error, onTap: () => context.go(AppRoutes.login)),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatBadge extends StatelessWidget {
  final String value; final String label;
  const _StatBadge({required this.value, required this.label});
  @override
  Widget build(BuildContext context) {
    return Column(children: [
      Text(value, style: SanaTextStyles.heading3.copyWith(color: SanaColors.primaryDark)),
      Text(label, style: SanaTextStyles.caption),
    ]);
  }
}

class _MenuItem extends StatelessWidget {
  final IconData icon; final String label; final VoidCallback onTap; final Color? color;
  const _MenuItem({required this.icon, required this.label, required this.onTap, this.color});
  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(SanaSpacing.md),
        child: Row(children: [
          Icon(icon, color: color ?? SanaColors.textSecondary),
          const SizedBox(width: SanaSpacing.md),
          Expanded(child: Text(label, style: SanaTextStyles.body.copyWith(color: color))),
          Icon(Icons.chevron_right, color: color ?? SanaColors.textTertiary),
        ]),
      ),
    );
  }
}
