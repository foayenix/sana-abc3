import 'package:flutter/material.dart';

class VerificationTestScreen extends StatelessWidget {
  const VerificationTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SCVM - Credential Verification'),
      ),
      body: const Center(
        child: Text('Verification algorithm test interface'),
      ),
    );
  }
}
