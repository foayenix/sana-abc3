import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/session_provider.dart';
import '../../../shared/widgets/sana_button.dart';

class SessionDetailScreen extends ConsumerWidget {
  final int sessionId;

  const SessionDetailScreen({super.key, required this.sessionId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final sessionAsync = ref.watch(sessionProvider(sessionId));

    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Session Details'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: sessionAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (e, _) => Center(child: Text('Error: $e')),
        data: (session) => SingleChildScrollView(
          padding: const EdgeInsets.all(20),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              // Practitioner info
              Row(
                children: [
                  CircleAvatar(
                    radius: 30,
                    backgroundColor: SanaColors.primaryLightest,
                    backgroundImage: session.practitionerAvatar != null
                        ? NetworkImage(session.practitionerAvatar!)
                        : null,
                    child: session.practitionerAvatar == null
                        ? Text(
                            session.practitionerName[0],
                            style: SanaTextStyles.heading3.copyWith(
                              color: SanaColors.primaryDark,
                            ),
                          )
                        : null,
                  ),
                  const SizedBox(width: 16),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(session.practitionerName, style: SanaTextStyles.heading3),
                        Text(
                          session.serviceName,
                          style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary),
                        ),
                      ],
                    ),
                  ),
                  _StatusBadge(status: session.status),
                ],
              ),
              const SizedBox(height: 24),

              // Session details card
              Container(
                padding: const EdgeInsets.all(16),
                decoration: BoxDecoration(
                  color: SanaColors.surface,
                  borderRadius: BorderRadius.circular(12),
                  border: Border.all(color: SanaColors.grey200),
                ),
                child: Column(
                  children: [
                    _DetailRow(
                      icon: Icons.calendar_today,
                      label: 'Date',
                      value: _formatDate(session.scheduledAt),
                    ),
                    const Divider(height: 24),
                    _DetailRow(
                      icon: Icons.access_time,
                      label: 'Time',
                      value: _formatTime(session.scheduledAt),
                    ),
                    const Divider(height: 24),
                    _DetailRow(
                      icon: Icons.timer,
                      label: 'Duration',
                      value: '${session.durationMinutes} minutes',
                    ),
                    const Divider(height: 24),
                    _DetailRow(
                      icon: Icons.payment,
                      label: 'Price',
                      value: '\$${session.price.toStringAsFixed(2)}',
                    ),
                  ],
                ),
              ),

              if (session.notes != null) ...[
                const SizedBox(height: 24),
                Text('Notes', style: SanaTextStyles.heading3),
                const SizedBox(height: 8),
                Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16),
                  decoration: BoxDecoration(
                    color: SanaColors.surface,
                    borderRadius: BorderRadius.circular(12),
                    border: Border.all(color: SanaColors.grey200),
                  ),
                  child: Text(session.notes!, style: SanaTextStyles.body),
                ),
              ],

              const SizedBox(height: 32),

              // Actions based on status
              if (session.status == 'scheduled' && session.isUpcoming) ...[
                if (session.meetingLink != null)
                  SanaButton(
                    text: 'Join Session',
                    icon: Icons.video_call,
                    onPressed: () async {
                      final url = Uri.parse(session.meetingLink!);
                      if (await canLaunchUrl(url)) {
                        await launchUrl(url);
                      }
                    },
                  ),
                const SizedBox(height: 12),
                Row(
                  children: [
                    Expanded(
                      child: SanaButton(
                        text: 'Reschedule',
                        variant: SanaButtonVariant.outline,
                        onPressed: () {
                          // TODO: Implement reschedule
                        },
                      ),
                    ),
                    const SizedBox(width: 12),
                    Expanded(
                      child: SanaButton(
                        text: 'Cancel',
                        variant: SanaButtonVariant.outline,
                        onPressed: () => _showCancelDialog(context, ref),
                      ),
                    ),
                  ],
                ),
              ],

              if (session.status == 'completed') ...[
                SanaButton(
                  text: 'Leave Review',
                  onPressed: () => _showReviewDialog(context, ref),
                ),
                const SizedBox(height: 12),
                SanaButton(
                  text: 'Book Again',
                  variant: SanaButtonVariant.outline,
                  onPressed: () => context.push('/booking/${session.practitionerId}'),
                ),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _formatDate(DateTime dt) {
    final months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
    return '${months[dt.month - 1]} ${dt.day}, ${dt.year}';
  }

  String _formatTime(DateTime dt) {
    final hour = dt.hour > 12 ? dt.hour - 12 : (dt.hour == 0 ? 12 : dt.hour);
    final period = dt.hour >= 12 ? 'PM' : 'AM';
    return '$hour:${dt.minute.toString().padLeft(2, '0')} $period';
  }

  void _showCancelDialog(BuildContext context, WidgetRef ref) {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Cancel Session'),
        content: const Text('Are you sure you want to cancel this session?'),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('No'),
          ),
          ElevatedButton(
            onPressed: () async {
              Navigator.pop(context);
              await ref.read(sessionsProvider.notifier).cancelSession(sessionId);
              if (context.mounted) context.pop();
            },
            child: const Text('Yes, Cancel'),
          ),
        ],
      ),
    );
  }

  void _showReviewDialog(BuildContext context, WidgetRef ref) {
    int rating = 5;
    final commentController = TextEditingController();

    showDialog(
      context: context,
      builder: (context) => StatefulBuilder(
        builder: (context, setState) => AlertDialog(
          title: const Text('Leave Review'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.center,
                children: List.generate(5, (index) => IconButton(
                  icon: Icon(
                    index < rating ? Icons.star : Icons.star_border,
                    color: SanaColors.accent,
                  ),
                  onPressed: () => setState(() => rating = index + 1),
                )),
              ),
              const SizedBox(height: 16),
              TextField(
                controller: commentController,
                decoration: const InputDecoration(
                  labelText: 'Comment (optional)',
                ),
                maxLines: 3,
              ),
            ],
          ),
          actions: [
            TextButton(
              onPressed: () => Navigator.pop(context),
              child: const Text('Cancel'),
            ),
            ElevatedButton(
              onPressed: () async {
                Navigator.pop(context);
                await ref.read(sessionsProvider.notifier).submitReview(
                  sessionId,
                  rating: rating,
                  comment: commentController.text.isEmpty ? null : commentController.text,
                );
              },
              child: const Text('Submit'),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;

  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    Color color;
    Color bgColor;

    switch (status) {
      case 'scheduled':
        color = SanaColors.info;
        bgColor = SanaColors.infoLight;
        break;
      case 'completed':
        color = SanaColors.success;
        bgColor = SanaColors.successLight;
        break;
      case 'cancelled':
        color = SanaColors.error;
        bgColor = SanaColors.errorLight;
        break;
      default:
        color = SanaColors.grey600;
        bgColor = SanaColors.grey100;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: bgColor,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Text(
        status[0].toUpperCase() + status.substring(1),
        style: SanaTextStyles.bodySmall.copyWith(color: color),
      ),
    );
  }
}

class _DetailRow extends StatelessWidget {
  final IconData icon;
  final String label;
  final String value;

  const _DetailRow({
    required this.icon,
    required this.label,
    required this.value,
  });

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Icon(icon, size: 20, color: SanaColors.textSecondary),
        const SizedBox(width: 12),
        Text(label, style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary)),
        const Spacer(),
        Text(value, style: SanaTextStyles.bodyBold),
      ],
    );
  }
}
