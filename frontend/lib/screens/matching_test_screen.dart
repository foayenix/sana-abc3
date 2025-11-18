import 'package:flutter/material.dart';

class MatchingTestScreen extends StatelessWidget {
  const MatchingTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SPRM - Practitioner Matching'),
      ),
      body: const Center(
        child: Text('Matching algorithm test interface'),
      ),
    );
  }
}
