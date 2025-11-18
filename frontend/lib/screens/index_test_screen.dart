import 'package:flutter/material.dart';

class IndexTestScreen extends StatelessWidget {
  const IndexTestScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SANA Index'),
      ),
      body: const Center(
        child: Text('SANA Index test interface'),
      ),
    );
  }
}
