import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:table_calendar/table_calendar.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/practitioner_provider.dart';
import '../../../core/providers/session_provider.dart';
import '../../../shared/widgets/sana_button.dart';

class BookingScreen extends ConsumerStatefulWidget {
  final int practitionerId;

  const BookingScreen({super.key, required this.practitionerId});

  @override
  ConsumerState<BookingScreen> createState() => _BookingScreenState();
}

class _BookingScreenState extends ConsumerState<BookingScreen> {
  int _currentStep = 0;
  int? _selectedServiceId;
  DateTime _selectedDate = DateTime.now().add(const Duration(days: 1));
  String? _selectedTime;
  final _notesController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  Future<void> _handleBooking() async {
    if (_selectedServiceId == null || _selectedTime == null) return;

    setState(() => _isLoading = true);

    try {
      final timeParts = _selectedTime!.split(':');
      final scheduledAt = DateTime(
        _selectedDate.year,
        _selectedDate.month,
        _selectedDate.day,
        int.parse(timeParts[0]),
        int.parse(timeParts[1]),
      );

      await ref.read(sessionsProvider.notifier).createBooking(
        practitionerId: widget.practitionerId,
        serviceId: _selectedServiceId!,
        scheduledAt: scheduledAt,
        notes: _notesController.text.isEmpty ? null : _notesController.text,
      );

      if (mounted) {
        _showSuccessDialog();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(e.toString())),
        );
      }
    } finally {
      if (mounted) setState(() => _isLoading = false);
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      barrierDismissible: false,
      builder: (context) => AlertDialog(
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            Container(
              width: 64,
              height: 64,
              decoration: BoxDecoration(
                color: SanaColors.successLight,
                borderRadius: BorderRadius.circular(32),
              ),
              child: const Icon(Icons.check, size: 32, color: SanaColors.success),
            ),
            const SizedBox(height: 16),
            Text('Booking Confirmed!', style: SanaTextStyles.heading3),
            const SizedBox(height: 8),
            Text(
              'Your session has been booked successfully.',
              style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary),
              textAlign: TextAlign.center,
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.go('/sessions');
            },
            child: const Text('View Sessions'),
          ),
          ElevatedButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
            },
            child: const Text('Done'),
          ),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final servicesAsync = ref.watch(practitionerServicesProvider(widget.practitionerId));
    final availabilityParams = (id: widget.practitionerId, date: _selectedDate);
    final availabilityAsync = ref.watch(practitionerAvailabilityProvider(availabilityParams));

    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Book Session'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: Stepper(
        currentStep: _currentStep,
        onStepContinue: () {
          if (_currentStep < 3) {
            setState(() => _currentStep++);
          } else {
            _handleBooking();
          }
        },
        onStepCancel: () {
          if (_currentStep > 0) {
            setState(() => _currentStep--);
          }
        },
        controlsBuilder: (context, details) {
          return Padding(
            padding: const EdgeInsets.only(top: 16),
            child: Row(
              children: [
                if (_currentStep > 0)
                  TextButton(
                    onPressed: details.onStepCancel,
                    child: const Text('Back'),
                  ),
                const Spacer(),
                SanaButton(
                  text: _currentStep == 3 ? 'Confirm Booking' : 'Continue',
                  onPressed: _canContinue() ? details.onStepContinue : null,
                  isLoading: _isLoading,
                  width: 150,
                ),
              ],
            ),
          );
        },
        steps: [
          // Step 1: Select Service
          Step(
            title: const Text('Select Service'),
            isActive: _currentStep >= 0,
            state: _currentStep > 0 ? StepState.complete : StepState.indexed,
            content: servicesAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
              data: (services) => Column(
                children: services.map((service) => RadioListTile<int>(
                  title: Text(service.name, style: SanaTextStyles.bodyBold),
                  subtitle: Text('${service.durationMinutes} min - \$${service.price.round()}'),
                  value: service.id,
                  groupValue: _selectedServiceId,
                  onChanged: (value) => setState(() => _selectedServiceId = value),
                  activeColor: SanaColors.primaryDark,
                )).toList(),
              ),
            ),
          ),

          // Step 2: Select Date
          Step(
            title: const Text('Select Date'),
            isActive: _currentStep >= 1,
            state: _currentStep > 1 ? StepState.complete : StepState.indexed,
            content: TableCalendar(
              firstDay: DateTime.now(),
              lastDay: DateTime.now().add(const Duration(days: 60)),
              focusedDay: _selectedDate,
              selectedDayPredicate: (day) => isSameDay(_selectedDate, day),
              onDaySelected: (selectedDay, focusedDay) {
                setState(() => _selectedDate = selectedDay);
              },
              calendarStyle: CalendarStyle(
                selectedDecoration: const BoxDecoration(
                  color: SanaColors.primaryDark,
                  shape: BoxShape.circle,
                ),
                todayDecoration: BoxDecoration(
                  color: SanaColors.primaryLightest,
                  shape: BoxShape.circle,
                ),
              ),
              headerStyle: const HeaderStyle(
                formatButtonVisible: false,
                titleCentered: true,
              ),
            ),
          ),

          // Step 3: Select Time
          Step(
            title: const Text('Select Time'),
            isActive: _currentStep >= 2,
            state: _currentStep > 2 ? StepState.complete : StepState.indexed,
            content: availabilityAsync.when(
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (e, _) => Text('Error: $e'),
              data: (slots) => Wrap(
                spacing: 8,
                runSpacing: 8,
                children: slots.where((s) => s.isAvailable).map((slot) => ChoiceChip(
                  label: Text(slot.time),
                  selected: _selectedTime == slot.time,
                  onSelected: (selected) {
                    setState(() => _selectedTime = selected ? slot.time : null);
                  },
                  selectedColor: SanaColors.primaryLightest,
                )).toList(),
              ),
            ),
          ),

          // Step 4: Confirm
          Step(
            title: const Text('Confirm'),
            isActive: _currentStep >= 3,
            state: StepState.indexed,
            content: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Notes (optional)', style: SanaTextStyles.body),
                const SizedBox(height: 8),
                TextField(
                  controller: _notesController,
                  decoration: const InputDecoration(
                    hintText: 'Any notes for the practitioner...',
                  ),
                  maxLines: 3,
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }

  bool _canContinue() {
    switch (_currentStep) {
      case 0:
        return _selectedServiceId != null;
      case 1:
        return true;
      case 2:
        return _selectedTime != null;
      case 3:
        return true;
      default:
        return false;
    }
  }
}
