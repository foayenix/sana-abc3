import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_text_field.dart';

class ForgotPasswordScreen extends StatefulWidget {
  const ForgotPasswordScreen({super.key});

  @override
  State<ForgotPasswordScreen> createState() => _ForgotPasswordScreenState();
}

class _ForgotPasswordScreenState extends State<ForgotPasswordScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  bool _isLoading = false;
  bool _emailSent = false;

  @override
  void dispose() {
    _emailController.dispose();
    super.dispose();
  }

  Future<void> _handleResetPassword() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isLoading = true);

      // TODO: Implement actual password reset
      await Future.delayed(const Duration(seconds: 2));

      if (mounted) {
        setState(() {
          _isLoading = false;
          _emailSent = true;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      appBar: AppBar(
        backgroundColor: Colors.transparent,
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.pop(),
        ),
      ),
      body: SafeArea(
        child: Padding(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: _emailSent ? _buildSuccessState() : _buildFormState(),
        ),
      ),
    );
  }

  Widget _buildFormState() {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        // Icon
        Container(
          width: 64,
          height: 64,
          decoration: BoxDecoration(
            color: SanaColors.primaryLightest,
            borderRadius: BorderRadius.circular(16),
          ),
          child: const Icon(
            Icons.lock_reset,
            size: 32,
            color: SanaColors.primaryDark,
          ),
        ),

        const SizedBox(height: SanaSpacing.lg),

        // Title
        Text(
          'Forgot Password?',
          style: SanaTextStyles.heading1,
        ),
        const SizedBox(height: SanaSpacing.sm),
        Text(
          "Enter your email address and we'll send you instructions to reset your password.",
          style: SanaTextStyles.body.copyWith(
            color: SanaColors.textSecondary,
          ),
        ),

        const SizedBox(height: SanaSpacing.xl),

        // Email form
        Form(
          key: _formKey,
          child: SanaTextField(
            label: 'Email',
            hint: 'Enter your email',
            controller: _emailController,
            keyboardType: TextInputType.emailAddress,
            prefixIcon: Icons.email_outlined,
            textInputAction: TextInputAction.done,
            validator: (value) {
              if (value == null || value.isEmpty) {
                return 'Please enter your email';
              }
              if (!value.contains('@')) {
                return 'Please enter a valid email';
              }
              return null;
            },
          ),
        ),

        const SizedBox(height: SanaSpacing.lg),

        // Reset button
        SanaButton(
          text: 'Send Reset Link',
          onPressed: _handleResetPassword,
          isLoading: _isLoading,
        ),
      ],
    );
  }

  Widget _buildSuccessState() {
    return Column(
      mainAxisAlignment: MainAxisAlignment.center,
      children: [
        Container(
          width: 96,
          height: 96,
          decoration: BoxDecoration(
            color: SanaColors.successLight,
            shape: BoxShape.circle,
          ),
          child: const Icon(
            Icons.check_circle,
            size: 56,
            color: SanaColors.success,
          ),
        ),
        const SizedBox(height: SanaSpacing.lg),
        Text(
          'Check Your Email',
          style: SanaTextStyles.heading2,
        ),
        const SizedBox(height: SanaSpacing.sm),
        Text(
          'We sent a password reset link to\n${_emailController.text}',
          style: SanaTextStyles.body.copyWith(
            color: SanaColors.textSecondary,
          ),
          textAlign: TextAlign.center,
        ),
        const SizedBox(height: SanaSpacing.xl),
        SanaButton(
          text: 'Back to Sign In',
          onPressed: () => context.pop(),
        ),
        const SizedBox(height: SanaSpacing.md),
        TextButton(
          onPressed: () {
            setState(() => _emailSent = false);
          },
          child: Text(
            'Resend Email',
            style: SanaTextStyles.link,
          ),
        ),
      ],
    );
  }
}
