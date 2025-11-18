import 'package:flutter/material.dart';
import '../services/api_client.dart';

class SafetyTestScreen extends StatefulWidget {
  const SafetyTestScreen({super.key});

  @override
  State<SafetyTestScreen> createState() => _SafetyTestScreenState();
}

class _SafetyTestScreenState extends State<SafetyTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _scenario = 'safe';
  Map<String, dynamic>? _result;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _runTest() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final result = await _apiClient.testSafetyScenario(scenario: _scenario);
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
        title: const Text('SST - Safety & Triage'),
        backgroundColor: Colors.red.shade700,
        foregroundColor: Colors.white,
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            _buildInfoCard(),
            const SizedBox(height: 20),
            _buildScenarioSelector(),
            const SizedBox(height: 20),
            _buildTestButton(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_result != null) _buildResultsSection(),
          ],
        ),
      ),
    );
  }

  Widget _buildInfoCard() {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.health_and_safety, color: Colors.red.shade700),
                const SizedBox(width: 8),
                const Text(
                  'About SST',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SST monitors user safety and detects health crises through score analysis, keyword detection, and pattern recognition.',
              style: TextStyle(fontSize: 14),
            ),
            const SizedBox(height: 8),
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                color: Colors.red.shade100,
                borderRadius: BorderRadius.circular(4),
              ),
              child: Row(
                children: [
                  Icon(Icons.warning, size: 16, color: Colors.red.shade900),
                  const SizedBox(width: 8),
                  const Expanded(
                    child: Text(
                      'Critical safety system - prevents harm to vulnerable users',
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

  Widget _buildScenarioSelector() {
    final scenarios = {
      'safe': 'Safe - Healthy user',
      'declining': 'Declining - Rapid deterioration',
      'chronic_low': 'Chronic Low - Long-term low scores',
      'crisis_keywords': 'Crisis Keywords - Concerning language',
      'urgent': 'Urgent - Multiple critical indicators',
    };

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Test Scenario',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            DropdownButtonFormField<String>(
              value: _scenario,
              decoration: const InputDecoration(
                border: OutlineInputBorder(),
              ),
              items: scenarios.entries
                  .map((e) => DropdownMenuItem(
                        value: e.key,
                        child: Text(e.value),
                      ))
                  .toList(),
              onChanged: (value) => setState(() => _scenario = value!),
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
        icon: const Icon(Icons.security),
        label: const Text('Run Safety Analysis'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.red.shade700,
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
          Text('Analyzing safety...'),
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

  Widget _buildResultsSection() {
    final safetyAnalysis = _result!['safety_analysis'];

    return Column(
      children: [
        _buildStatusCard(safetyAnalysis),
        const SizedBox(height: 16),
        _buildRiskCard(safetyAnalysis),
        const SizedBox(height: 16),
        if ((safetyAnalysis['risk_indicators'] as List).isNotEmpty)
          _buildIndicatorsCard(safetyAnalysis),
        if ((safetyAnalysis['risk_indicators'] as List).isNotEmpty)
          const SizedBox(height: 16),
        if (safetyAnalysis['requires_human_review'] == true)
          _buildReviewCard(safetyAnalysis),
        if (safetyAnalysis['requires_human_review'] == true)
          const SizedBox(height: 16),
        if ((safetyAnalysis['resources_to_provide'] as List).isNotEmpty)
          _buildResourcesCard(safetyAnalysis),
      ],
    );
  }

  Widget _buildStatusCard(Map<String, dynamic> analysis) {
    final status = analysis['safety_status'];

    Color statusColor;
    IconData statusIcon;
    String statusText;

    switch (status) {
      case 'safe':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        statusText = 'SAFE';
        break;
      case 'monitor':
        statusColor = Colors.orange;
        statusIcon = Icons.visibility;
        statusText = 'MONITOR';
        break;
      case 'escalate':
        statusColor = Colors.red;
        statusIcon = Icons.arrow_upward;
        statusText = 'ESCALATE';
        break;
      case 'urgent':
        statusColor = Colors.red.shade900;
        statusIcon = Icons.emergency;
        statusText = 'URGENT';
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help;
        statusText = 'UNKNOWN';
    }

    return Card(
      color: statusColor.withOpacity(0.1),
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Icon(statusIcon, size: 64, color: statusColor),
            const SizedBox(height: 12),
            Text(
              statusText,
              style: TextStyle(
                fontSize: 24,
                fontWeight: FontWeight.bold,
                color: statusColor,
              ),
            ),
            if (analysis['user_message'] != null) ...[
              const SizedBox(height: 12),
              Container(
                padding: const EdgeInsets.all(12),
                decoration: BoxDecoration(
                  color: statusColor.withOpacity(0.1),
                  border: Border.all(color: statusColor),
                  borderRadius: BorderRadius.circular(8),
                ),
                child: Text(
                  analysis['user_message'],
                  style: const TextStyle(fontSize: 13),
                  textAlign: TextAlign.center,
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildRiskCard(Map<String, dynamic> analysis) {
    final riskScore = (analysis['risk_score'] as num).toDouble();
    final trend = analysis['score_trend'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Risk Assessment',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            _buildRiskBar(riskScore),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Trend: ${trend.toString().replaceAll('_', ' ').toUpperCase()}'),
                if (analysis['trend_percentage'] != null)
                  Text('${analysis['trend_percentage']}%'),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Confidence: ${(analysis['confidence'] as num).toStringAsFixed(0)}%',
              style: TextStyle(color: Colors.grey[600], fontSize: 12),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildRiskBar(double riskScore) {
    Color color;
    if (riskScore >= 85) {
      color = Colors.red.shade900;
    } else if (riskScore >= 60) {
      color = Colors.red;
    } else if (riskScore >= 30) {
      color = Colors.orange;
    } else {
      color = Colors.green;
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Row(
          mainAxisAlignment: MainAxisAlignment.spaceBetween,
          children: [
            const Text('Risk Score',
                style: TextStyle(fontWeight: FontWeight.bold)),
            Text(riskScore.toStringAsFixed(1),
                style: TextStyle(fontWeight: FontWeight.bold, color: color)),
          ],
        ),
        const SizedBox(height: 4),
        LinearProgressIndicator(
          value: riskScore / 100,
          backgroundColor: Colors.grey.shade200,
          valueColor: AlwaysStoppedAnimation<Color>(color),
          minHeight: 12,
        ),
      ],
    );
  }

  Widget _buildIndicatorsCard(Map<String, dynamic> analysis) {
    final indicators = analysis['risk_indicators'] as List;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                const SizedBox(width: 8),
                const Text(
                  'Risk Indicators',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...indicators.map((ind) => _buildIndicatorTile(ind)),
          ],
        ),
      ),
    );
  }

  Widget _buildIndicatorTile(Map<String, dynamic> indicator) {
    final severity = indicator['severity'] as int;
    Color severityColor = severity >= 8
        ? Colors.red
        : severity >= 6
            ? Colors.orange
            : Colors.yellow.shade700;

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: severityColor.withOpacity(0.1),
        border: Border(left: BorderSide(width: 4, color: severityColor)),
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                decoration: BoxDecoration(
                  color: severityColor,
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  'Severity: $severity/10',
                  style: const TextStyle(fontSize: 10, color: Colors.white),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  indicator['risk_category']
                      .toString()
                      .replaceAll('_', ' ')
                      .toUpperCase(),
                  style: const TextStyle(
                      fontWeight: FontWeight.bold, fontSize: 11),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            indicator['description'],
            style: const TextStyle(fontSize: 13),
          ),
        ],
      ),
    );
  }

  Widget _buildReviewCard(Map<String, dynamic> analysis) {
    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.person, color: Colors.red.shade700),
                const SizedBox(width: 8),
                const Text(
                  'Human Review Required',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(analysis['recommended_action']),
            const SizedBox(height: 8),
            Text(
              'Escalation: ${analysis['escalation_pathway'].toString().replaceAll('_', ' ').toUpperCase()}',
              style: const TextStyle(fontWeight: FontWeight.bold),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildResourcesCard(Map<String, dynamic> analysis) {
    final resources = analysis['resources_to_provide'] as List;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Support Resources',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...resources.map((res) => _buildResourceTile(res)),
          ],
        ),
      ),
    );
  }

  Widget _buildResourceTile(Map<String, dynamic> resource) {
    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.blue.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            resource['name'],
            style: const TextStyle(fontWeight: FontWeight.bold, fontSize: 15),
          ),
          const SizedBox(height: 4),
          Text(resource['description'], style: const TextStyle(fontSize: 13)),
          const SizedBox(height: 4),
          Text(
            resource['contact_details'],
            style: const TextStyle(
                fontSize: 13,
                fontWeight: FontWeight.bold,
                color: Colors.blue),
          ),
          Text(
            'Available: ${resource['availability']}',
            style: TextStyle(fontSize: 11, color: Colors.grey[600]),
          ),
        ],
      ),
    );
  }
}
