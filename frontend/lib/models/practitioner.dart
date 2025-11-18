class Practitioner {
  final String id;
  final String fullName;
  final List<String> specialties;
  final List<String> credentials;
  final bool verified;
  final double? sanaIndexScore;
  final double? hourlyRate;

  Practitioner({
    required this.id,
    required this.fullName,
    required this.specialties,
    required this.credentials,
    this.verified = false,
    this.sanaIndexScore,
    this.hourlyRate,
  });

  factory Practitioner.fromJson(Map<String, dynamic> json) {
    return Practitioner(
      id: json['id'],
      fullName: json['full_name'],
      specialties: List<String>.from(json['specialties']),
      credentials: List<String>.from(json['credentials']),
      verified: json['verified'] ?? false,
      sanaIndexScore: json['sana_index_score']?.toDouble(),
      hourlyRate: json['hourly_rate']?.toDouble(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'full_name': fullName,
      'specialties': specialties,
      'credentials': credentials,
      'verified': verified,
      'sana_index_score': sanaIndexScore,
      'hourly_rate': hourlyRate,
    };
  }
}
