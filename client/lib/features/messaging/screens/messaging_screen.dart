import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../core/providers/messaging_provider.dart';

class MessagingScreen extends ConsumerStatefulWidget {
  const MessagingScreen({super.key});

  @override
  ConsumerState<MessagingScreen> createState() => _MessagingScreenState();
}

class _MessagingScreenState extends ConsumerState<MessagingScreen> {
  @override
  void initState() {
    super.initState();
    Future.microtask(() {
      ref.read(conversationsProvider.notifier).loadConversations();
    });
  }

  @override
  Widget build(BuildContext context) {
    final state = ref.watch(conversationsProvider);

    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Messages'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: state.isLoading
          ? const Center(child: CircularProgressIndicator())
          : state.conversations.isEmpty
              ? Center(
                  child: Column(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      Icon(Icons.message_outlined, size: 64, color: SanaColors.grey400),
                      const SizedBox(height: 16),
                      Text(
                        'No conversations yet',
                        style: SanaTextStyles.body.copyWith(color: SanaColors.textSecondary),
                      ),
                      const SizedBox(height: 8),
                      Text(
                        'Start by booking a session',
                        style: SanaTextStyles.bodySmall.copyWith(color: SanaColors.textTertiary),
                      ),
                    ],
                  ),
                )
              : RefreshIndicator(
                  onRefresh: () => ref.read(conversationsProvider.notifier).refresh(),
                  child: ListView.builder(
                    itemCount: state.conversations.length,
                    itemBuilder: (context, index) {
                      final conversation = state.conversations[index];
                      return _ConversationTile(
                        conversation: conversation,
                        onTap: () {
                          ref.read(conversationsProvider.notifier).markAsRead(conversation.id);
                          context.push('/chat/${conversation.id}');
                        },
                      );
                    },
                  ),
                ),
    );
  }
}

class _ConversationTile extends StatelessWidget {
  final dynamic conversation;
  final VoidCallback onTap;

  const _ConversationTile({required this.conversation, required this.onTap});

  @override
  Widget build(BuildContext context) {
    return ListTile(
      onTap: onTap,
      leading: CircleAvatar(
        backgroundColor: SanaColors.primaryLightest,
        backgroundImage: conversation.participantAvatar != null
            ? NetworkImage(conversation.participantAvatar)
            : null,
        child: conversation.participantAvatar == null
            ? Text(
                conversation.participantName[0],
                style: SanaTextStyles.body.copyWith(color: SanaColors.primaryDark),
              )
            : null,
      ),
      title: Row(
        children: [
          Expanded(
            child: Text(
              conversation.participantName,
              style: conversation.unreadCount > 0
                  ? SanaTextStyles.bodyBold
                  : SanaTextStyles.body,
            ),
          ),
          if (conversation.lastMessageAt != null)
            Text(
              _formatTime(conversation.lastMessageAt),
              style: SanaTextStyles.caption,
            ),
        ],
      ),
      subtitle: Row(
        children: [
          Expanded(
            child: Text(
              conversation.lastMessage ?? 'No messages yet',
              style: SanaTextStyles.bodySmall.copyWith(
                color: SanaColors.textSecondary,
              ),
              maxLines: 1,
              overflow: TextOverflow.ellipsis,
            ),
          ),
          if (conversation.unreadCount > 0)
            Container(
              padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
              decoration: BoxDecoration(
                color: SanaColors.primaryDark,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Text(
                conversation.unreadCount.toString(),
                style: SanaTextStyles.caption.copyWith(color: SanaColors.white),
              ),
            ),
        ],
      ),
    );
  }

  String _formatTime(DateTime dt) {
    final now = DateTime.now();
    final diff = now.difference(dt);
    if (diff.inDays > 0) return '${diff.inDays}d';
    if (diff.inHours > 0) return '${diff.inHours}h';
    if (diff.inMinutes > 0) return '${diff.inMinutes}m';
    return 'now';
  }
}
