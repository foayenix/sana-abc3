import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_card.dart';

class ServicesScreen extends StatelessWidget {
  const ServicesScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Services & Pricing'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        children: [
          _ServiceItem(name: 'Initial Consultation', duration: '90 min', price: '\$150', description: 'Comprehensive assessment'),
          _ServiceItem(name: 'Follow-up Session', duration: '60 min', price: '\$100', description: 'Regular treatment'),
          _ServiceItem(name: 'Cupping Therapy', duration: '45 min', price: '\$80', description: 'Add-on service'),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () {},
        backgroundColor: SanaColors.primaryDark,
        child: const Icon(Icons.add, color: SanaColors.white),
      ),
    );
  }
}

class _ServiceItem extends StatelessWidget {
  final String name, duration, price, description;
  const _ServiceItem({required this.name, required this.duration, required this.price, required this.description});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
      child: SanaCard(
        child: Row(
          children: [
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(name, style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                  const SizedBox(height: 4),
                  Text(description, style: SanaTextStyles.caption),
                  const SizedBox(height: 4),
                  Text(duration, style: SanaTextStyles.bodySmall),
                ],
              ),
            ),
            Text(price, style: SanaTextStyles.heading3.copyWith(color: SanaColors.primaryDark)),
          ],
        ),
      ),
    );
  }
}
