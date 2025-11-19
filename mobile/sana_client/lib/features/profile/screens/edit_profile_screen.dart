import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_avatar.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_text_field.dart';

class EditProfileScreen extends StatefulWidget {
  const EditProfileScreen({super.key});

  @override
  State<EditProfileScreen> createState() => _EditProfileScreenState();
}

class _EditProfileScreenState extends State<EditProfileScreen> {
  final _nameController = TextEditingController(text: 'Sarah Johnson');
  final _emailController = TextEditingController(text: 'sarah.johnson@email.com');
  final _phoneController = TextEditingController(text: '+1 (555) 123-4567');
  final _dobController = TextEditingController(text: '01/15/1990');

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _phoneController.dispose();
    _dobController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        title: const Text('Edit Profile'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(SanaSpacing.lg),
        child: Column(
          children: [
            // Avatar
            Stack(
              children: [
                const SanaAvatar(
                  name: 'Sarah Johnson',
                  size: SanaAvatarSize.xxl,
                ),
                Positioned(
                  right: 0,
                  bottom: 0,
                  child: Container(
                    padding: const EdgeInsets.all(8),
                    decoration: BoxDecoration(
                      color: SanaColors.primaryDark,
                      shape: BoxShape.circle,
                      border: Border.all(
                        color: SanaColors.background,
                        width: 3,
                      ),
                    ),
                    child: const Icon(
                      Icons.camera_alt,
                      size: 20,
                      color: SanaColors.white,
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: SanaSpacing.xl),

            // Form
            SanaTextField(
              label: 'Full Name',
              controller: _nameController,
              prefixIcon: Icons.person_outline,
            ),
            const SizedBox(height: SanaSpacing.md),
            SanaTextField(
              label: 'Email',
              controller: _emailController,
              prefixIcon: Icons.email_outlined,
              keyboardType: TextInputType.emailAddress,
            ),
            const SizedBox(height: SanaSpacing.md),
            SanaTextField(
              label: 'Phone',
              controller: _phoneController,
              prefixIcon: Icons.phone_outlined,
              keyboardType: TextInputType.phone,
            ),
            const SizedBox(height: SanaSpacing.md),
            SanaTextField(
              label: 'Date of Birth',
              controller: _dobController,
              prefixIcon: Icons.calendar_today_outlined,
              keyboardType: TextInputType.datetime,
            ),

            const SizedBox(height: SanaSpacing.xxl),
          ],
        ),
      ),
      bottomNavigationBar: Container(
        padding: const EdgeInsets.all(SanaSpacing.lg),
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
          child: SanaButton(
            text: 'Save Changes',
            onPressed: () {
              // TODO: Save profile
              context.pop();
            },
          ),
        ),
      ),
    );
  }
}
