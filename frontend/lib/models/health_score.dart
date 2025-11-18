class HealthScore {
  final String id;
  final String userId;
  final double overallScore;
  final Map<String, double> domainScores;
  final DateTime calculatedAt;

  HealthScore({
    required this.id,
    required this.userId,
    required this.overallScore,
    required this.domainScores,
    required this.calculatedAt,
  });

  factory HealthScore.fromJson(Map<String, dynamic> json) {
    return HealthScore(
      id: json['id'],
      userId: json['user_id'],
      overallScore: json['overall_score'].toDouble(),
      domainScores: Map<String, double>.from(
        json['domain_scores'].map(
          (key, value) => MapEntry(key, value.toDouble()),
        ),
      ),
      calculatedAt: DateTime.parse(json['calculated_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'user_id': userId,
      'overall_score': overallScore,
      'domain_scores': domainScores,
      'calculated_at': calculatedAt.toIso8601String(),
    };
  }
}
