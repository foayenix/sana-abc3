import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_card.dart';

class SessionsScreen extends StatelessWidget {
  const SessionsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('All Sessions'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: ListView.builder(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        itemCount: 15,
        itemBuilder: (context, index) => Padding(
          padding: const EdgeInsets.only(bottom: SanaSpacing.sm),
          child: SanaCard(
            onTap: () => context.push('/sessions/$index'),
            child: Row(
              children: [
                SanaAvatar(name: ['Sarah J.', 'Michael B.', 'Lisa W.'][index % 3], size: SanaAvatarSize.md),
                const SizedBox(width: SanaSpacing.md),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(['Sarah Johnson', 'Michael Brown', 'Lisa Wang'][index % 3], style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
                      Text(['Acupuncture', 'Follow-up', 'Consultation'][index % 3], style: SanaTextStyles.caption),
                    ],
                  ),
                ),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.end,
                  children: [
                    Text('Nov ${22 - index}', style: SanaTextStyles.bodySmall),
                    Text('${['9:00', '11:00', '2:00'][index % 3]} ${index % 2 == 0 ? 'AM' : 'PM'}', style: SanaTextStyles.caption),
                  ],
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
