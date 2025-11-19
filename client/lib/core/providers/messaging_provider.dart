import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api/services/messaging_service.dart';

/// Conversations state
class ConversationsState {
  final List<ConversationDto> conversations;
  final bool isLoading;
  final String? error;

  const ConversationsState({
    this.conversations = const [],
    this.isLoading = false,
    this.error,
  });

  ConversationsState copyWith({
    List<ConversationDto>? conversations,
    bool? isLoading,
    String? error,
  }) {
    return ConversationsState(
      conversations: conversations ?? this.conversations,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }

  int get totalUnread =>
      conversations.fold(0, (sum, c) => sum + c.unreadCount);
}

/// Conversations notifier
class ConversationsNotifier extends StateNotifier<ConversationsState> {
  final MessagingService _service;

  ConversationsNotifier(this._service) : super(const ConversationsState());

  /// Load conversations
  Future<void> loadConversations() async {
    state = state.copyWith(isLoading: true, error: null);

    try {
      final conversations = await _service.getConversations();
      state = state.copyWith(
        conversations: conversations,
        isLoading: false,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Start new conversation
  Future<ConversationDto> startConversation(int practitionerId) async {
    final conversation = await _service.startConversation(practitionerId);

    // Check if conversation already exists
    final exists = state.conversations.any((c) => c.id == conversation.id);
    if (!exists) {
      state = state.copyWith(
        conversations: [conversation, ...state.conversations],
      );
    }

    return conversation;
  }

  /// Mark conversation as read
  Future<void> markAsRead(int conversationId) async {
    await _service.markAsRead(conversationId);

    state = state.copyWith(
      conversations: state.conversations.map((c) {
        if (c.id == conversationId) {
          return ConversationDto(
            id: c.id,
            participantId: c.participantId,
            participantName: c.participantName,
            participantAvatar: c.participantAvatar,
            lastMessage: c.lastMessage,
            lastMessageAt: c.lastMessageAt,
            unreadCount: 0,
          );
        }
        return c;
      }).toList(),
    );
  }

  /// Update conversation with new message
  void updateConversation(int conversationId, String message) {
    state = state.copyWith(
      conversations: state.conversations.map((c) {
        if (c.id == conversationId) {
          return ConversationDto(
            id: c.id,
            participantId: c.participantId,
            participantName: c.participantName,
            participantAvatar: c.participantAvatar,
            lastMessage: message,
            lastMessageAt: DateTime.now(),
            unreadCount: c.unreadCount,
          );
        }
        return c;
      }).toList()
        ..sort((a, b) => (b.lastMessageAt ?? DateTime.now())
            .compareTo(a.lastMessageAt ?? DateTime.now())),
    );
  }

  /// Refresh conversations
  Future<void> refresh() async {
    await loadConversations();
  }
}

/// Conversations provider
final conversationsProvider =
    StateNotifierProvider<ConversationsNotifier, ConversationsState>((ref) {
  final service = ref.watch(messagingServiceProvider);
  return ConversationsNotifier(service);
});

/// Messages state
class MessagesState {
  final List<MessageDto> messages;
  final bool isLoading;
  final bool hasMore;
  final String? error;

  const MessagesState({
    this.messages = const [],
    this.isLoading = false,
    this.hasMore = true,
    this.error,
  });

  MessagesState copyWith({
    List<MessageDto>? messages,
    bool? isLoading,
    bool? hasMore,
    String? error,
  }) {
    return MessagesState(
      messages: messages ?? this.messages,
      isLoading: isLoading ?? this.isLoading,
      hasMore: hasMore ?? this.hasMore,
      error: error,
    );
  }
}

/// Messages notifier
class MessagesNotifier extends StateNotifier<MessagesState> {
  final MessagingService _service;
  final int conversationId;

  MessagesNotifier(this._service, this.conversationId)
      : super(const MessagesState());

  /// Load messages
  Future<void> loadMessages({bool loadMore = false}) async {
    if (state.isLoading) return;

    state = state.copyWith(isLoading: true, error: null);

    try {
      final before = loadMore && state.messages.isNotEmpty
          ? state.messages.last.createdAt
          : null;

      final messages = await _service.getMessages(
        conversationId,
        before: before,
      );

      state = state.copyWith(
        messages: loadMore
            ? [...state.messages, ...messages]
            : messages,
        isLoading: false,
        hasMore: messages.length >= 50,
      );
    } catch (e) {
      state = state.copyWith(
        isLoading: false,
        error: e.toString(),
      );
    }
  }

  /// Send message
  Future<void> sendMessage(String content, {String? attachmentUrl}) async {
    final message = await _service.sendMessage(
      conversationId,
      content: content,
      attachmentUrl: attachmentUrl,
    );

    state = state.copyWith(
      messages: [message, ...state.messages],
    );
  }

  /// Delete message
  Future<void> deleteMessage(int messageId) async {
    await _service.deleteMessage(conversationId, messageId);

    state = state.copyWith(
      messages: state.messages.where((m) => m.id != messageId).toList(),
    );
  }

  /// Add message (for real-time updates)
  void addMessage(MessageDto message) {
    state = state.copyWith(
      messages: [message, ...state.messages],
    );
  }
}

/// Messages provider family
final messagesProvider = StateNotifierProvider.family<MessagesNotifier,
    MessagesState, int>((ref, conversationId) {
  final service = ref.watch(messagingServiceProvider);
  return MessagesNotifier(service, conversationId);
});

/// Unread count provider
final unreadCountProvider = FutureProvider<int>((ref) async {
  final service = ref.watch(messagingServiceProvider);
  return service.getUnreadCount();
});

/// Total unread from conversations
final totalUnreadProvider = Provider<int>((ref) {
  return ref.watch(conversationsProvider).totalUnread;
});

/// Selected conversation provider
final selectedConversationProvider = StateProvider<int?>((ref) => null);
