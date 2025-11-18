import 'package:flutter/material.dart';
import 'scoring_test_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SANA Algorithms Suite'),
        backgroundColor: Theme.of(context).colorScheme.inversePrimary,
      ),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.psychology, size: 100, color: Colors.teal),
            const SizedBox(height: 20),
            const Text(
              'SANA Health Framework',
              style: TextStyle(fontSize: 24, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 10),
            const Text(
              'Algorithm Testing Dashboard',
              style: TextStyle(fontSize: 16, color: Colors.grey),
            ),
            const SizedBox(height: 40),
            ElevatedButton.icon(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(
                    builder: (context) => const ScoringTestScreen(),
                  ),
                );
              },
              icon: const Icon(Icons.science),
              label: const Text('Test SISM Algorithm'),
            ),
          ],
        ),
      ),
    );
  }
}
