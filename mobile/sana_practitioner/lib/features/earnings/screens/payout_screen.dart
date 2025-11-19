import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_card.dart';
import '../../../shared/widgets/sana_text_field.dart';

class PayoutScreen extends StatelessWidget {
  const PayoutScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Withdraw Funds'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            SanaCard(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text('Available Balance', style: SanaTextStyles.bodySmall),
                  const SizedBox(height: 4),
                  Text('\$2,840.00', style: SanaTextStyles.heading1.copyWith(color: SanaColors.primaryDark)),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.lg),
            Text('Withdraw Amount', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(hint: 'Enter amount', prefixIcon: Icons.attach_money, keyboardType: TextInputType.number),
            const SizedBox(height: SanaSpacing.lg),
            Text('Payout Method', style: SanaTextStyles.heading3),
            const SizedBox(height: SanaSpacing.md),
            SanaCard(
              child: Row(
                children: [
                  Container(
                    width: 48, height: 48,
                    decoration: BoxDecoration(color: SanaColors.grey100, borderRadius: BorderRadius.circular(8)),
                    child: const Icon(Icons.account_balance, color: SanaColors.textSecondary),
                  ),
                  const SizedBox(width: SanaSpacing.md),
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text('Bank Account', style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                        Text('****4567', style: SanaTextStyles.caption),
                      ],
                    ),
                  ),
                  const Icon(Icons.check_circle, color: SanaColors.primaryDark),
                ],
              ),
            ),
            const SizedBox(height: SanaSpacing.xl),
            SanaButton(text: 'Withdraw', onPressed: () => _showSuccess(context)),
          ],
        ),
      ),
    );
  }

  void _showSuccess(BuildContext context) {
    showDialog(
      context: context,
      builder: (_) => AlertDialog(
        title: const Text('Withdrawal Initiated'),
        content: const Text('Your funds will be transferred within 2-3 business days.'),
        actions: [TextButton(onPressed: () { Navigator.pop(context); context.pop(); }, child: const Text('OK'))],
      ),
    );
  }
}
