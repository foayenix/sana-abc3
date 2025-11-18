class Intervention {
  final String id;
  final String name;
  final String category;
  final String evidenceRating;
  final List<String> targetDomains;
  final List<String> contraindications;
  final int typicalDurationMinutes;
  final double? costEstimate;

  Intervention({
    required this.id,
    required this.name,
    required this.category,
    required this.evidenceRating,
    required this.targetDomains,
    this.contraindications = const [],
    required this.typicalDurationMinutes,
    this.costEstimate,
  });

  factory Intervention.fromJson(Map<String, dynamic> json) {
    return Intervention(
      id: json['id'],
      name: json['name'],
      category: json['category'],
      evidenceRating: json['evidence_rating'],
      targetDomains: List<String>.from(json['target_domains']),
      contraindications: List<String>.from(json['contraindications'] ?? []),
      typicalDurationMinutes: json['typical_duration_minutes'],
      costEstimate: json['cost_estimate']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'name': name,
      'category': category,
      'evidence_rating': evidenceRating,
      'target_domains': targetDomains,
      'contraindications': contraindications,
      'typical_duration_minutes': typicalDurationMinutes,
      'cost_estimate': costEstimate,
    };
  }
}
