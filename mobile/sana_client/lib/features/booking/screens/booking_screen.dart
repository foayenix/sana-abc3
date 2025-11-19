import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class BookingScreen extends StatefulWidget {
  final String practitionerId;

  const BookingScreen({
    super.key,
    required this.practitionerId,
  });

  @override
  State<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends State<BookingScreen> {
  DateTime _focusedDay = DateTime.now();
  DateTime? _selectedDay;
  String? _selectedTime;
  String? _selectedService;

  final List<String> _services = [
    'Initial Consultation - \$150',
    'Follow-up Session - \$100',
    'Cupping Therapy - \$80',
  ];

  final List<String> _availableTimes = [
    '9:00 AM',
    '10:00 AM',
    '11:00 AM',
    '2:00 PM',
    '3:00 PM',
    '4:00 PM',
  ];

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Book Appointment'),
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
            // Service Selection
            Text('Select Service', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            ...List.generate(_services.length, (index) {
              final service = _services[index];
              final isSelected = _selectedService == service;
              return Padding(
                padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
                child: GestureDetector(
                  onTap: () => setState(() => _selectedService = service),
                  child: Container(
                    padding: const EdgeInsets.all(SanaSpacing.md),
                    decoration: BoxDecoration(
                      color: isSelected ? SanaColors.primaryLightest : SanaColors.surface,
                      borderRadius: BorderRadius.circular(SanaBorderRadius.md),
                      border: Border.all(
                        color: isSelected ? SanaColors.primaryDark : SanaColors.grey200,
                        width: isSelected ? 2 : 1,
                      ),
                    ),
                    child: Row(
                      children: [
                        Icon(
                          isSelected ? Icons.check_circle : Icons.circle_outlined,
                          color: isSelected ? SanaColors.primaryDark : SanaColors.grey400,
                        ),
                        const SizedBox(width: SanaSpacing.md),
                        Text(
                          service,
                          style: SanaTextStyles.body.copyWith(
                            fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                          ),
                        ),
                      ],
                    ),
                  ),
                ),
              );
            }),

            const SizedBox(height: SanaSpacing.lg),

            // Calendar
            Text('Select Date', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              padding: const EdgeInsets.all(SanaSpacing.sm),
              child: TableCalendar(
                firstDay: DateTime.now(),
                lastDay: DateTime.now().add(const Duration(days: 90)),
                focusedDay: _focusedDay,
                calendarFormat: CalendarFormat.month,
                selectedDayPredicate: (day) => isSameDay(_selectedDay, day),
                onDaySelected: (selectedDay, focusedDay) {
                  setState(() {
                    _selectedDay = selectedDay;
                    _focusedDay = focusedDay;
                    _selectedTime = null;
                  });
                },
                onPageChanged: (focusedDay) {
                  _focusedDay = focusedDay;
                },
                calendarStyle: CalendarStyle(
                  outsideDaysVisible: false,
                  selectedDecoration: const BoxDecoration(
                    color: SanaColors.primaryDark,
                    shape: BoxShape.circle,
                  ),
                  todayDecoration: BoxDecoration(
                    color: SanaColors.primaryLight.withOpacity(0.5),
                    shape: BoxShape.circle,
                  ),
                  weekendTextStyle: const TextStyle(color: SanaColors.textSecondary),
                ),
                headerStyle: HeaderStyle(
                  formatButtonVisible: false,
                  titleCentered: true,
                  titleTextStyle: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
                ),
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Time Selection
            if (_selectedDay != null) ...[
              Text('Select Time', style: SanaTextStyles.heading3),
              const SizedBox(height: SanaSpacing.md),
              Wrap(
                spacing: SanaSpacing.sm,
                runSpacing: SanaSpacing.sm,
                children: _availableTimes.map((time) {
                  final isSelected = _selectedTime == time;
                  return GestureDetector(
                    onTap: () => setState(() => _selectedTime = time),
                    child: Container(
                      padding: const EdgeInsets.symmetric(
                        horizontal: SanaSpacing.md,
                        vertical: SanaSpacing.sm,
                      ),
                      decoration: BoxDecoration(
                        color: isSelected ? SanaColors.primaryDark : SanaColors.surface,
                        borderRadius: BorderRadius.circular(SanaBorderRadius.sm),
                        border: Border.all(
                          color: isSelected ? SanaColors.primaryDark : SanaColors.grey200,
                        ),
                      ),
                      child: Text(
                        time,
                        style: SanaTextStyles.body.copyWith(
                          color: isSelected ? SanaColors.white : SanaColors.textPrimary,
                          fontWeight: isSelected ? FontWeight.w600 : FontWeight.w400,
                        ),
                      ),
                    ),
                  );
                }).toList(),
              ),
            ],

            const SizedBox(height: SanaSpacing.xxl),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        decoration: BoxDecoration(
          color: SanaColors.surface,
          boxShadow: [
            BoxShadow(
              color: SanaColors.black.withOpacity(0.05),
              blurRadius: 10,
              offset: const Offset(0, -4),
            ),
          ],
        ),
        child: SafeArea(
          child: SanaButton(
            text: 'Confirm Booking',
            onPressed: _canBook ? () => context.push(AppRoutes.bookingConfirmation) : null,
          ),
        ),
      ),
    );
  }

  bool get _canBook =>
      _selectedService != null && _selectedDay != null && _selectedTime != null;
}
