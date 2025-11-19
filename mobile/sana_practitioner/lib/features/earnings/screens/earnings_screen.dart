import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';

class EarningsScreen extends StatelessWidget {
  const EarningsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Earnings'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Balance Card
            SanaGradientCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  const Text('Available Balance', style: TextStyle(fontSize: 14, color: SanaColors.white)),
                  const SizedBox(height: 8),
                  const Text('\$2,840.00', style: TextStyle(fontSize: 36, fontWeight: FontWeight.w700, color: SanaColors.white)),
                  const SizedBox(height: SanaSpacing.md),
                  SanaButton(
                    text: 'Withdraw',
                    variant: SanaButtonVariant.accent,
                    onPressed: () => context.push(AppRoutes.payout),
                    isFullWidth: false,
                    size: SanaButtonSize.small,
                  ),
                ],
              ),
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Stats
            Row(
              children: [
                Expanded(child: _StatCard(label: 'This Month', value: '\$4,280')),
                const SizedBox(width: SanaSpacing.sm),
                Expanded(child: _StatCard(label: 'Pending', value: '\$1,440')),
              ],
            ),

            const SizedBox(height: SanaSpacing.lg),

            // Recent Transactions
            Text('Recent Transactions', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),

            _TransactionItem(
              title: 'Session with Sarah J.',
              date: 'Nov 22, 2024',
              amount: '\$100',
              status: 'Completed',
              isCredit: true,
            ),
            _TransactionItem(
              title: 'Withdrawal to Bank',
              date: 'Nov 20, 2024',
              amount: '-\$1,500',
              status: 'Processed',
              isCredit: false,
            ),
            _TransactionItem(
              title: 'Session with Michael B.',
              date: 'Nov 19, 2024',
              amount: '\$100',
              status: 'Completed',
              isCredit: true,
            ),
            _TransactionItem(
              title: 'Session with Lisa W.',
              date: 'Nov 18, 2024',
              amount: '\$150',
              status: 'Completed',
              isCredit: true,
            ),
            _TransactionItem(
              title: 'Session with James K.',
              date: 'Nov 17, 2024',
              amount: '\$80',
              status: 'Completed',
              isCredit: true,
            ),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;

  const _StatCard({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return SanaCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(label, style: SanaTextStyles.caption),
          const SizedBox(height: 4),
          Text(value, style: SanaTextStyles.heading3),
        ],
      ),
    );
  }
}

class _TransactionItem extends StatelessWidget {
  final String title;
  final String date;
  final String amount;
  final String status;
  final bool isCredit;

  const _TransactionItem({
    required this.title,
    required this.date,
    required this.amount,
    required this.status,
    required this.isCredit,
  });

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: SanaCard(
        child: Row(
          children: [
            Container(
              width: 40,
              height: 40,
              decoration: BoxDecoration(
                color: isCredit ? SanaColors.successLight : SanaColors.grey100,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(
                isCredit ? Icons.arrow_downward : Icons.arrow_upward,
                color: isCredit ? SanaColors.success : SanaColors.textSecondary,
                size: 20,
              ),
            ),
            const SizedBox(width: SanaSpacing.md),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(title, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w500)),
                  Text(date, style: SanaTextStyles.caption),
                ],
              ),
            ),
            Column(
              crossAxisAlignment: CrossAxisAlignment.end,
              children: [
                Text(
                  amount,
                  style: SanaTextStyles.body.copyWith(
                    fontWeight: FontWeight.w600,
                    color: isCredit ? SanaColors.success : SanaColors.textPrimary,
                  ),
                ),
                Text(status, style: SanaTextStyles.caption),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
