import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class MessagesScreen extends StatelessWidget {
  const MessagesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          children: [
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Messages', style: SanaTextStyles.heading2),
                  const SizedBox(height: SanaSpacing.md),
                  const SanaSearchField(hint: 'Search messages'),
                ],
              ),
            ),
            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                itemCount: 8,
                itemBuilder: (context, index) {
                  return _ConversationItem(
                    name: ['Sarah Johnson', 'Michael Brown', 'Lisa Wang', 'James Kim', 'Anna Smith', 'Robert Davis', 'Jennifer Lee', 'David Park'][index],
                    message: ['Thank you for the great session!', 'When is my next appointment?', 'The exercises are helping', 'Can I reschedule?', 'See you tomorrow!', 'Quick question about...', 'Feeling much better', 'Thanks for the follow-up'][index],
                    time: ['2m', '1h', '3h', 'Yesterday', 'Yesterday', '2 days', '3 days', '1 week'][index],
                    unread: index < 2 ? (index == 0 ? 2 : 1) : 0,
                    onTap: () => context.push('/messages/$index'),
                  );
                },
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _ConversationItem extends StatelessWidget {
  final String name;
  final String message;
  final String time;
  final int unread;
  final VoidCallback onTap;

  const _ConversationItem({required this.name, required this.message, required this.time, required this.unread, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: SanaCard(
        onTap: onTap,
        child: Row(
          children: [
            SanaAvatar(name: name, size: SanaAvatarSize.md),
            const SizedBox(width: SanaSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(name, style: SanaTextStyles.body.copyWith(fontWeight: unread > 0 ? FontWeight.w600 : FontWeight.w500)),
                      Text(time, style: SanaTextStyles.caption),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Expanded(
                        child: Text(message, style: SanaTextStyles.bodySmall, maxLines: 1, overflow: TextOverflow.ellipsis),
                      ),
                      if (unread > 0)
                        Container(
                          margin: const EdgeInsets.only(left: 8),
                          padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                          decoration: BoxDecoration(color: SanaColors.primaryDark, borderRadius: BorderRadius.circular(10)),
                          child: Text('$unread', style: const TextStyle(fontSize: 11, fontWeight: FontWeight.w600, color: SanaColors.white)),
                        ),
                    ],
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }
}
