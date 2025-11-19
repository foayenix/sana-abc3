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
  final _controller = TextEditingController();

  @override
  void dispose() {
    _controller.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
        title: Row(
          children: [
            const SanaAvatar(name: 'Sarah Johnson', size: SanaAvatarSize.sm),
            const SizedBox(width: SanaSpacing.sm),
            Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text('Sarah Johnson', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                Text('Online', style: SanaTextStyles.caption.copyWith(color: SanaColors.success)),
              ],
            ),
          ],
        ),
      ),
      body: Column(
        children: [
          Expanded(
            child: ListView(
              padding: const EdgeInsets.all(SanaSpacing.lg),
              children: [
                _Message(text: 'Hi Dr. Chen! Quick question about the exercises.', isMe: false, time: '10:30 AM'),
                _Message(text: 'Of course! What would you like to know?', isMe: true, time: '10:32 AM'),
                _Message(text: 'How often should I do the stretches?', isMe: false, time: '10:33 AM'),
                _Message(text: 'I recommend doing them twice daily - morning and evening. Start with 5 minutes each session and gradually increase.', isMe: true, time: '10:35 AM'),
                _Message(text: 'Thank you for the great session!', isMe: false, time: '10:38 AM'),
              ],
            ),
          ),
          Container(
            padding: const EdgeInsets.all(SanaSpacing.md),
            decoration: BoxDecoration(
              color: SanaColors.surface,
              boxShadow: [BoxShadow(color: SanaColors.black.withOpacity(0.05), blurRadius: 10, offset: const Offset(0, -4))],
            ),
            child: SafeArea(
              child: Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _controller,
                      decoration: InputDecoration(
                        hintText: 'Type a message...',
                        filled: true, fillColor: SanaColors.grey100,
                        border: OutlineInputBorder(borderRadius: BorderRadius.circular(24), borderSide: BorderSide.none),
                      ),
                    ),
                  ),
                  const SizedBox(width: SanaSpacing.sm),
                  Container(
                    decoration: const BoxDecoration(color: SanaColors.primaryDark, shape: BoxShape.circle),
                    child: IconButton(icon: const Icon(Icons.send, size: 20), color: SanaColors.white, onPressed: () {}),
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

class _Message extends StatelessWidget {
  final String text; final bool isMe; final String time;
  const _Message({required this.text, required this.isMe, required this.time});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.md),
      child: Row(
        mainAxisAlignment: isMe ? MainAxisAlignment.end : MainAxisAlignment.start,
        children: [
          Container(
            constraints: BoxConstraints(maxWidth: MediaQuery.of(context).size.width * 0.7),
            padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.md, vertical: SanaSpacing.sm),
            decoration: BoxDecoration(
              color: isMe ? SanaColors.primaryDark : SanaColors.surface,
              borderRadius: BorderRadius.circular(16),
              border: isMe ? null : Border.all(color: SanaColors.grey200),
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(text, style: SanaTextStyles.body.copyWith(color: isMe ? SanaColors.white : SanaColors.textPrimary)),
                const SizedBox(height: 4),
                Text(time, style: TextStyle(fontSize: 10, color: isMe ? SanaColors.white.withOpacity(0.7) : SanaColors.textTertiary)),
              ],
            ),
          ),
        ],
      ),
    );
  }
}
