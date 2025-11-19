import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';

class CalendarScreen extends StatefulWidget {
  const CalendarScreen({super.key});

  @override
  State<CalendarScreen> createState() => _CalendarScreenState();
}

class _CalendarScreenState extends State<CalendarScreen> {
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  CalendarFormat _calendarFormat = CalendarFormat.week;

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Calendar', style: SanaTextStyles.heading2),
                  TextButton.icon(
                    onPressed: () => context.push(AppRoutes.availability),
                    icon: const Icon(Icons.schedule, size: 18),
                    label: const Text('Availability'),
                  ),
                ],
              ),
            ),
            SanaCard(
              margin: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              padding: const EdgeInsets.all(SanaSpacing.sm),
              child: TableCalendar(
                firstDay: DateTime.now().subtract(const Duration(days: 365)),
                lastDay: DateTime.now().add(const Duration(days: 365)),
                focusedDay: _focusedDay,
                calendarFormat: _calendarFormat,
                selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                onDaySelected: (selectedDay, focusedDay) {
                  setState(() {
                    _selectedDay = selectedDay;
                    _focusedDay = focusedDay;
                  });
                },
                onFormatChanged: (format) {
                  setState(() => _calendarFormat = format);
                },
                calendarStyle: const CalendarStyle(
                  selectedDecoration: BoxDecoration(
                    color: SanaColors.primaryDark,
                    shape: BoxShape.circle,
                  ),
                  todayDecoration: BoxDecoration(
                    color: SanaColors.primaryLight,
                    shape: BoxShape.circle,
                  ),
                ),
                headerStyle: const HeaderStyle(
                  formatButtonVisible: true,
                  titleCentered: true,
                ),
              ),
            ),
            const SizedBox(height: SanaSpacing.md),
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
              child: Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text(
                    _selectedDay != null
                        ? 'Sessions on ${_selectedDay!.day}/${_selectedDay!.month}'
                        : "Today's Sessions",
                    style: SanaTextStyles.heading3,
                  ),
                  Text('3 sessions', style: SanaTextStyles.caption),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.sm),
            Expanded(
              child: ListView(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                children: [
                  _TimeSlot(time: '9:00 AM', session: _SessionBlock(clientName: 'Sarah Johnson', service: 'Acupuncture', duration: '60 min')),
                  _TimeSlot(time: '10:00 AM', session: null),
                  _TimeSlot(time: '11:00 AM', session: _SessionBlock(clientName: 'Michael Brown', service: 'Follow-up', duration: '60 min')),
                  _TimeSlot(time: '12:00 PM', session: null),
                  _TimeSlot(time: '1:00 PM', session: null),
                  _TimeSlot(time: '2:00 PM', session: _SessionBlock(clientName: 'Lisa Wang', service: 'Initial Consultation', duration: '90 min')),
                  _TimeSlot(time: '3:00 PM', session: null),
                  _TimeSlot(time: '4:00 PM', session: null),
                ],
              ),
            ),
          ],
        ),
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: SanaColors.primaryDark,
        child: const Icon(Icons.add, color: SanaColors.white),
      ),
    );
  }
}

class _TimeSlot extends StatelessWidget {
  final String time;
  final _SessionBlock? session;

  const _TimeSlot({required this.time, this.session});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: Row(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          SizedBox(
            width: 70,
            child: Text(time, style: SanaTextStyles.caption),
          ),
          Expanded(
            child: session ??
                Container(
                  height: 60,
                  decoration: BoxDecoration(
                    border: Border(
                      top: BorderSide(color: SanaColors.grey200),
                    ),
                  ),
                ),
          ),
        ],
      ),
    );
  }
}

class _SessionBlock extends StatelessWidget {
  final String clientName;
  final String service;
  final String duration;

  const _SessionBlock({
    required this.clientName,
    required this.service,
    required this.duration,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(SanaSpacing.sm),
      decoration: BoxDecoration(
        color: SanaColors.primaryLightest,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: SanaColors.primaryLight),
      ),
      child: Row(
        children: [
          SanaAvatar(name: clientName, size: SanaAvatarSize.sm),
          const SizedBox(width: SanaSpacing.sm),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(clientName, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600, fontSize: 14)),
                Text('$service • $duration', style: SanaTextStyles.caption),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
