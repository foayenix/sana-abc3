import 'package:flutter/material.dart';
import '../services/api_client.dart';

class MatchingTestScreen extends StatefulWidget {
  const MatchingTestScreen({super.key});

  @override
  State<MatchingTestScreen> createState() => _MatchingTestScreenState();
}

class _MatchingTestScreenState extends State<MatchingTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _profile = 'struggling';
  double _maxBudget = 80.0;
  double _maxDistance = 10.0;

  Map<String, dynamic>? _result;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _findMatches() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final result = await _apiClient.testMatchingFullFlow(
        profile: _profile,
        maxBudget: _maxBudget,
        maxDistance: _maxDistance,
      );

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
        title: const Text('SPRM - Practitioner Matching'),
        backgroundColor: Colors.deepPurple,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoCard(),
            const SizedBox(height: 20),
            _buildControlsCard(),
            const SizedBox(height: 20),
            _buildFindButton(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_result != null) ...[
              _buildMatchSummary(),
              const SizedBox(height: 20),
              _buildRecommendations(),
            ],
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
                Icon(Icons.people_alt, color: Colors.deepPurple),
                const SizedBox(width: 8),
                const Text(
                  'About SPRM',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SPRM (Practitioner Recommendation Model) intelligently matches you with verified CAM practitioners based on your health needs, preferences, budget, and location.',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildControlsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Matching Parameters',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            DropdownButtonFormField<String>(
              value: _profile,
              decoration: const InputDecoration(
                labelText: 'Health Profile',
                border: OutlineInputBorder(),
              ),
              items: ['balanced', 'struggling', 'thriving', 'physical_weak', 'emotional_weak']
                  .map((p) => DropdownMenuItem(
                      value: p, child: Text(p.toUpperCase().replaceAll('_', ' '))))
                  .toList(),
              onChanged: (value) => setState(() => _profile = value!),
            ),

            const SizedBox(height: 16),

            Text('Max Budget: £${_maxBudget.toStringAsFixed(0)}/session'),
            Slider(
              value: _maxBudget,
              min: 30,
              max: 150,
              divisions: 12,
              label: '£${_maxBudget.toStringAsFixed(0)}',
              onChanged: (value) => setState(() => _maxBudget = value),
            ),

            const SizedBox(height: 8),

            Text('Max Distance: ${_maxDistance.toStringAsFixed(0)} km'),
            Slider(
              value: _maxDistance,
              min: 1,
              max: 50,
              divisions: 49,
              label: '${_maxDistance.toStringAsFixed(0)} km',
              onChanged: (value) => setState(() => _maxDistance = value),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildFindButton() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _findMatches,
        icon: const Icon(Icons.search),
        label: const Text('Find Practitioners'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.deepPurple,
          foregroundColor: Colors.white,
        ),
      ),
    );
  }

  Widget _buildLoadingIndicator() {
    return const Center(
      child: Column(
        children: [
          CircularProgressIndicator(),
          SizedBox(height: 16),
          Text('Finding your perfect practitioner matches...'),
        ],
      ),
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
                child: Text(_errorMessage!,
                    style: TextStyle(color: Colors.red.shade900))),
          ],
        ),
      ),
    );
  }

  Widget _buildMatchSummary() {
    final matches = _result!['matches'];
    final sism = _result!['sism_output'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Match Results',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              matches['match_summary'],
              style: TextStyle(fontSize: 14, color: Colors.grey[700]),
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatBox(
                  'Your Score',
                  '${sism['overall_score'].toStringAsFixed(1)}',
                  Icons.assessment,
                  Colors.blue,
                ),
                _buildStatBox(
                  'Practitioners',
                  '${matches['total_practitioners_filtered']}',
                  Icons.people,
                  Colors.green,
                ),
                _buildStatBox(
                  'Matches',
                  '${(matches['top_recommendations'] as List).length}',
                  Icons.star,
                  Colors.amber,
                ),
              ],
            ),
            if ((sism['weak_domains'] as List).isNotEmpty) ...[
              const SizedBox(height: 16),
              const Text('Your Focus Areas:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                children: (sism['weak_domains'] as List)
                    .map((d) => Chip(
                          label: Text(d.toString().toUpperCase()),
                          backgroundColor: Colors.deepPurple.shade50,
                        ))
                    .toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildRecommendations() {
    final recommendations = _result!['matches']['top_recommendations'] as List;

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        const Text(
          'Top Recommendations',
          style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ...recommendations.map((rec) => _buildPractitionerCard(rec)),
      ],
    );
  }

  Widget _buildPractitionerCard(Map<String, dynamic> recommendation) {
    final practitioner = recommendation['practitioner'];
    final matchScore = recommendation['match_score'];
    final score = matchScore['overall_score'];

    return Card(
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            // Header
            Row(
              children: [
                CircleAvatar(
                  backgroundColor: Colors.deepPurple.shade100,
                  child: Text(
                    practitioner['full_name'].toString().substring(0, 1),
                    style: TextStyle(
                      color: Colors.deepPurple.shade700,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                const SizedBox(width: 12),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        practitioner['full_name'],
                        style: const TextStyle(
                          fontSize: 16,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        practitioner['business_name'] ?? '',
                        style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
                  decoration: BoxDecoration(
                    color: _getScoreColor(score).withOpacity(0.2),
                    borderRadius: BorderRadius.circular(20),
                  ),
                  child: Text(
                    '${score.toStringAsFixed(0)}%',
                    style: TextStyle(
                      fontWeight: FontWeight.bold,
                      color: _getScoreColor(score),
                    ),
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Headline
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.deepPurple.shade50,
                borderRadius: BorderRadius.circular(8),
              ),
              child: Text(
                recommendation['headline'],
                style: TextStyle(
                  fontWeight: FontWeight.w500,
                  color: Colors.deepPurple.shade700,
                ),
              ),
            ),

            const SizedBox(height: 12),

            // Key info
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: [
                _buildInfoChip(Icons.star, '${practitioner['client_satisfaction_rating']?.toStringAsFixed(1) ?? 'N/A'}'),
                _buildInfoChip(Icons.work, '${practitioner['years_experience']} yrs'),
                _buildInfoChip(Icons.attach_money, '£${practitioner['hourly_rate'].toStringAsFixed(0)}'),
                if (practitioner['verification_tier'] == 'gold')
                  _buildInfoChip(Icons.verified, 'Gold', Colors.amber),
              ],
            ),

            const SizedBox(height: 12),

            // Specialties
            if ((practitioner['specialties'] as List).isNotEmpty) ...[
              const Text('Specialties:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 4,
                children: (practitioner['specialties'] as List)
                    .take(3)
                    .map((s) => Chip(
                          label: Text(s.toString(), style: const TextStyle(fontSize: 10)),
                          materialTapTargetSize: MaterialTapTargetSize.shrinkWrap,
                          padding: EdgeInsets.zero,
                          visualDensity: VisualDensity.compact,
                        ))
                    .toList(),
              ),
            ],

            const SizedBox(height: 12),

            // Match reasons
            if ((matchScore['match_reasons'] as List).isNotEmpty) ...[
              const Text('Why this match:', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 12)),
              const SizedBox(height: 4),
              ...(matchScore['match_reasons'] as List).take(3).map(
                    (reason) => Padding(
                      padding: const EdgeInsets.only(bottom: 2),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          Icon(Icons.check_circle, size: 14, color: Colors.green),
                          const SizedBox(width: 4),
                          Expanded(
                            child: Text(
                              reason.toString(),
                              style: TextStyle(fontSize: 12, color: Colors.grey[700]),
                            ),
                          ),
                        ],
                      ),
                    ),
                  ),
            ],

            const SizedBox(height: 12),

            // Cost estimate
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Est. ${recommendation['estimated_sessions_needed']} sessions',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                Text(
                  'Total: £${recommendation['estimated_total_cost']?.toStringAsFixed(0) ?? 'N/A'}',
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Book button
            SizedBox(
              width: double.infinity,
              child: ElevatedButton(
                onPressed: () {},
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.deepPurple,
                  foregroundColor: Colors.white,
                ),
                child: const Text('View Profile & Book'),
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoChip(IconData icon, String label, [Color? color]) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey.shade100,
        borderRadius: BorderRadius.circular(12),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Icon(icon, size: 14, color: color ?? Colors.grey[600]),
          const SizedBox(width: 4),
          Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[700])),
        ],
      ),
    );
  }

  Color _getScoreColor(double score) {
    if (score >= 80) return Colors.green;
    if (score >= 60) return Colors.orange;
    return Colors.red;
  }
}
