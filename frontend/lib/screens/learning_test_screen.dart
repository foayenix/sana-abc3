import 'package:flutter/material.dart';
import '../services/api_client.dart';

class LearningTestScreen extends StatefulWidget {
  const LearningTestScreen({super.key});

  @override
  State<LearningTestScreen> createState() => _LearningTestScreenState();
}

class _LearningTestScreenState extends State<LearningTestScreen> {
  final ApiClient _apiClient = ApiClient();

  double _baselineScore = 45.0;
  String _weakDomain = 'emotional';
  Map<String, dynamic>? _metricsResult;
  Map<String, dynamic>? _recommendationsResult;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _loadMetrics() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
    });

    try {
      final metrics = await _apiClient.getLearningMetrics();
      setState(() {
        _metricsResult = metrics;
        _isLoading = false;
      });
    } catch (e) {
      setState(() {
        _errorMessage = e.toString();
        _isLoading = false;
      });
    }
  }

  Future<void> _testRecommendations() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _recommendationsResult = null;
    });

    try {
      final result = await _apiClient.testSOURecommendations(
        baselineScore: _baselineScore,
        weakDomain: _weakDomain,
      );
      setState(() {
        _recommendationsResult = result;
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
  void initState() {
    super.initState();
    _loadMetrics();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('SOU - Outcome Uplift'),
        backgroundColor: Colors.purple.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoCard(),
            const SizedBox(height: 20),
            if (_metricsResult != null) _buildMetricsSection(),
            const SizedBox(height: 20),
            _buildRecommendationControls(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_recommendationsResult != null) _buildRecommendationsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      color: Colors.purple.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.trending_up, color: Colors.purple.shade700),
                const SizedBox(width: 8),
                const Text(
                  'About SOU',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SOU learns from user outcomes to improve recommendations. It uses reinforcement learning to identify which interventions work best for different user profiles.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.purple.shade100,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                children: [
                  Icon(Icons.auto_graph, size: 16, color: Colors.purple.shade900),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      'Competitive moat - system gets smarter with every user',
                      style: TextStyle(fontSize: 12, fontWeight: FontWeight.bold),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricsSection() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Learning Metrics',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildMetricRow(
              'Learning Phase',
              _metricsResult!['learning_phase'].toString().toUpperCase(),
              _getPhaseColor(_metricsResult!['learning_phase']),
            ),
            _buildMetricRow(
              'Total Outcomes',
              _metricsResult!['total_outcome_records'].toString(),
              Colors.blue,
            ),
            _buildMetricRow(
              'Exploration Rate',
              '${(_metricsResult!['exploration_rate'] * 100).toStringAsFixed(0)}%',
              Colors.orange,
            ),
            _buildMetricRow(
              'Avg Improvement',
              '${(_metricsResult!['average_improvement_with_sou'] as num).toStringAsFixed(1)}%',
              Colors.green,
            ),
            _buildMetricRow(
              'Uplift vs Baseline',
              '+${(_metricsResult!['uplift_percentage'] as num).toStringAsFixed(1)}%',
              Colors.purple,
            ),
            const Divider(),
            _buildMetricRow(
              'Model R²',
              (_metricsResult!['model_r2'] as num).toStringAsFixed(2),
              Colors.teal,
            ),
            _buildMetricRow(
              'Prediction Accuracy',
              '${((_metricsResult!['prediction_accuracy_within_10pct'] as num) * 100).toStringAsFixed(0)}%',
              Colors.indigo,
            ),
          ],
        ),
      ),
    );
  }

  Color _getPhaseColor(String phase) {
    switch (phase) {
      case 'cold_start':
        return Colors.orange;
      case 'early_learning':
        return Colors.blue;
      case 'mature':
        return Colors.green;
      default:
        return Colors.grey;
    }
  }

  Widget _buildMetricRow(String label, String value, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 4),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label),
          Container(
            padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
            decoration: BoxDecoration(
              color: color.withOpacity(0.1),
              borderRadius: BorderRadius.circular(4),
            ),
            child: Text(
              value,
              style: TextStyle(fontWeight: FontWeight.bold, color: color),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildRecommendationControls() {
    final domains = ['emotional', 'physical', 'social', 'cognitive', 'spiritual'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Test Recommendations',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Text('Baseline Score: ${_baselineScore.toStringAsFixed(0)}'),
            Slider(
              value: _baselineScore,
              min: 20,
              max: 80,
              divisions: 12,
              label: _baselineScore.toStringAsFixed(0),
              onChanged: (value) => setState(() => _baselineScore = value),
            ),
            const SizedBox(height: 8),
            DropdownButtonFormField<String>(
              value: _weakDomain,
              decoration: const InputDecoration(
                labelText: 'Weak Domain',
                border: OutlineInputBorder(),
              ),
              items: domains
                  .map((d) => DropdownMenuItem(
                        value: d,
                        child: Text(d.substring(0, 1).toUpperCase() + d.substring(1)),
                      ))
                  .toList(),
              onChanged: (value) => setState(() => _weakDomain = value!),
            ),
            const SizedBox(height: 16),
            SizedBox(
              width: double.infinity,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _testRecommendations,
                icon: const Icon(Icons.psychology),
                label: const Text('Get SOU Recommendations'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.purple.shade700,
                  foregroundColor: Colors.white,
                ),
              ),
            ),
          ],
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
          Text('Analyzing outcomes and generating recommendations...'),
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
            Expanded(child: Text(_errorMessage!)),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendationsSection() {
    final souOutput = _recommendationsResult!['sou_recommendations'];
    final explanation = _recommendationsResult!['explanation'];

    return Column(
      children: [
        _buildUpliftCard(souOutput, explanation),
        const SizedBox(height: 16),
        _buildRecommendationsCard(souOutput),
      ],
    );
  }

  Widget _buildUpliftCard(Map<String, dynamic> souOutput, String explanation) {
    final uplift = (souOutput['uplift'] as num).toDouble();

    return Card(
      color: Colors.green.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.trending_up, color: Colors.green.shade700),
                const SizedBox(width: 8),
                const Text(
                  'SOU Advantage',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              '+${uplift.toStringAsFixed(1)}% uplift',
              style: TextStyle(
                fontSize: 32,
                fontWeight: FontWeight.bold,
                color: Colors.green.shade700,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              explanation,
              style: const TextStyle(fontSize: 13),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildComparisonColumn(
                  'With SOU',
                  '${(souOutput['expected_improvement_with_sou'] as num).toStringAsFixed(1)}%',
                  Colors.green,
                ),
                _buildComparisonColumn(
                  'Baseline',
                  '${(souOutput['expected_improvement_baseline'] as num).toStringAsFixed(1)}%',
                  Colors.grey,
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildComparisonColumn(String label, String value, Color color) {
    return Column(
      children: [
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
        Text(
          value,
          style: TextStyle(
            fontSize: 20,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }

  Widget _buildRecommendationsCard(Map<String, dynamic> souOutput) {
    final recommendations = souOutput['recommendations'] as List;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                const Text(
                  'Outcome-Optimized Recommendations',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                  decoration: BoxDecoration(
                    color: _getConfidenceColor(souOutput['prediction_confidence']),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Text(
                    souOutput['prediction_confidence'].toString().toUpperCase(),
                    style: const TextStyle(color: Colors.white, fontSize: 10),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...recommendations.asMap().entries.map(
                  (entry) => _buildRecommendationTile(entry.key + 1, entry.value),
                ),
          ],
        ),
      ),
    );
  }

  Color _getConfidenceColor(String confidence) {
    switch (confidence) {
      case 'high':
        return Colors.green;
      case 'medium':
        return Colors.orange;
      case 'low':
        return Colors.red;
      default:
        return Colors.grey;
    }
  }

  Widget _buildRecommendationTile(int rank, Map<String, dynamic> rec) {
    final isExploration = rec['is_exploration'] as bool;
    final prediction = rec['predicted_outcome'];

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: isExploration ? Colors.orange.shade50 : Colors.purple.shade50,
        borderRadius: BorderRadius.circular(8),
        border: Border.all(
          color: isExploration ? Colors.orange : Colors.purple.shade200,
        ),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              CircleAvatar(
                radius: 12,
                backgroundColor: isExploration ? Colors.orange : Colors.purple,
                child: Text(
                  '#$rank',
                  style: const TextStyle(fontSize: 10, color: Colors.white),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  rec['intervention_name'],
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
              ),
              if (isExploration)
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: Colors.orange,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: const Text(
                    'EXPLORE',
                    style: TextStyle(fontSize: 8, color: Colors.white),
                  ),
                ),
            ],
          ),
          const SizedBox(height: 8),
          Row(
            children: [
              _buildPredictionChip(
                'Predicted',
                '+${(prediction['predicted_improvement'] as num).toStringAsFixed(1)}%',
                Colors.green,
              ),
              const SizedBox(width: 8),
              _buildPredictionChip(
                'Confidence',
                '${(prediction['confidence'] as num).toStringAsFixed(0)}%',
                Colors.blue,
              ),
              const SizedBox(width: 8),
              _buildPredictionChip(
                'Success',
                '${(rec['success_rate'] as num).toStringAsFixed(0)}%',
                Colors.teal,
              ),
            ],
          ),
          const SizedBox(height: 8),
          Text(
            rec['why_recommended'],
            style: TextStyle(fontSize: 12, color: Colors.grey[700]),
          ),
        ],
      ),
    );
  }

  Widget _buildPredictionChip(String label, String value, Color color) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
      decoration: BoxDecoration(
        color: color.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        children: [
          Text(label, style: TextStyle(fontSize: 8, color: Colors.grey[600])),
          Text(
            value,
            style: TextStyle(fontSize: 11, fontWeight: FontWeight.bold, color: color),
          ),
        ],
      ),
    );
  }
}
