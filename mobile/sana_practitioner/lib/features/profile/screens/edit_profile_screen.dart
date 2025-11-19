import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_text_field.dart';

class EditProfileScreen extends StatelessWidget {
  const EditProfileScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Edit Profile'),
        leading: IconButton(icon: const Icon(Icons.arrow_back), onPressed: () => context.pop()),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          children: [
            Stack(
              children: [
                const SanaAvatar(name: 'Dr. Emily Chen', size: SanaAvatarSize.xxl),
                Positioned(
                  right: 0, bottom: 0,
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: SanaColors.primaryDark, shape: BoxShape.circle,
                      border: Border.all(color: SanaColors.background, width: 3),
                    ),
                    child: const Icon(Icons.camera_alt, size: 20, color: SanaColors.white),
                  ),
                ),
              ],
            ),
            const SizedBox(height: SanaSpacing.xl),
            const SanaTextField(label: 'Full Name', hint: 'Dr. Emily Chen', prefixIcon: Icons.person_outline),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Email', hint: 'emily.chen@email.com', prefixIcon: Icons.email_outlined),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Phone', hint: '+1 (555) 123-4567', prefixIcon: Icons.phone_outlined),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'License Number', hint: 'AC-12345', prefixIcon: Icons.verified_outlined),
            const SizedBox(height: SanaSpacing.md),
            const SanaTextField(label: 'Bio', hint: 'Tell clients about yourself...', maxLines: 4),
            const SizedBox(height: SanaSpacing.xl),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: SafeArea(child: SanaButton(text: 'Save Changes', onPressed: () => context.pop())),
      ),
    );
  }
}
