import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';

class ChatScreen extends StatefulWidget {
  final String conversationId;

  const ChatScreen({super.key, required this.conversationId});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final _messageController = TextEditingController();
  final _scrollController = ScrollController();

  final List<_ChatMessage> _messages = [
    _ChatMessage(
      text: 'Hi Dr. Chen, I wanted to follow up about my last session.',
      isMe: true,
      time: '10:30 AM',
    ),
    _ChatMessage(
      text: 'Hello! How are you feeling after our session?',
      isMe: false,
      time: '10:32 AM',
    ),
    _ChatMessage(
      text: 'Much better! The back pain has reduced significantly.',
      isMe: true,
      time: '10:35 AM',
    ),
    _ChatMessage(
      text: 'That\'s wonderful to hear! Remember to continue with the stretching exercises I recommended.',
      isMe: false,
      time: '10:36 AM',
    ),
    _ChatMessage(
      text: 'Will do! Thank you for the great care.',
      isMe: true,
      time: '10:38 AM',
    ),
    _ChatMessage(
      text: 'You\'re welcome! See you at your next appointment. Don\'t hesitate to reach out if you have any questions.',
      isMe: false,
      time: '10:40 AM',
    ),
  ];

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  void _sendMessage() {
    if (_messageController.text.trim().isEmpty) return;
    setState(() {
      _messages.add(_ChatMessage(
        text: _messageController.text.trim(),
        isMe: true,
        time: 'Now',
      ));
      _messageController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
        title: Row(
          children: [
            const SanaAvatar(
              name: 'Dr. Emily Chen',
              size: SanaAvatarSize.sm,
              isOnline: true,
            ),
            const SizedBox(width: SanaSpacing.sm),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  'Dr. Emily Chen',
                  style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600),
                ),
                Text(
                  'Online',
                  style: SanaTextStyles.caption.copyWith(
                    color: SanaColors.success,
                  ),
                ),
              ],
            ),
          ],
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.videocam_outlined),
            onPressed: () {},
          ),
          IconButton(
            icon: const Icon(Icons.more_vert),
            onPressed: () {},
          ),
        ],
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView.builder(
              controller: _scrollController,
              padding: const EdgeInsets.all(SanaSpacing.lg),
              itemCount: _messages.length,
              itemBuilder: (context, index) {
                final message = _messages[index];
                return _MessageBubble(message: message);
              },
            ),
          ),
          Container(
            padding: const EdgeInsets.all(SanaSpacing.md),
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
              child: Row(
                children: [
                  IconButton(
                    icon: const Icon(Icons.attach_file),
                    color: SanaColors.textSecondary,
                    onPressed: () {},
                  ),
                  Expanded(
                    child: TextField(
                      controller: _messageController,
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        filled: true,
                        fillColor: SanaColors.grey100,
                        contentPadding: const EdgeInsets.symmetric(
                          horizontal: 16,
                          vertical: 10,
                        ),
                        border: OutlineInputBorder(
                          borderRadius: BorderRadius.circular(24),
                          borderSide: BorderSide.none,
                        ),
                      ),
                      onSubmitted: (_) => _sendMessage(),
                    ),
                  ),
                  const SizedBox(width: SanaSpacing.sm),
                  Container(
                    decoration: const BoxDecoration(
                      color: SanaColors.primaryDark,
                      shape: BoxShape.circle,
                    ),
                    child: IconButton(
                      icon: const Icon(Icons.send, size: 20),
                      color: SanaColors.white,
                      onPressed: _sendMessage,
                    ),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _ChatMessage {
  final String text;
  final bool isMe;
  final String time;

  _ChatMessage({
    required this.text,
    required this.isMe,
    required this.time,
  });
}

class _MessageBubble extends StatelessWidget {
  final _ChatMessage message;

  const _MessageBubble({required this.message});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.md),
      child: Row(
        mainAxisAlignment:
            message.isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(
              maxWidth: MediaQuery.of(context).size.width * 0.7,
            ),
            padding: const EdgeInsets.symmetric(
              horizontal: SanaSpacing.md,
              vertical: SanaSpacing.sm,
            ),
            decoration: BoxDecoration(
              color: message.isMe
                  ? SanaColors.primaryDark
                  : SanaColors.surface,
              borderRadius: BorderRadius.circular(16).copyWith(
                bottomRight: message.isMe ? const Radius.circular(4) : null,
                bottomLeft: !message.isMe ? const Radius.circular(4) : null,
              ),
              border: message.isMe
                  ? null
                  : Border.all(color: SanaColors.grey200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  message.text,
                  style: SanaTextStyles.body.copyWith(
                    color: message.isMe
                        ? SanaColors.white
                        : SanaColors.textPrimary,
                  ),
                ),
                const SizedBox(height: 4),
                Text(
                  message.time,
                  style: SanaTextStyles.caption.copyWith(
                    fontSize: 10,
                    color: message.isMe
                        ? SanaColors.white.withOpacity(0.7)
                        : SanaColors.textTertiary,
                  ),
                ),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
