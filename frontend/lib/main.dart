import 'package:flutter/material.dart';
import 'screens/home_screen.dart';

void main() {
  runApp(const SanaAlgorithmsApp());
}

class SanaAlgorithmsApp extends StatelessWidget {
  const SanaAlgorithmsApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'SANA Algorithms Suite',
      theme: ThemeData(
        colorScheme: ColorScheme.fromSeed(seedColor: Colors.teal),
        useMaterial3: true,
      ),
      home: const HomeScreen(),
      debugShowCheckedModeBanner: false,
    );
  }
}
