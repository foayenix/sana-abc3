import 'package:flutter/material.dart';

class EngagementTestScreen extends StatelessWidget {
  const EngagementTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SEC - Engagement Prediction'),
      ),
      body: const Center(
        child: Text('Engagement algorithm test interface'),
      ),
    );
  }
}
