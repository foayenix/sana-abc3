import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';
import '../../../shared/widgets/sana_button.dart';
import '../../../shared/widgets/sana_text_field.dart';

class RegisterScreen extends StatefulWidget {
  const RegisterScreen({super.key});

  @override
  State<RegisterScreen> createState() => _RegisterScreenState();
}

class _RegisterScreenState extends State<RegisterScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _emailController = TextEditingController();
  final _licenseController = TextEditingController();
  final _specialtyController = TextEditingController();
  bool _isLoading = false;

  @override
  void dispose() {
    _nameController.dispose();
    _emailController.dispose();
    _licenseController.dispose();
    _specialtyController.dispose();
    super.dispose();
  }

  Future<void> _handleApply() async {
    if (_formKey.currentState?.validate() ?? false) {
      setState(() => _isLoading = true);
      await Future.delayed(const Duration(seconds: 2));
      if (mounted) {
        setState(() => _isLoading = false);
        _showSuccessDialog();
      }
    }
  }

  void _showSuccessDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Application Submitted'),
        content: const Text(
          'Thank you for applying! We will review your credentials and get back to you within 2-3 business days.',
        ),
        actions: [
          TextButton(
            onPressed: () {
              Navigator.pop(context);
              context.pop();
            },
            child: const Text('OK'),
          ),
        ],
      ),
    );
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
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(SanaSpacing.lg),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text('Join SANA', style: SanaTextStyles.heading1),
              const SizedBox(height: SanaSpacing.sm),
              Text(
                'Apply to become a verified practitioner',
                style: SanaTextStyles.subtitle,
              ),
              const SizedBox(height: SanaSpacing.xl),
              Form(
                key: _formKey,
                child: Column(
                  children: [
                    SanaTextField(
                      label: 'Full Name',
                      hint: 'Dr. Jane Smith',
                      controller: _nameController,
                      prefixIcon: Icons.person_outline,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your name';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: SanaSpacing.md),
                    SanaTextField(
                      label: 'Email',
                      hint: 'your@email.com',
                      controller: _emailController,
                      keyboardType: TextInputType.emailAddress,
                      prefixIcon: Icons.email_outlined,
                      validator: (value) {
                        if (value == null || !value.contains('@')) {
                          return 'Please enter a valid email';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: SanaSpacing.md),
                    SanaTextField(
                      label: 'License Number',
                      hint: 'Enter your license number',
                      controller: _licenseController,
                      prefixIcon: Icons.verified_outlined,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your license number';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: SanaSpacing.md),
                    SanaTextField(
                      label: 'Primary Specialty',
                      hint: 'e.g., Acupuncture, Massage Therapy',
                      controller: _specialtyController,
                      prefixIcon: Icons.medical_services_outlined,
                      validator: (value) {
                        if (value == null || value.isEmpty) {
                          return 'Please enter your specialty';
                        }
                        return null;
                      },
                    ),
                  ],
                ),
              ),
              const SizedBox(height: SanaSpacing.lg),
              SanaButton(
                text: 'Submit Application',
                onPressed: _handleApply,
                isLoading: _isLoading,
              ),
            ],
          ),
        ),
      ),
    );
  }
}
