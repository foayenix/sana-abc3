import 'package:flutter/material.dart';

class ScoreDisplay extends StatelessWidget {
  final double score;
  final String label;
  final Color? color;

  const ScoreDisplay({
    super.key,
    required this.score,
    required this.label,
    this.color,
  });

  @override
  Widget build(BuildContext context) {
    final displayColor = color ?? _getColorForScore(score);

    return Column(
      children: [
        Stack(
          alignment: Alignment.center,
          children: [
            SizedBox(
              width: 80,
              height: 80,
              child: CircularProgressIndicator(
                value: score / 100,
                strokeWidth: 8,
                backgroundColor: Colors.grey.shade200,
                color: displayColor,
              ),
            ),
            Text(
              score.toStringAsFixed(0),
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: displayColor,
              ),
            ),
          ],
        ),
        const SizedBox(height: 8),
        Text(
          label,
          style: const TextStyle(fontSize: 12, color: Colors.grey),
        ),
      ],
    );
  }

  Color _getColorForScore(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.teal;
    if (score >= 40) return Colors.orange;
    return Colors.red;
  }
}
