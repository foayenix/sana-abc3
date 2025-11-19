/// User model
class User {
  final int id;
  final String email;
  final String fullName;
  final String role;
  final bool isActive;
  final bool isVerified;
  final String? avatar;
  final String? phone;
  final DateTime? dateOfBirth;
  final String? address;
  final List<String>? healthGoals;
  final DateTime createdAt;

  User({
    required this.id,
    required this.email,
    required this.fullName,
    required this.role,
    required this.isActive,
    required this.isVerified,
    this.avatar,
    this.phone,
    this.dateOfBirth,
    this.address,
    this.healthGoals,
    required this.createdAt,
  });

  factory User.fromJson(Map<String, dynamic> json) {
    return User(
      id: json['id'],
      email: json['email'],
      fullName: json['full_name'],
      role: json['role'] ?? 'client',
      isActive: json['is_active'] ?? true,
      isVerified: json['is_verified'] ?? false,
      avatar: json['avatar'],
      phone: json['phone'],
      dateOfBirth: json['date_of_birth'] != null
          ? DateTime.parse(json['date_of_birth'])
          : null,
      address: json['address'],
      healthGoals: json['health_goals'] != null
          ? List<String>.from(json['health_goals'])
          : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'email': email,
      'full_name': fullName,
      'role': role,
      'is_active': isActive,
      'is_verified': isVerified,
      'avatar': avatar,
      'phone': phone,
      'date_of_birth': dateOfBirth?.toIso8601String(),
      'address': address,
      'health_goals': healthGoals,
      'created_at': createdAt.toIso8601String(),
    };
  }

  User copyWith({
    int? id,
    String? email,
    String? fullName,
    String? role,
    bool? isActive,
    bool? isVerified,
    String? avatar,
    String? phone,
    DateTime? dateOfBirth,
    String? address,
    List<String>? healthGoals,
    DateTime? createdAt,
  }) {
    return User(
      id: id ?? this.id,
      email: email ?? this.email,
      fullName: fullName ?? this.fullName,
      role: role ?? this.role,
      isActive: isActive ?? this.isActive,
      isVerified: isVerified ?? this.isVerified,
      avatar: avatar ?? this.avatar,
      phone: phone ?? this.phone,
      dateOfBirth: dateOfBirth ?? this.dateOfBirth,
      address: address ?? this.address,
      healthGoals: healthGoals ?? this.healthGoals,
      createdAt: createdAt ?? this.createdAt,
    );
  }

  String get initials {
    final parts = fullName.split(' ');
    if (parts.length >= 2) {
      return '${parts[0][0]}${parts[1][0]}'.toUpperCase();
    }
    return fullName.isNotEmpty ? fullName[0].toUpperCase() : '?';
  }

  String get firstName {
    return fullName.split(' ').first;
  }

  bool get isClient => role == 'client';
  bool get isPractitioner => role == 'practitioner';
  bool get isAdmin => role == 'admin';
}
