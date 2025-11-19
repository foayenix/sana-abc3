import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../api_client.dart';

/// Earnings/Payout API service
class EarningsService {
  final ApiClient _client;

  EarningsService(this._client);

  /// Get earnings overview
  Future<EarningsOverview> getOverview({String period = 'month'}) async {
    final response = await _client.get(
      '/practitioners/me/earnings',
      queryParameters: {'period': period},
    );
    return EarningsOverview.fromJson(response.data);
  }

  /// Get transaction history
  Future<List<Transaction>> getTransactions({
    int page = 1,
    int limit = 20,
  }) async {
    final response = await _client.get(
      '/practitioners/me/transactions',
      queryParameters: {
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => Transaction.fromJson(json))
        .toList();
  }

  /// Get payout history
  Future<List<Payout>> getPayouts({int page = 1, int limit = 10}) async {
    final response = await _client.get(
      '/practitioners/me/payouts',
      queryParameters: {
        'page': page,
        'limit': limit,
      },
    );
    return (response.data as List)
        .map((json) => Payout.fromJson(json))
        .toList();
  }

  /// Get payout settings
  Future<PayoutSettings> getPayoutSettings() async {
    final response = await _client.get('/practitioners/me/payout-settings');
    return PayoutSettings.fromJson(response.data);
  }

  /// Update payout settings
  Future<void> updatePayoutSettings({
    String? bankAccountId,
    String? payoutSchedule,
  }) async {
    await _client.patch(
      '/practitioners/me/payout-settings',
      data: {
        if (bankAccountId != null) 'bank_account_id': bankAccountId,
        if (payoutSchedule != null) 'payout_schedule': payoutSchedule,
      },
    );
  }

  /// Request instant payout
  Future<Payout> requestInstantPayout(double amount) async {
    final response = await _client.post(
      '/practitioners/me/payouts/instant',
      data: {'amount': amount},
    );
    return Payout.fromJson(response.data);
  }
}

/// Earnings overview DTO
class EarningsOverview {
  final double totalEarnings;
  final double pendingBalance;
  final double availableBalance;
  final double platformFee;
  final int totalSessions;
  final List<EarningsDataPoint> chartData;

  EarningsOverview({
    required this.totalEarnings,
    required this.pendingBalance,
    required this.availableBalance,
    required this.platformFee,
    required this.totalSessions,
    required this.chartData,
  });

  factory EarningsOverview.fromJson(Map<String, dynamic> json) {
    return EarningsOverview(
      totalEarnings: (json['total_earnings'] ?? 0).toDouble(),
      pendingBalance: (json['pending_balance'] ?? 0).toDouble(),
      availableBalance: (json['available_balance'] ?? 0).toDouble(),
      platformFee: (json['platform_fee'] ?? 0).toDouble(),
      totalSessions: json['total_sessions'] ?? 0,
      chartData: (json['chart_data'] as List? ?? [])
          .map((d) => EarningsDataPoint.fromJson(d))
          .toList(),
    );
  }
}

/// Earnings data point
class EarningsDataPoint {
  final DateTime date;
  final double amount;

  EarningsDataPoint({required this.date, required this.amount});

  factory EarningsDataPoint.fromJson(Map<String, dynamic> json) {
    return EarningsDataPoint(
      date: DateTime.parse(json['date']),
      amount: (json['amount'] ?? 0).toDouble(),
    );
  }
}

/// Transaction DTO
class Transaction {
  final int id;
  final String type;
  final double amount;
  final String description;
  final String status;
  final DateTime createdAt;

  Transaction({
    required this.id,
    required this.type,
    required this.amount,
    required this.description,
    required this.status,
    required this.createdAt,
  });

  factory Transaction.fromJson(Map<String, dynamic> json) {
    return Transaction(
      id: json['id'],
      type: json['type'],
      amount: (json['amount'] ?? 0).toDouble(),
      description: json['description'] ?? '',
      status: json['status'],
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Payout DTO
class Payout {
  final int id;
  final double amount;
  final String status;
  final String? bankLast4;
  final DateTime? paidAt;
  final DateTime createdAt;

  Payout({
    required this.id,
    required this.amount,
    required this.status,
    this.bankLast4,
    this.paidAt,
    required this.createdAt,
  });

  factory Payout.fromJson(Map<String, dynamic> json) {
    return Payout(
      id: json['id'],
      amount: (json['amount'] ?? 0).toDouble(),
      status: json['status'],
      bankLast4: json['bank_last4'],
      paidAt: json['paid_at'] != null
          ? DateTime.parse(json['paid_at'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }
}

/// Payout settings DTO
class PayoutSettings {
  final String? bankAccountId;
  final String? bankLast4;
  final String payoutSchedule;
  final double minimumPayout;

  PayoutSettings({
    this.bankAccountId,
    this.bankLast4,
    required this.payoutSchedule,
    required this.minimumPayout,
  });

  factory PayoutSettings.fromJson(Map<String, dynamic> json) {
    return PayoutSettings(
      bankAccountId: json['bank_account_id'],
      bankLast4: json['bank_last4'],
      payoutSchedule: json['payout_schedule'] ?? 'weekly',
      minimumPayout: (json['minimum_payout'] ?? 50).toDouble(),
    );
  }
}

/// Provider for earnings service
final earningsServiceProvider = Provider<EarningsService>((ref) {
  final client = ref.watch(apiClientProvider);
  return EarningsService(client);
});
