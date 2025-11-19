import 'package:flutter/material.dart';
import 'dart:math' as math;
import '../../config/colors.dart';
import '../../config/theme.dart';

class HealthScoreWidget extends StatelessWidget {
  final int score;
  final double size;
  final bool showLabel;
  final bool animated;

  const HealthScoreWidget({
    super.key,
    required this.score,
    this.size = 160,
    this.showLabel = true,
    this.animated = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      mainAxisSize: MainAxisSize.min,
      children: [
        SizedBox(
          width: size,
          height: size,
          child: Stack(
            alignment: Alignment.center,
            children: [
              // Background circle
              CustomPaint(
                size: Size(size, size),
                painter: _ScoreCirclePainter(
                  progress: 1.0,
                  color: SanaColors.grey200,
                  strokeWidth: size * 0.08,
                ),
              ),
              // Progress circle
              animated
                  ? TweenAnimationBuilder<double>(
                      tween: Tween(begin: 0, end: score / 100),
                      duration: const Duration(milliseconds: 1500),
                      curve: Curves.easeOutCubic,
                      builder: (context, value, child) {
                        return CustomPaint(
                          size: Size(size, size),
                          painter: _ScoreCirclePainter(
                            progress: value,
                            color: SanaColors.getHealthColor(score),
                            strokeWidth: size * 0.08,
                          ),
                        );
                      },
                    )
                  : CustomPaint(
                      size: Size(size, size),
                      painter: _ScoreCirclePainter(
                        progress: score / 100,
                        color: SanaColors.getHealthColor(score),
                        strokeWidth: size * 0.08,
                      ),
                    ),
              // Score text
              Column(
                mainAxisSize: MainAxisSize.min,
                children: [
                  animated
                      ? TweenAnimationBuilder<int>(
                          tween: IntTween(begin: 0, end: score),
                          duration: const Duration(milliseconds: 1500),
                          curve: Curves.easeOutCubic,
                          builder: (context, value, child) {
                            return Text(
                              '$value',
                              style: TextStyle(
                                fontSize: size * 0.28,
                                fontWeight: FontWeight.w700,
                                color: SanaColors.textPrimary,
                                height: 1,
                              ),
                            );
                          },
                        )
                      : Text(
                          '$score',
                          style: TextStyle(
                            fontSize: size * 0.28,
                            fontWeight: FontWeight.w700,
                            color: SanaColors.textPrimary,
                            height: 1,
                          ),
                        ),
                  const SizedBox(height: 4),
                  Text(
                    _getScoreLabel(),
                    style: TextStyle(
                      fontSize: size * 0.1,
                      fontWeight: FontWeight.w500,
                      color: SanaColors.getHealthColor(score),
                    ),
                  ),
                ],
              ),
            ],
          ),
        ),
        if (showLabel) ...[
          const SizedBox(height: 12),
          Text(
            'Health Score',
            style: SanaTextStyles.subtitle.copyWith(
              color: SanaColors.textSecondary,
            ),
          ),
        ],
      ],
    );
  }

  String _getScoreLabel() {
    if (score >= 80) return 'Excellent';
    if (score >= 60) return 'Good';
    if (score >= 40) return 'Fair';
    if (score >= 20) return 'Needs Work';
    return 'Critical';
  }
}

class _ScoreCirclePainter extends CustomPainter {
  final double progress;
  final Color color;
  final double strokeWidth;

  _ScoreCirclePainter({
    required this.progress,
    required this.color,
    required this.strokeWidth,
  });

  @override
  void paint(Canvas canvas, Size size) {
    final center = Offset(size.width / 2, size.height / 2);
    final radius = (size.width - strokeWidth) / 2;

    final paint = Paint()
      ..color = color
      ..strokeWidth = strokeWidth
      ..style = PaintingStyle.stroke
      ..strokeCap = StrokeCap.round;

    canvas.drawArc(
      Rect.fromCircle(center: center, radius: radius),
      -math.pi / 2,
      2 * math.pi * progress,
      false,
      paint,
    );
  }

  @override
  bool shouldRepaint(covariant _ScoreCirclePainter oldDelegate) {
    return oldDelegate.progress != progress || oldDelegate.color != color;
  }
}

class MiniHealthScore extends StatelessWidget {
  final int score;
  final double size;

  const MiniHealthScore({
    super.key,
    required this.score,
    this.size = 48,
  });

  @override
  Widget build(BuildContext context) {
    return Container(
      width: size,
      height: size,
      decoration: BoxDecoration(
        shape: BoxShape.circle,
        color: SanaColors.getHealthColor(score).withOpacity(0.15),
      ),
      child: Center(
        child: Text(
          '$score',
          style: TextStyle(
            fontSize: size * 0.4,
            fontWeight: FontWeight.w700,
            color: SanaColors.getHealthColor(score),
          ),
        ),
      ),
    );
  }
}

class HealthScoreBar extends StatelessWidget {
  final int score;
  final double height;
  final bool showLabel;

  const HealthScoreBar({
    super.key,
    required this.score,
    this.height = 8,
    this.showLabel = true,
  });

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        if (showLabel) ...[
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Health Score',
                style: SanaTextStyles.bodySmall.copyWith(
                  fontWeight: FontWeight.w500,
                ),
              ),
              Text(
                '$score/100',
                style: SanaTextStyles.bodySmall.copyWith(
                  fontWeight: FontWeight.w600,
                  color: SanaColors.getHealthColor(score),
                ),
              ),
            ],
          ),
          const SizedBox(height: 8),
        ],
        ClipRRect(
          borderRadius: BorderRadius.circular(height / 2),
          child: Stack(
            children: [
              Container(
                height: height,
                width: double.infinity,
                color: SanaColors.grey200,
              ),
              TweenAnimationBuilder<double>(
                tween: Tween(begin: 0, end: score / 100),
                duration: const Duration(milliseconds: 1000),
                curve: Curves.easeOutCubic,
                builder: (context, value, child) {
                  return FractionallySizedBox(
                    widthFactor: value,
                    child: Container(
                      height: height,
                      decoration: BoxDecoration(
                        color: SanaColors.getHealthColor(score),
                        borderRadius: BorderRadius.circular(height / 2),
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ],
    );
  }
}
