import 'package:flutter/material.dart';

class SafetyTestScreen extends StatelessWidget {
  const SafetyTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SST - Safety & Triage'),
      ),
      body: const Center(
        child: Text('Safety algorithm test interface'),
      ),
    );
  }
}
