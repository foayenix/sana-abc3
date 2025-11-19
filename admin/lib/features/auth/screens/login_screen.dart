import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Container(
          width: 400,
          padding: const EdgeInsets.all(32),
          decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(16), boxShadow: [BoxShadow(color: SanaColors.black.withOpacity(0.1), blurRadius: 20)]),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Container(
                width: 64, height: 64,
                decoration: BoxDecoration(gradient: SanaColors.primaryGradient, borderRadius: BorderRadius.circular(12)),
                child: const Center(child: Text('S', style: TextStyle(fontSize: 36, fontWeight: FontWeight.w700, color: SanaColors.white))),
              ),
              const SizedBox(height: 24),
              Text('Admin Portal', style: SanaTextStyles.heading2),
              const SizedBox(height: 32),
              TextField(decoration: const InputDecoration(labelText: 'Email', prefixIcon: Icon(Icons.email_outlined))),
              const SizedBox(height: 16),
              TextField(obscureText: true, decoration: const InputDecoration(labelText: 'Password', prefixIcon: Icon(Icons.lock_outline))),
              const SizedBox(height: 24),
              SizedBox(
                width: double.infinity,
                child: ElevatedButton(onPressed: () => context.go('/dashboard'), child: const Padding(padding: EdgeInsets.all(12), child: Text('Sign In'))),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
