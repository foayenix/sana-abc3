import 'package:flutter/material.dart';

class ScoringTestScreen extends StatelessWidget {
  const ScoringTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SISM - Intake Scoring'),
      ),
      body: const Center(
        child: Text('Scoring algorithm test interface'),
      ),
    );
  }
}
