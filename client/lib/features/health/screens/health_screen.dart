import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/health_provider.dart';
import '../../../shared/widgets/health_score_widget.dart';

class HealthScreen extends ConsumerStatefulWidget {
  const HealthScreen({super.key});

  @override
  ConsumerState<HealthScreen> createState() => _HealthScreenState();
}

class _HealthScreenState extends ConsumerState<HealthScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(healthProvider.notifier).loadHealthData();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(healthProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Health'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add),
            onPressed: () => _showAddEntryDialog(),
          ),
        ],
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : RefreshIndicator(
              onRefresh: () => ref.read(healthProvider.notifier).refresh(),
              child: SingleChildScrollView(
                physics: const AlwaysScrollableScrollPhysics(),
                padding: const EdgeInsets.all(20),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    // Health Score
                    Center(
                      child: HealthScoreWidget(
                        score: state.currentScore?.score ?? 0,
                        size: 150,
                      ),
                    ),
                    const SizedBox(height: 24),

                    // Mood Tracking
                    Text('Today\'s Mood', style: SanaTextStyles.heading3),
                    const SizedBox(height: 12),
                    _MoodSelector(
                      onMoodSelected: (score) async {
                        await ref.read(healthProvider.notifier).logMood(
                          moodScore: score,
                        );
                      },
                    ),
                    const SizedBox(height: 24),

                    // Health Dimensions
                    if (state.dimensions.isNotEmpty) ...[
                      Text('Health Dimensions', style: SanaTextStyles.heading3),
                      const SizedBox(height: 12),
                      ...state.dimensions.entries.map((e) => _DimensionBar(
                        name: e.key,
                        value: e.value,
                      )),
                      const SizedBox(height: 24),
                    ],

                    // Journal Entries
                    Text('Recent Journal', style: SanaTextStyles.heading3),
                    const SizedBox(height: 12),
                    if (state.journalEntries.isEmpty)
                      _EmptyState(
                        icon: Icons.note_alt_outlined,
                        message: 'No journal entries yet',
                        actionLabel: 'Add Entry',
                        onAction: _showAddEntryDialog,
                      )
                    else
                      ...state.journalEntries.take(5).map((entry) => _JournalCard(
                        entry: entry,
                        onDelete: () async {
                          await ref.read(healthProvider.notifier).deleteJournalEntry(entry.id);
                        },
                      )),
                  ],
                ),
              ),
            ),
    );
  }

  void _showAddEntryDialog() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (context) => _AddJournalEntrySheet(
        onSubmit: (type, title, description, severity) async {
          await ref.read(healthProvider.notifier).createJournalEntry(
            entryType: type,
            title: title,
            description: description,
            severity: severity,
          );
          if (mounted) Navigator.pop(context);
        },
      ),
    );
  }
}

class _MoodSelector extends StatelessWidget {
  final Function(int) onMoodSelected;

  const _MoodSelector({required this.onMoodSelected});

  @override
  Widget build(BuildContext context) {
    return Row(
      mainAxisAlignment: MainAxisAlignment.spaceEvenly,
      children: [
        _MoodButton(emoji: '😢', label: 'Bad', score: 2, onTap: onMoodSelected),
        _MoodButton(emoji: '😕', label: 'Meh', score: 4, onTap: onMoodSelected),
        _MoodButton(emoji: '😐', label: 'Okay', score: 6, onTap: onMoodSelected),
        _MoodButton(emoji: '😊', label: 'Good', score: 8, onTap: onMoodSelected),
        _MoodButton(emoji: '😄', label: 'Great', score: 10, onTap: onMoodSelected),
      ],
    );
  }
}

class _MoodButton extends StatelessWidget {
  final String emoji;
  final String label;
  final int score;
  final Function(int) onTap;

  const _MoodButton({
    required this.emoji,
    required this.label,
    required this.score,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () => onTap(score),
      child: Column(
        children: [
          Text(emoji, style: const TextStyle(fontSize: 32)),
          const SizedBox(height: 4),
          Text(label, style: SanaTextStyles.caption),
        ],
      ),
    );
  }
}

class _DimensionBar extends StatelessWidget {
  final String name;
  final double value;

