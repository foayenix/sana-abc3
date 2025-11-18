import 'package:flutter/material.dart';

class PlanningTestScreen extends StatelessWidget {
  const PlanningTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SHAM - Habit Planning'),
      ),
      body: const Center(
        child: Text('Planning algorithm test interface'),
      ),
    );
  }
}
