import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class MessagesScreen extends StatefulWidget {
  const MessagesScreen({super.key});

  @override
  State<MessagesScreen> createState() => _MessagesScreenState();
}

class _MessagesScreenState extends State<MessagesScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Padding(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(
                    'Messages',
                    style: SanaTextStyles.heading2,
                  ),
                  const SizedBox(height: SanaSpacing.md),
                  SanaSearchField(
                    controller: _searchController,
                    hint: 'Search conversations',
                  ),
                ],
              ),
            ),

            Expanded(
              child: ListView.builder(
                padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.lg),
                itemCount: 6,
                itemBuilder: (context, index) {
                  final isUnread = index < 2;
                  return _ConversationItem(
                    name: ['Dr. Emily Chen', 'Dr. Michael Park', 'Dr. Sarah Lee', 'Dr. James Wilson', 'Dr. Lisa Wang', 'Dr. David Kim'][index],
                    lastMessage: [
                      'Thank you for your feedback! I\'ll see you at your next appointment.',
                      'Your lab results look great. Let\'s discuss...',
                      'Remember to do the breathing exercises we discussed.',
                      'How are you feeling after the adjustment?',
                      'I\'ve prepared your herb formula.',
                      'Looking forward to our session tomorrow!'
                    ][index],
                    time: ['2m', '1h', '3h', 'Yesterday', 'Yesterday', '2 days'][index],
                    unreadCount: isUnread ? (index == 0 ? 2 : 1) : 0,
                    isOnline: index % 2 == 0,
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
  final String lastMessage;
  final String time;
  final int unreadCount;
  final bool isOnline;
  final VoidCallback onTap;

  const _ConversationItem({
    required this.name,
    required this.lastMessage,
    required this.time,
    required this.unreadCount,
    required this.isOnline,
    required this.onTap,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: SanaCard(
        onTap: onTap,
        child: Row(
          children: [
            SanaAvatar(
              name: name,
              size: SanaAvatarSize.md,
              isOnline: isOnline,
            ),
            const SizedBox(width: SanaSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Row(
                    mainAxisAlignment: MainAxisAlignment.spaceBetween,
                    children: [
                      Text(
                        name,
                        style: SanaTextStyles.body.copyWith(
                          fontWeight: unreadCount > 0
                              ? FontWeight.w600
                              : FontWeight.w500,
                        ),
                      ),
                      Text(
                        time,
                        style: SanaTextStyles.caption.copyWith(
                          color: unreadCount > 0
                              ? SanaColors.primaryDark
                              : SanaColors.textTertiary,
                        ),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Row(
                    children: [
                      Expanded(
                        child: Text(
                          lastMessage,
                          style: SanaTextStyles.bodySmall.copyWith(
                            color: unreadCount > 0
                                ? SanaColors.textPrimary
                                : SanaColors.textSecondary,
                            fontWeight: unreadCount > 0
                                ? FontWeight.w500
                                : FontWeight.w400,
                          ),
                          maxLines: 1,
                          overflow: TextOverflow.ellipsis,
                        ),
                      ),
                      if (unreadCount > 0) ...[
                        const SizedBox(width: 8),
                        Container(
                          padding: const EdgeInsets.symmetric(
                            horizontal: 8,
                            vertical: 2,
                          ),
                          decoration: BoxDecoration(
                            color: SanaColors.primaryDark,
                            borderRadius: BorderRadius.circular(10),
                          ),
                          child: Text(
                            '$unreadCount',
                            style: const TextStyle(
                              fontSize: 11,
                              fontWeight: FontWeight.w600,
                              color: SanaColors.white,
                            ),
                          ),
                        ),
                      ],
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