  const _DimensionBar({required this.name, required this.value});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 12),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(_formatName(name), style: SanaTextStyles.body),
              Text('${(value * 100).round()}%', style: SanaTextStyles.bodyBold),
            ],
          ),
          const SizedBox(height: 4),
          LinearProgressIndicator(
            value: value,
            backgroundColor: SanaColors.grey200,
            valueColor: AlwaysStoppedAnimation(SanaColors.getHealthColor((value * 100).round())),
            minHeight: 8,
            borderRadius: BorderRadius.circular(4),
          ),
        ],
      ),
    );
  }

  String _formatName(String name) {
    return name.split('_').map((w) => w[0].toUpperCase() + w.substring(1)).join(' ');
  }
}

class _JournalCard extends StatelessWidget {
  final dynamic entry;
  final VoidCallback onDelete;

  const _JournalCard({required this.entry, required this.onDelete});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(
          entry.entryType == 'symptom' ? Icons.warning_amber : Icons.note,
          color: entry.entryType == 'symptom' ? SanaColors.warning : SanaColors.primaryDark,
        ),
        title: Text(entry.title),
        subtitle: Text(entry.description ?? ''),
        trailing: IconButton(
          icon: const Icon(Icons.delete_outline, size: 20),
          onPressed: onDelete,
        ),
      ),
    );
  }
}

class _EmptyState extends StatelessWidget {
  final IconData icon;
  final String message;
  final String actionLabel;
  final VoidCallback onAction;

  const _EmptyState({
    required this.icon,
    required this.message,
    required this.actionLabel,
    required this.onAction,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(32),
      child: Column(
        children: [
          Icon(icon, size: 48, color: SanaColors.grey400),
          const SizedBox(height: 16),
          Text(message, style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary)),
          const SizedBox(height: 16),
          TextButton(onPressed: onAction, child: Text(actionLabel)),
        ],
      ),
    );
  }
}

class _AddJournalEntrySheet extends StatefulWidget {
  final Function(String, String, String?, int?) onSubmit;

  const _AddJournalEntrySheet({required this.onSubmit});

  @override
  State<_AddJournalEntrySheet> createState() => _AddJournalEntrySheetState();
}

class _AddJournalEntrySheetState extends State<_AddJournalEntrySheet> {
  final _titleController = TextEditingController();
  final _descController = TextEditingController();
  String _type = 'note';
  int _severity = 3;

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: EdgeInsets.only(
        left: 20,
        right: 20,
        top: 20,
        bottom: MediaQuery.of(context).viewInsets.bottom + 20,
      ),
      child: Column(
        mainAxisSize: MainAxisSize.min,
        crossAxisAlignment: CrossAxisAlignment.stretch,
        children: [
          Text('Add Journal Entry', style: SanaTextStyles.heading3),
          const SizedBox(height: 16),
          SegmentedButton<String>(
            segments: const [
              ButtonSegment(value: 'note', label: Text('Note')),
              ButtonSegment(value: 'symptom', label: Text('Symptom')),
            ],
            selected: {_type},
            onSelectionChanged: (s) => setState(() => _type = s.first),
          ),
          const SizedBox(height: 16),
          TextField(
            controller: _titleController,
            decoration: const InputDecoration(labelText: 'Title'),
          ),
          const SizedBox(height: 12),
          TextField(
            controller: _descController,
            decoration: const InputDecoration(labelText: 'Description'),
            maxLines: 3,
          ),
          if (_type == 'symptom') ...[
            const SizedBox(height: 12),
            Text('Severity: $_severity', style: SanaTextStyles.body),
            Slider(
              value: _severity.toDouble(),
              min: 1,
              max: 10,
              divisions: 9,
              onChanged: (v) => setState(() => _severity = v.round()),
            ),
          ],
          const SizedBox(height: 16),
          ElevatedButton(
            onPressed: () {
              if (_titleController.text.isNotEmpty) {
                widget.onSubmit(
                  _type,
                  _titleController.text,
                  _descController.text.isEmpty ? null : _descController.text,
                  _type == 'symptom' ? _severity : null,
                );
              }
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
