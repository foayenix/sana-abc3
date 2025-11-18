import 'package:flutter/material.dart';

class EvidenceTestScreen extends StatelessWidget {
  const EvidenceTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Evidence Engine'),
      ),
      body: const Center(
        child: Text('Evidence engine test interface'),
      ),
    );
  }
}
