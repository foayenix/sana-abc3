class Endpoints {
  static const String baseUrl = 'http://localhost:8000';
  static const String apiPrefix = '/api/v1';

  // Health check
  static const String health = '$baseUrl/health';

  // Scoring endpoints
  static const String scoringSism = '$baseUrl$apiPrefix/scoring/sism';
  static String scoringHistory(String userId) =>
      '$baseUrl$apiPrefix/scoring/user/$userId/history';

  // Matching endpoints
  static const String matchingRecommend = '$baseUrl$apiPrefix/matching/recommend';
  static const String matchingScore = '$baseUrl$apiPrefix/matching/score';

  // Verification endpoints
  static const String verificationVerify = '$baseUrl$apiPrefix/verification/verify';
  static String verificationStatus(String practitionerId) =>
      '$baseUrl$apiPrefix/verification/status/$practitionerId';

  // Safety endpoints
  static const String safetyAssess = '$baseUrl$apiPrefix/safety/assess';
  static String safetyAlerts(String userId) =>
      '$baseUrl$apiPrefix/safety/user/$userId/alerts';

  // Engagement endpoints
  static const String engagementPredict = '$baseUrl$apiPrefix/engagement/predict';
  static const String engagementFollowup = '$baseUrl$apiPrefix/engagement/followup';
  static const String engagementOutcome = '$baseUrl$apiPrefix/engagement/outcome-uplift';

  // Evidence endpoints
  static const String evidenceRecommend = '$baseUrl$apiPrefix/evidence/recommend';
  static String evidenceIntervention(String interventionId) =>
      '$baseUrl$apiPrefix/evidence/intervention/$interventionId';
  static String evidenceCondition(String condition) =>
      '$baseUrl$apiPrefix/evidence/condition/$condition';

  // Planning endpoints
  static const String planningHabits = '$baseUrl$apiPrefix/planning/habits';
  static const String planningTimetable = '$baseUrl$apiPrefix/planning/timetable';
  static const String planningOptimize = '$baseUrl$apiPrefix/planning/optimize';

  // Index endpoints
  static const String indexCalculate = '$baseUrl$apiPrefix/index/calculate';
  static String indexPractitioner(String practitionerId) =>
      '$baseUrl$apiPrefix/index/practitioner/$practitionerId';
  static const String indexLeaderboard = '$baseUrl$apiPrefix/index/leaderboard';
}
