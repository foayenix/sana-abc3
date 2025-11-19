import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/routes.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_text_field.dart';

class LoginScreen extends StatefulWidget {
  const LoginScreen({super.key});

  @override
  State<LoginScreen> createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    super.dispose();
  }

  Future<void> _handleLogin() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isLoading = true);

      // TODO: Implement actual login
      await Future.delayed(const Duration(seconds: 2));

      if (mounted) {
        setState(() => _isLoading = false);
        context.go(AppRoutes.home);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SafeArea(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              const SizedBox(height: SanaSpacing.xl),

              // Logo and title
              Center(
                child: Column(
                  children: [
                    Container(
                      width: 72,
                      height: 72,
                      decoration: BoxDecoration(
                        gradient: SanaColors.primaryGradient,
                        borderRadius: BorderRadius.circular(16),
                      ),
                      child: const Center(
                        child: Text(
                          'S',
                          style: TextStyle(
                            fontSize: 40,
                            fontWeight: FontWeight.w700,
                            color: SanaColors.white,
                          ),
                        ),
                      ),
                    ),
                    const SizedBox(height: SanaSpacing.lg),
                    Text(
                      'Welcome Back',
                      style: SanaTextStyles.heading1,
                    ),
                    const SizedBox(height: SanaSpacing.sm),
                    Text(
                      'Sign in to continue your health journey',
                      style: SanaTextStyles.subtitle,
                    ),
                  ],
                ),
              ),

              const SizedBox(height: SanaSpacing.xxl),

              // Login form
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    SanaTextField(
                      label: 'Email',
                      hint: 'Enter your email',
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      prefixIcon: Icons.email_outlined,
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
                    const SizedBox(height: SanaSpacing.md),
                    SanaTextField(
                      label: 'Password',
                      hint: 'Enter your password',
                      controller: _passwordController,
                      obscureText: true,
                      prefixIcon: Icons.lock_outline,
                      textInputAction: TextInputAction.done,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your password';
                        }
                        if (value.length < 6) {
                          return 'Password must be at least 6 characters';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),

              // Forgot password
              Align(
                alignment: Alignment.centerRight,
                child: TextButton(
                  onPressed: () => context.push(AppRoutes.forgotPassword),
                  child: Text(
                    'Forgot Password?',
                    style: SanaTextStyles.link,
                  ),
                ),
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Login button
              SanaButton(
                text: 'Sign In',
                onPressed: _handleLogin,
                isLoading: _isLoading,
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Divider
              Row(
                children: [
                  const Expanded(child: Divider()),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: SanaSpacing.md),
                    child: Text(
                      'or continue with',
                      style: SanaTextStyles.caption,
                    ),
                  ),
                  const Expanded(child: Divider()),
                ],
              ),

              const SizedBox(height: SanaSpacing.lg),

              // Social login buttons
              Row(
                children: [
                  Expanded(
                    child: _SocialButton(
                      icon: Icons.g_mobiledata,
                      label: 'Google',
                      onPressed: () {
                        // TODO: Implement Google login
                      },
                    ),
                  ),
                  const SizedBox(width: SanaSpacing.md),
                  Expanded(
                    child: _SocialButton(
                      icon: Icons.apple,
                      label: 'Apple',
                      onPressed: () {
                        // TODO: Implement Apple login
                      },
                    ),
                  ),
                ],
              ),

              const SizedBox(height: SanaSpacing.xl),

              // Register link
              Center(
                child: Row(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    Text(
                      "Don't have an account? ",
                      style: SanaTextStyles.bodySmall,
                    ),
                    GestureDetector(
                      onTap: () => context.push(AppRoutes.register),
                      child: Text(
                        'Sign Up',
                        style: SanaTextStyles.link,
                      ),
                    ),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}

class _SocialButton extends StatelessWidget {
  final IconData icon;
  final String label;
  final VoidCallback onPressed;

  const _SocialButton({
    required this.icon,
    required this.label,
    required this.onPressed,
  });

  @override
  Widget build(BuildContext context) {
    return OutlinedButton(
      onPressed: onPressed,
      style: OutlinedButton.styleFrom(
        padding: const EdgeInsets.symmetric(vertical: 14),
        side: const BorderSide(color: SanaColors.grey300),
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(SanaBorderRadius.md),
        ),
      ),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.center,
        children: [
          Icon(
            icon,
            size: 24,
            color: SanaColors.textPrimary,
          ),
          const SizedBox(width: 8),
          Text(
            label,
            style: SanaTextStyles.body.copyWith(
              fontWeight: FontWeight.w500,
            ),
          ),
        ],
      ),
    );
  }
}
