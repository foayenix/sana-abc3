class UserProfile {
  final String userId;
  final String email;
  final String fullName;
  final int? age;
  final Map<String, dynamic> preferences;
  final List<String> healthGoals;

  UserProfile({
    required this.userId,
    required this.email,
    required this.fullName,
    this.age,
    this.preferences = const {},
    this.healthGoals = const [],
  });

  factory UserProfile.fromJson(Map<String, dynamic> json) {
    return UserProfile(
      userId: json['user_id'],
      email: json['email'],
      fullName: json['full_name'],
      age: json['age'],
      preferences: json['preferences'] ?? {},
      healthGoals: List<String>.from(json['health_goals'] ?? []),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'user_id': userId,
      'email': email,
      'full_name': fullName,
      'age': age,
      'preferences': preferences,
      'health_goals': healthGoals,
    };
  }
}
