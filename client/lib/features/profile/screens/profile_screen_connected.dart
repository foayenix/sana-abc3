import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/auth_provider.dart';
import '../../../core/providers/messaging_provider.dart';
import '../../../core/router/app_router.dart';

/// Profile screen connected to real data
class ProfileScreenConnected extends ConsumerWidget {
  const ProfileScreenConnected({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final user = ref.watch(currentUserProvider);
    final unreadCount = ref.watch(totalUnreadProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            children: [
              // Profile header
              Container(
                padding: const EdgeInsets.all(20),
                decoration: BoxDecoration(
                  color: SanaColors.surface,
                  borderRadius: BorderRadius.circular(16),
                  border: Border.all(color: SanaColors.grey200),
                ),
                child: Column(
                  children: [
                    CircleAvatar(
                      radius: 40,
                      backgroundColor: SanaColors.primaryLightest,
                      backgroundImage: user?.avatar != null
                          ? NetworkImage(user!.avatar!)
                          : null,
                      child: user?.avatar == null
                          ? Text(
                              user?.initials ?? '?',
                              style: SanaTextStyles.heading2.copyWith(
                                color: SanaColors.primaryDark,
                              ),
                            )
                          : null,
                    ),
                    const SizedBox(height: 12),
                    Text(
                      user?.fullName ?? 'User',
                      style: SanaTextStyles.heading3,
                    ),
                    Text(
                      user?.email ?? '',
                      style: SanaTextStyles.body.copyWith(
                        color: SanaColors.textSecondary,
                      ),
                    ),
                    const SizedBox(height: 16),
                    OutlinedButton(
                      onPressed: () => _editProfile(context),
                      child: const Text('Edit Profile'),
                    ),
                  ],
                ),
              ),

              const SizedBox(height: 24),

              // Menu items
              _MenuSection(
                items: [
                  _MenuItem(
                    icon: Icons.message_outlined,
                    title: 'Messages',
                    trailing: unreadCount > 0
                        ? Container(
                            padding: const EdgeInsets.symmetric(
                              horizontal: 8,
                              vertical: 2,
                            ),
                            decoration: BoxDecoration(
                              color: SanaColors.error,
                              borderRadius: BorderRadius.circular(10),
                            ),
                            child: Text(
                              unreadCount.toString(),
                              style: SanaTextStyles.caption.copyWith(
                                color: SanaColors.white,
                              ),
                            ),
                          )
                        : null,
                    onTap: () => context.push(AppRoutes.messaging),
                  ),
                  _MenuItem(
                    icon: Icons.favorite_outline,
                    title: 'Favorite Practitioners',
                    onTap: () {},
                  ),
                  _MenuItem(
                    icon: Icons.payment_outlined,
                    title: 'Payment Methods',
                    onTap: () {},
                  ),
                ],
              ),

              const SizedBox(height: 16),

              _MenuSection(
                items: [
                  _MenuItem(
                    icon: Icons.notifications_outlined,
                    title: 'Notifications',
                    onTap: () {},
                  ),
                  _MenuItem(
                    icon: Icons.lock_outline,
                    title: 'Privacy & Security',
                    onTap: () {},
                  ),
                  _MenuItem(
                    icon: Icons.settings_outlined,
                    title: 'Settings',
                    onTap: () => context.push(AppRoutes.settings),
                  ),
                ],
              ),

              const SizedBox(height: 16),

              _MenuSection(
                items: [
                  _MenuItem(
                    icon: Icons.help_outline,
                    title: 'Help & Support',
                    onTap: () {},
                  ),
                  _MenuItem(
                    icon: Icons.info_outline,
                    title: 'About SANA',
                    onTap: () {},
                  ),
                ],
              ),

              const SizedBox(height: 16),

              _MenuSection(
                items: [
                  _MenuItem(
                    icon: Icons.logout,
                    title: 'Sign Out',
                    textColor: SanaColors.error,
                    onTap: () => _signOut(context, ref),
                  ),
                ],
              ),

              const SizedBox(height: 24),

              Text(
                'Version 1.0.0',
                style: SanaTextStyles.caption.copyWith(
                  color: SanaColors.textTertiary,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  void _editProfile(BuildContext context) {
    // Navigate to edit profile
  }

  Future<void> _signOut(BuildContext context, WidgetRef ref) async {
    final confirmed = await showDialog<bool>(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Sign Out'),
        content: const Text('Are you sure you want to sign out?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context, false),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () => Navigator.pop(context, true),
            child: const Text('Sign Out'),
          ),
        ],
      ),
    );

    if (confirmed == true) {
      await ref.read(authProvider.notifier).logout();
    }
  }
}

class _MenuSection extends StatelessWidget {
  final List<_MenuItem> items;

  const _MenuSection({required this.items});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(
        color: SanaColors.surface,
        borderRadius: BorderRadius.circular(12),
        border: Border.all(color: SanaColors.grey200),
      ),
      child: Column(
        children: items.asMap().entries.map((entry) {
          final index = entry.key;
          final item = entry.value;
          return Column(
            children: [
              ListTile(
                leading: Icon(
                  item.icon,
                  color: item.textColor ?? SanaColors.textPrimary,
                ),
                title: Text(
                  item.title,
                  style: SanaTextStyles.body.copyWith(
                    color: item.textColor,
                  ),
                ),
                trailing: item.trailing ??
                    Icon(
                      Icons.chevron_right,
                      color: SanaColors.grey400,
                    ),
                onTap: item.onTap,
              ),
              if (index < items.length - 1)
                Divider(height: 1, indent: 56, color: SanaColors.grey200),
            ],
          );
        }).toList(),
      ),
    );
  }
}

class _MenuItem {
  final IconData icon;
  final String title;
  final Widget? trailing;
  final Color? textColor;
  final VoidCallback onTap;

  const _MenuItem({
    required this.icon,
    required this.title,
    this.trailing,
    this.textColor,
    required this.onTap,
  });
}
