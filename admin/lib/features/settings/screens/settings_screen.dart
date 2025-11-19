import 'package:flutter/material.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Settings', style: SanaTextStyles.heading1),
            const SizedBox(height: 32),
            _SettingsSection(title: 'Platform Settings', children: [
              _SettingRow(label: 'Platform Fee (%)', trailing: const SizedBox(width: 100, child: TextField(decoration: InputDecoration(hintText: '10')))),
              _SettingRow(label: 'Allow New Registrations', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'Require Email Verification', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'Auto-approve Practitioners', trailing: Switch(value: false, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
            ]),
            const SizedBox(height: 24),
            _SettingsSection(title: 'Email Notifications', children: [
              _SettingRow(label: 'New User Registration', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'New Practitioner Application', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'Daily Reports', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'Weekly Summary', trailing: Switch(value: true, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
            ]),
            const SizedBox(height: 24),
            _SettingsSection(title: 'Security', children: [
              _SettingRow(label: 'Two-Factor Authentication', trailing: Switch(value: false, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
              _SettingRow(label: 'Session Timeout (minutes)', trailing: const SizedBox(width: 100, child: TextField(decoration: InputDecoration(hintText: '30')))),
              _SettingRow(label: 'IP Whitelisting', trailing: Switch(value: false, onChanged: (_) {}, activeColor: SanaColors.primaryDark)),
            ]),
            const SizedBox(height: 32),
            ElevatedButton(onPressed: () {}, child: const Padding(padding: EdgeInsets.symmetric(horizontal: 24, vertical: 12), child: Text('Save Settings'))),
          ],
        ),
      ),
    );
  }
}

class _SettingsSection extends StatelessWidget {
  final String title;
  final List<Widget> children;
  const _SettingsSection({required this.title, required this.children});

  @override
  Widget build(BuildContext context) {
    return Container(
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Padding(padding: const EdgeInsets.all(20), child: Text(title, style: SanaTextStyles.heading3)),
          const Divider(height: 1),
          ...children,
        ],
      ),
    );
  }
}

class _SettingRow extends StatelessWidget {
  final String label;
  final Widget trailing;
  const _SettingRow({required this.label, required this.trailing});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [Text(label, style: SanaTextStyles.body), trailing],
      ),
    );
  }
}
