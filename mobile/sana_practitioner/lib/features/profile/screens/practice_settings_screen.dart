import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class PracticeSettingsScreen extends StatelessWidget {
  const PracticeSettingsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Practice Settings'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Practice Information', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Practice Name', hint: 'Chen Acupuncture & Wellness'),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Address', hint: '123 Wellness Street, San Francisco, CA'),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Phone', hint: '+1 (555) 123-4567'),
            const SizedBox(height: SanaSpacing.lg),
            Text('Booking Settings', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: Column(
                children: [
                  _SettingRow(label: 'Accept Online Bookings', value: true),
                  const Divider(),
                  _SettingRow(label: 'Require Deposit', value: false),
                  const Divider(),
                  _SettingRow(label: 'Send Reminders', value: true),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.xl),
            SanaButton(text: 'Save Settings', onPressed: () => context.pop()),
          ],
        ),
      ),
    );
  }
}

class _SettingRow extends StatefulWidget {
  final String label; final bool value;
  const _SettingRow({required this.label, required this.value});
  @override
  State<_SettingRow> createState() => _SettingRowState();
}

class _SettingRowState extends State<_SettingRow> {
  late bool _value;
  @override
  void initState() { super.initState(); _value = widget.value; }
  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: SanaSpacing.xs),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(widget.label, style: SanaTextStyles.body),
          Switch(value: _value, onChanged: (v) => setState(() => _value = v), activeColor: SanaColors.primaryDark),
        ],
      ),
    );
  }
}
