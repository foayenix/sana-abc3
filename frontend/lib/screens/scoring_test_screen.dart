import 'package:flutter/material.dart';
import '../services/api_client.dart';

class ScoringTestScreen extends StatefulWidget {
  const ScoringTestScreen({super.key});

  @override
  State<ScoringTestScreen> createState() => _ScoringTestScreenState();
}

class _ScoringTestScreenState extends State<ScoringTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _selectedProfile = 'balanced';
  Map<String, dynamic>? _result;
  bool _isLoading = false;
  String? _errorMessage;

  final List<String> _profiles = [
    'balanced',
    'struggling',
    'thriving',
    'mixed',
    'physical_weak',
    'emotional_weak',
  ];

  final Map<String, String> _profileDescriptions = {
    'balanced': 'Generally healthy (scores 6-8)',
    'struggling': 'Low scores across domains (3-5)',
    'thriving': 'High scores everywhere (8-10)',
    'mixed': 'Random realistic mix',
    'physical_weak': 'Strong except physical',
    'emotional_weak': 'Strong except emotional',
  };

  Future<void> _runTest() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final result = await _apiClient.testFullFlow(profile: _selectedProfile);
      setState(() {
        _result = result;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SISM - Intake Scoring Model'),
        backgroundColor: Colors.teal,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoCard(),
            const SizedBox(height: 20),
            _buildProfileSelector(),
            const SizedBox(height: 20),
            _buildTestButton(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_result != null) _buildResultsCard(),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.info_outline, color: Colors.teal),
                const SizedBox(width: 8),
                const Text(
                  'About SISM',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SISM (SANA Intake Scoring Model) calculates a baseline health score from multi-domain wellness questionnaire data.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            const Text(
              'Domains: Physical - Emotional - Social - Cognitive - Spiritual',
              style: TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProfileSelector() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Select Test Profile',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _selectedProfile,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
                contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
              ),
              items: _profiles.map((profile) {
                return DropdownMenuItem(
                  value: profile,
                  child: Text(profile.replaceAll('_', ' ').toUpperCase()),
                );
              }).toList(),
              onChanged: (value) {
                if (value != null) {
                  setState(() {
                    _selectedProfile = value;
                  });
                }
              },
            ),
            const SizedBox(height: 8),
            Text(
              _profileDescriptions[_selectedProfile] ?? '',
              style: const TextStyle(fontSize: 12, color: Colors.grey),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildTestButton() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _runTest,
        icon: const Icon(Icons.play_arrow),
        label: const Text('Run SISM Test'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.teal,
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return const Center(
      child: CircularProgressIndicator(),
    );
  }

  Widget _buildErrorCard() {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Row(
          children: [
            Icon(Icons.error, color: Colors.red),
            const SizedBox(width: 12),
            Expanded(
              child: Text(
                _errorMessage!,
                style: TextStyle(color: Colors.red.shade900),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResultsCard() {
    final overallScore = _result!['overall_score'];
    final domainScores = _result!['domain_scores'] as Map<String, dynamic>;
    final weakDomains = _result!['weak_domains'] as List<dynamic>;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Results',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 20),

            // Overall Score
            _buildScoreDisplay(
              'Overall Health Score',
              overallScore,
              isOverall: true,
            ),

            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            // Domain Scores
            const Text(
              'Domain Breakdown',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),

            ...domainScores.entries.map((entry) {
              final domain = entry.key;
              final score = entry.value['normalized_score'];
              return Padding(
                padding: const EdgeInsets.only(bottom: 12.0),
                child: _buildDomainScore(domain, score),
              );
            }).toList(),

            const SizedBox(height: 20),
            const Divider(),
            const SizedBox(height: 20),

            // Weak Domains
            if (weakDomains.isNotEmpty) ...[
              Row(
                children: [
                  Icon(Icons.warning_amber, color: Colors.orange),
                  const SizedBox(width: 8),
                  const Text(
                    'Areas for Improvement',
                    style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                  ),
                ],
              ),
              const SizedBox(height: 12),
              Wrap(
                spacing: 8,
                children: weakDomains.map((domain) {
                  return Chip(
                    label: Text(domain.toString().toUpperCase()),
                    backgroundColor: Colors.orange.shade100,
                  );
                }).toList(),
              ),
            ] else ...[
              Row(
                children: [
                  Icon(Icons.check_circle, color: Colors.green),
                  const SizedBox(width: 8),
                  const Text(
                    'All domains are healthy!',
                    style: TextStyle(fontSize: 16, color: Colors.green),
                  ),
                ],
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildScoreDisplay(String label, dynamic score, {bool isOverall = false}) {
    final scoreValue = (score as num).toDouble();
    final color = _getScoreColor(scoreValue);

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(
            fontSize: isOverall ? 16 : 14,
            fontWeight: isOverall ? FontWeight.bold : FontWeight.normal,
          ),
        ),
        const SizedBox(height: 8),
        Row(
          children: [
            Expanded(
              child: LinearProgressIndicator(
                value: scoreValue / 100,
                backgroundColor: Colors.grey.shade200,
                valueColor: AlwaysStoppedAnimation<Color>(color),
                minHeight: isOverall ? 20 : 12,
              ),
            ),
            const SizedBox(width: 12),
            Text(
              scoreValue.toStringAsFixed(1),
              style: TextStyle(
                fontSize: isOverall ? 20 : 16,
                fontWeight: FontWeight.bold,
                color: color,
              ),
            ),
          ],
        ),
      ],
    );
  }

  Widget _buildDomainScore(String domain, dynamic score) {
    return _buildScoreDisplay(
      domain.toUpperCase(),
      score,
      isOverall: false,
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 75) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }
}
