import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Messaging API service
class MessagingService {
  final ApiClient _client;

  MessagingService(this._client);

  /// Get conversations list
  Future<List<ConversationDto>> getConversations({
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/messaging/conversations',
      queryParameters: {
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => ConversationDto.fromJson(json))
        .toList();
  }

  /// Get messages for a conversation
  Future<List<MessageDto>> getMessages(
    int conversationId, {
    int page = 1,
    int limit = 50,
    DateTime? before,
  }) async {
    final response = await _client.get(
      '/messaging/conversations/$conversationId/messages',
      queryParameters: {
        'page': page,
        'limit': limit,
        if (before != null) 'before': before.toIso8601String(),
      },
    );
    return (response.data as List)
        .map((json) => MessageDto.fromJson(json))
        .toList();
  }

  /// Send a message
  Future<MessageDto> sendMessage(
    int conversationId, {
    required String content,
    String? attachmentUrl,
  }) async {
    final response = await _client.post(
      '/messaging/conversations/$conversationId/messages',
      data: {
        'content': content,
        if (attachmentUrl != null) 'attachment_url': attachmentUrl,
      },
    );
    return MessageDto.fromJson(response.data);
  }

  /// Mark conversation as read
  Future<void> markAsRead(int conversationId) async {
    await _client.post('/messaging/conversations/$conversationId/read');
  }

  /// Get unread count
  Future<int> getUnreadCount() async {
    final response = await _client.get('/messaging/unread-count');
    return response.data['count'] ?? 0;
  }

  /// Start new conversation with practitioner
  Future<ConversationDto> startConversation(int practitionerId) async {
    final response = await _client.post(
      '/messaging/conversations',
      data: {'practitioner_id': practitionerId},
    );
    return ConversationDto.fromJson(response.data);
  }

  /// Delete a message
  Future<void> deleteMessage(int conversationId, int messageId) async {
    await _client.delete(
      '/messaging/conversations/$conversationId/messages/$messageId',
    );
  }
}

/// Conversation DTO
class ConversationDto {
  final int id;
  final int participantId;
  final String participantName;
  final String? participantAvatar;
  final String? lastMessage;
  final DateTime? lastMessageAt;
  final int unreadCount;

  ConversationDto({
    required this.id,
    required this.participantId,
    required this.participantName,
    this.participantAvatar,
    this.lastMessage,
    this.lastMessageAt,
    required this.unreadCount,
  });

  factory ConversationDto.fromJson(Map<String, dynamic> json) {
    return ConversationDto(
      id: json['id'],
      participantId: json['participant_id'],
      participantName: json['participant_name'] ?? '',
      participantAvatar: json['participant_avatar'],
      lastMessage: json['last_message'],
      lastMessageAt: json['last_message_at'] != null
          ? DateTime.parse(json['last_message_at'])
          : null,
      unreadCount: json['unread_count'] ?? 0,
    );
  }
}

/// Message DTO
class MessageDto {
  final int id;
  final int senderId;
  final String content;
  final String? attachmentUrl;
  final bool isRead;
  final DateTime createdAt;

  MessageDto({
    required this.id,
    required this.senderId,
    required this.content,
    this.attachmentUrl,
    required this.isRead,
    required this.createdAt,
  });

  factory MessageDto.fromJson(Map<String, dynamic> json) {
    return MessageDto(
      id: json['id'],
      senderId: json['sender_id'],
      content: json['content'],
      attachmentUrl: json['attachment_url'],
      isRead: json['is_read'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Provider for messaging service
final messagingServiceProvider = Provider<MessagingService>((ref) {
  final client = ref.watch(apiClientProvider);
  return MessagingService(client);
});
