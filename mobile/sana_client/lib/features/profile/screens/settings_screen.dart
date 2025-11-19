import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_card.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  bool _pushNotifications = true;
  bool _emailNotifications = true;
  bool _smsNotifications = false;
  bool _darkMode = false;
  bool _biometricAuth = true;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Settings'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Notifications', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _SettingsSwitch(
                    label: 'Push Notifications',
                    value: _pushNotifications,
                    onChanged: (value) => setState(() => _pushNotifications = value),
                  ),
                  const Divider(height: 1),
                  _SettingsSwitch(
                    label: 'Email Notifications',
                    value: _emailNotifications,
                    onChanged: (value) => setState(() => _emailNotifications = value),
                  ),
                  const Divider(height: 1),
                  _SettingsSwitch(
                    label: 'SMS Notifications',
                    value: _smsNotifications,
                    onChanged: (value) => setState(() => _smsNotifications = value),
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            Text('Appearance', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: _SettingsSwitch(
                label: 'Dark Mode',
                value: _darkMode,
                onChanged: (value) => setState(() => _darkMode = value),
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            Text('Security', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _SettingsSwitch(
                    label: 'Biometric Authentication',
                    value: _biometricAuth,
                    onChanged: (value) => setState(() => _biometricAuth = value),
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Change Password',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Two-Factor Authentication',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            Text('Data & Privacy', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _SettingsItem(
                    label: 'Export My Data',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Privacy Policy',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Terms of Service',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            Text('About', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: EdgeInsets.zero,
              child: Column(
                children: [
                  _SettingsItem(
                    label: 'App Version',
                    trailing: '1.0.0',
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Rate the App',
                    onTap: () {},
                  ),
                  const Divider(height: 1),
                  _SettingsItem(
                    label: 'Contact Support',
                    onTap: () {},
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),
          ],
        ),
      ),
    );
  }
}

class _SettingsSwitch extends StatelessWidget {
  final String label;
  final bool value;
  final ValueChanged<bool> onChanged;

  const _SettingsSwitch({
    required this.label,
    required this.value,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(
        horizontal: SanaSpacing.md,
        vertical: SanaSpacing.sm,
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: SanaTextStyles.body),
          Switch(
            value: value,
            onChanged: onChanged,
            activeColor: SanaColors.primaryDark,
          ),
        ],
      ),
    );
  }
}

class _SettingsItem extends StatelessWidget {
  final String label;
  final String? trailing;
  final VoidCallback? onTap;

  const _SettingsItem({
    required this.label,
    this.trailing,
    this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return InkWell(
      onTap: onTap,
      child: Padding(
        padding: const EdgeInsets.all(SanaSpacing.md),
        child: Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            Text(label, style: SanaTextStyles.body),
            if (trailing != null)
              Text(
                trailing!,
                style: SanaTextStyles.bodySmall,
              )
            else if (onTap != null)
              const Icon(
                Icons.chevron_right,
                color: SanaColors.textTertiary,
              ),
          ],
        ),
      ),
    );
  }
}
