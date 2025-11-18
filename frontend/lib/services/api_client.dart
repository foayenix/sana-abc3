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

  void dispose() {
    _client.close();
  }
}
