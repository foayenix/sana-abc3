import 'dart:convert';
import 'package:http/http.dart' as http;
import 'endpoints.dart';

class ApiClient {
  final http.Client _client = http.Client();

  Future<Map<String, dynamic>> get(String url) async {
    try {
      final response = await _client.get(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('GET request failed: $e');
    }
  }

  Future<Map<String, dynamic>> post(
    String url,
    Map<String, dynamic> body,
  ) async {
    try {
      final response = await _client.post(
        Uri.parse(url),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode(body),
      );
      return _handleResponse(response);
    } catch (e) {
      throw Exception('POST request failed: $e');
    }
  }

  Map<String, dynamic> _handleResponse(http.Response response) {
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body);
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // Health check
  Future<bool> checkHealth() async {
    try {
      final response = await get(Endpoints.health);
      return response['status'] == 'healthy';
    } catch (e) {
      return false;
    }
  }

  // Scoring
  Future<Map<String, dynamic>> testFullFlow({String profile = 'balanced'}) async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/scoring/test-full-flow?profile=$profile',
    );
    return response;
  }

  Future<Map<String, dynamic>> generateDummyQuestionnaire({String profile = 'balanced'}) async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/scoring/generate-dummy?profile=$profile',
    );
    return response;
  }

  Future<Map<String, dynamic>> calculateScore(Map<String, dynamic> questionnaire) async {
    return post(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/scoring/calculate',
      questionnaire,
    );
  }

  Future<Map<String, dynamic>> getDomainInfo() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/scoring/domains/list',
    );
    return response;
  }

  Future<Map<String, dynamic>> calculateSismScore(
    String userId,
    Map<String, Map<String, int>> domainResponses,
  ) async {
    return post(Endpoints.scoringSism, {
      'user_id': userId,
      'domain_responses': domainResponses,
    });
  }

  // Matching
  Future<Map<String, dynamic>> recommendPractitioners(
    String userId,
    List<String> healthGoals,
    Map<String, dynamic> preferences, {
    int topK = 5,
  }) async {
    return post(Endpoints.matchingRecommend, {
      'user_id': userId,
      'health_goals': healthGoals,
      'preferences': preferences,
      'top_k': topK,
    });
  }

  // Safety
  Future<Map<String, dynamic>> assessSafety(
    String userId,
    Map<String, dynamic> healthData,
  ) async {
    return post(Endpoints.safetyAssess, {
      'user_id': userId,
      'health_data': healthData,
    });
  }

  // Evidence
  Future<Map<String, dynamic>> recommendInterventions(
    String userId,
    List<String> healthGoals,
    Map<String, double> domainScores, {
    List<String>? contraindications,
    int topK = 5,
  }) async {
    return post(Endpoints.evidenceRecommend, {
      'user_id': userId,
      'health_goals': healthGoals,
      'domain_scores': domainScores,
      'contraindications': contraindications ?? [],
      'top_k': topK,
    });
  }

  // Index
  Future<Map<String, dynamic>> calculateSanaIndex(
    String practitionerId,
    List<String> credentials,
    Map<String, dynamic> outcomeData,
    List<Map<String, dynamic>> reviews,
    bool verificationStatus,
  ) async {
    return post(Endpoints.indexCalculate, {
      'practitioner_id': practitionerId,
      'credentials': credentials,
      'outcome_data': outcomeData,
      'reviews': reviews,
      'verification_status': verificationStatus,
    });
  }

  // Health Graph / Evidence
  Future<Map<String, dynamic>> getGraphStatistics() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/evidence/statistics',
    );
    return response;
  }

  Future<List<dynamic>> searchInterventionsByDomain(
    String domain, {
    String minEvidence = 'weak',
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/evidence/interventions/domain/$domain?min_evidence=$minEvidence',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<List<dynamic>> searchInterventionsByCondition(
    String condition, {
    String minEvidence = 'weak',
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/evidence/interventions/condition/$condition?min_evidence=$minEvidence',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // Planning / SHAM
  Future<Map<String, dynamic>> testSHAMFullFlow({
    String profile = 'balanced',
    int timePerDay = 60,
    double budgetPerWeek = 50.0,
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/planning/test-full-flow?'
        'profile=$profile&'
        'time_per_day=$timePerDay&'
        'budget_per_week=$budgetPerWeek',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // Verification / SCVM
  Future<Map<String, dynamic>> testVerificationFullFlow({
    String profile = 'standard',
    String tier = 'standard',
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/verification/test-full-flow?'
        'profile=$profile&'
        'tier=$tier',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getVerificationTiers() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/verification/tiers',
    );
    return response;
  }

  Future<Map<String, dynamic>> getSupportedRegistries() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/verification/registries',
    );
    return response;
  }

  Future<Map<String, dynamic>> getKnownInstitutions() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/verification/institutions',
    );
    return response;
  }

  Future<Map<String, dynamic>> checkInstitution(String institutionName) async {
    return post(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/verification/check-institution?institution_name=$institutionName',
      {},
    );
  }

  // Matching / SPRM
  Future<Map<String, dynamic>> testMatchingFullFlow({
    String profile = 'struggling',
    double maxBudget = 80.0,
    double maxDistance = 10.0,
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/matching/test-matching?'
        'profile=$profile&'
        'max_budget=$maxBudget&'
        'max_distance=$maxDistance',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<List<dynamic>> getAllPractitioners() async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/matching/practitioners',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as List<dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<List<String>> getAvailableSpecialties() async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/matching/specialties',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return (jsonDecode(response.body) as List<dynamic>).cast<String>();
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<List<String>> getAvailableModalities() async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/matching/modalities',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return (jsonDecode(response.body) as List<dynamic>).cast<String>();
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  // Safety / SST
  Future<Map<String, dynamic>> testSafetyScenario({
    String scenario = 'safe',
  }) async {
    final response = await _client.get(
      Uri.parse(
        '${Endpoints.baseUrl}${Endpoints.apiPrefix}/safety/test-scenarios?'
        'scenario=$scenario',
      ),
      headers: {'Content-Type': 'application/json'},
    );
    if (response.statusCode >= 200 && response.statusCode < 300) {
      return jsonDecode(response.body) as Map<String, dynamic>;
    } else {
      throw Exception('HTTP ${response.statusCode}: ${response.body}');
    }
  }

  Future<Map<String, dynamic>> getSafetyResources() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/safety/resources',
    );
    return response;
  }

  Future<Map<String, dynamic>> getSafetyThresholds() async {
    final response = await get(
      '${Endpoints.baseUrl}${Endpoints.apiPrefix}/safety/thresholds',
    );
    return response;
  }

  void dispose() {
    _client.close();
  }
}
