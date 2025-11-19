import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../config/colors.dart';
import '../../config/theme.dart';

/// Health score circular widget
class HealthScoreWidget extends StatelessWidget {
  final int score;
  final double size;
  final bool showLabel;

  const HealthScoreWidget({
    super.key,
    required this.score,
    this.size = 120,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    final color = SanaColors.getHealthColor(score);

    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: CustomPaint(
            painter: _ScoreRingPainter(
              score: score,
              color: color,
              backgroundColor: SanaColors.grey200,
            ),
            child: Center(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  Text(
                    score.toString(),
                    style: SanaTextStyles.heading1.copyWith(
                      fontSize: size * 0.3,
                      color: color,
                    ),
                  ),
                  if (showLabel)
                    Text(
                      'Score',
                      style: SanaTextStyles.caption.copyWith(
                        fontSize: size * 0.1,
                      ),
                    ),
                ],
              ),
            ),
          ),
        ),
      ],
    );
  }
}

class _ScoreRingPainter extends CustomPainter {
  final int score;
  final Color color;
  final Color backgroundColor;

  _ScoreRingPainter({
    required this.score,
    required this.color,
    required this.backgroundColor,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = size.width / 2 - 8;
    const strokeWidth = 12.0;

    // Background ring
    final bgPaint = Paint()
      ..color = backgroundColor
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    canvas.drawCircle(center, radius, bgPaint);

    // Score ring
    final scorePaint = Paint()
      ..color = color
      ..style = PaintingStyle.stroke
      ..strokeWidth = strokeWidth
      ..strokeCap = StrokeCap.round;

    final sweepAngle = (score / 100) * 2 * math.pi;
    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      sweepAngle,
      false,
      scorePaint,
    );
  }

  @override
  bool shouldRepaint(covariant _ScoreRingPainter oldDelegate) {
    return oldDelegate.score != score || oldDelegate.color != color;
  }
}
