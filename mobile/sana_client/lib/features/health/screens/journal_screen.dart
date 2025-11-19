import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class JournalScreen extends StatefulWidget {
  const JournalScreen({super.key});

  @override
  State<JournalScreen> createState() => _JournalScreenState();
}

class _JournalScreenState extends State<JournalScreen> {
  int _moodRating = 3;
  int _energyRating = 3;
  int _painRating = 1;
  final _notesController = TextEditingController();

  @override
  void dispose() {
    _notesController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Daily Check-in'),
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
            Text(
              'How are you feeling today?',
              style: SanaTextStyles.heading2,
            ),
            const SizedBox(height: SanaSpacing.xl),

            // Mood
            _RatingSection(
              title: 'Mood',
              icon: Icons.sentiment_satisfied_alt,
              value: _moodRating,
              labels: const ['Very Bad', 'Bad', 'Okay', 'Good', 'Great'],
              onChanged: (value) => setState(() => _moodRating = value),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Energy
            _RatingSection(
              title: 'Energy Level',
              icon: Icons.bolt,
              value: _energyRating,
              labels: const ['Very Low', 'Low', 'Moderate', 'High', 'Very High'],
              onChanged: (value) => setState(() => _energyRating = value),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Pain
            _RatingSection(
              title: 'Pain Level',
              icon: Icons.favorite,
              value: _painRating,
              labels: const ['None', 'Mild', 'Moderate', 'Severe', 'Extreme'],
              onChanged: (value) => setState(() => _painRating = value),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Symptoms
            Text('Any symptoms?', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            Wrap(
              spacing: SanaSpacing.sm,
              runSpacing: SanaSpacing.sm,
              children: [
                _SymptomChip(label: 'Headache'),
                _SymptomChip(label: 'Fatigue'),
                _SymptomChip(label: 'Anxiety'),
                _SymptomChip(label: 'Insomnia'),
                _SymptomChip(label: 'Nausea'),
                _SymptomChip(label: 'Muscle Pain'),
                _SymptomChip(label: 'Joint Pain'),
                _SymptomChip(label: 'Other'),
              ],
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Notes
            Text('Additional Notes', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            TextField(
              controller: _notesController,
              maxLines: 4,
              decoration: InputDecoration(
                hintText: 'Write about your day, any triggers, or things you noticed...',
                filled: true,
                fillColor: SanaColors.surface,
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(SanaBorderRadius.md),
                  borderSide: const BorderSide(color: SanaColors.grey200),
                ),
              ),
            ),

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
            text: 'Save Entry',
            onPressed: () {
              // TODO: Save journal entry
              context.pop();
            },
          ),
        ),
      ),
    );
  }
}

class _RatingSection extends StatelessWidget {
  final String title;
  final IconData icon;
  final int value;
  final List<String> labels;
  final ValueChanged<int> onChanged;

  const _RatingSection({
    required this.title,
    required this.icon,
    required this.value,
    required this.labels,
    required this.onChanged,
  });

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Icon(icon, color: SanaColors.primaryDark),
              const SizedBox(width: SanaSpacing.sm),
              Text(title, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
            ],
          ),
          const SizedBox(height: SanaSpacing.md),
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: List.generate(5, (index) {
              final isSelected = index == value;
              return GestureDetector(
                onTap: () => onChanged(index),
                child: Container(
                  width: 48,
                  height: 48,
                  decoration: BoxDecoration(
                    color: isSelected ? SanaColors.primaryDark : SanaColors.grey100,
                    borderRadius: BorderRadius.circular(12),
                  ),
                  child: Center(
                    child: Text(
                      '${index + 1}',
                      style: TextStyle(
                        fontSize: 18,
                        fontWeight: FontWeight.w600,
                        color: isSelected ? SanaColors.white : SanaColors.textSecondary,
                      ),
                    ),
                  ),
                ),
              );
            }),
          ),
          const SizedBox(height: SanaSpacing.sm),
          Text(
            labels[value],
            style: SanaTextStyles.bodySmall.copyWith(
              color: SanaColors.primaryDark,
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}

class _SymptomChip extends StatefulWidget {
  final String label;

  const _SymptomChip({required this.label});

  @override
  State<_SymptomChip> createState() => _SymptomChipState();
}

class _SymptomChipState extends State<_SymptomChip> {
  bool _isSelected = false;

  @override
  Widget build(BuildContext context) {
    return FilterChip(
      label: Text(widget.label),
      selected: _isSelected,
      onSelected: (selected) => setState(() => _isSelected = selected),
      selectedColor: SanaColors.primaryLightest,
      checkmarkColor: SanaColors.primaryDark,
    );
  }
}
