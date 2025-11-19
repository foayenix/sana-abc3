import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class AvailabilityScreen extends StatelessWidget {
  const AvailabilityScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Availability'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        children: [
          Text('Working Hours', style: SanaTextStyles.heading3),
          const SizedBox(height: SanaSpacing.md),
          ...['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
              .map((day) => _DaySchedule(day: day, isEnabled: day != 'Sunday')),
          const SizedBox(height: SanaSpacing.lg),
          SanaButton(text: 'Save Changes', onPressed: () => context.pop()),
        ],
      ),
    );
  }
}

class _DaySchedule extends StatefulWidget {
  final String day;
  final bool isEnabled;
  const _DaySchedule({required this.day, required this.isEnabled});
  @override
  State<_DaySchedule> createState() => _DayScheduleState();
}

class _DayScheduleState extends State<_DaySchedule> {
  late bool _enabled;
  @override
  void initState() {
    super.initState();
    _enabled = widget.isEnabled;
  }

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: SanaCard(
        child: Row(
          children: [
            Expanded(child: Text(widget.day, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w500))),
            if (_enabled) Text('9:00 AM - 5:00 PM', style: SanaTextStyles.bodySmall),
            Switch(value: _enabled, onChanged: (v) => setState(() => _enabled = v), activeColor: SanaColors.primaryDark),
          ],
        ),
      ),
    );
  }
}
