import 'package:flutter/material.dart';
import '../services/api_client.dart';

class VerificationTestScreen extends StatefulWidget {
  const VerificationTestScreen({super.key});

  @override
  State<VerificationTestScreen> createState() => _VerificationTestScreenState();
}

class _VerificationTestScreenState extends State<VerificationTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _profile = 'standard';
  String _tier = 'standard';

  Map<String, dynamic>? _result;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _runVerification() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final result = await _apiClient.testVerificationFullFlow(
        profile: _profile,
        tier: _tier,
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
        title: const Text('SCVM - Credential Verification'),
        backgroundColor: Colors.indigo,
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
            _buildVerifyButton(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_result != null) ...[
              _buildOverallStatus(),
              const SizedBox(height: 20),
              _buildCredentialResults(),
              const SizedBox(height: 20),
              if (_hasIssues()) _buildIssuesCard(),
              if (_hasFraudIndicators()) ...[
                const SizedBox(height: 20),
                _buildFraudIndicators(),
              ],
              const SizedBox(height: 20),
              _buildRecommendations(),
              const SizedBox(height: 20),
              if (_hasBadges()) _buildBadges(),
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
                Icon(Icons.verified_user, color: Colors.indigo),
                const SizedBox(width: 8),
                const Text(
                  'About SCVM',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SCVM (Credential Vetting Model) provides automated verification of practitioner credentials with fraud detection, confidence scoring, and human review queue management.',
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
              'Verification Parameters',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Profile selector
            DropdownButtonFormField<String>(
              value: _profile,
              decoration: const InputDecoration(
                labelText: 'Test Profile',
                border: OutlineInputBorder(),
              ),
              items: [
                'standard',
                'suspicious',
                'expired',
                'multi_credential',
              ]
                  .map((p) => DropdownMenuItem(
                      value: p, child: Text(p.toUpperCase().replaceAll('_', ' '))))
                  .toList(),
              onChanged: (value) => setState(() => _profile = value!),
            ),

            const SizedBox(height: 16),

            // Tier selector
            DropdownButtonFormField<String>(
              value: _tier,
              decoration: const InputDecoration(
                labelText: 'Verification Tier',
                border: OutlineInputBorder(),
              ),
              items: [
                'basic',
                'standard',
                'enhanced',
                'premium',
              ]
                  .map((t) =>
                      DropdownMenuItem(value: t, child: Text(t.toUpperCase())))
                  .toList(),
              onChanged: (value) => setState(() => _tier = value!),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildVerifyButton() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _runVerification,
        icon: const Icon(Icons.security),
        label: const Text('Run Verification'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.indigo,
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
          Text('Verifying credentials...'),
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

  Widget _buildOverallStatus() {
    final verificationResult = _result!['result'];
    final status = verificationResult['overall_status'];
    final confidence = verificationResult['overall_confidence'];
    final verified = verificationResult['verified'];
    final fraudRisk = verificationResult['fraud_risk_score'];

    Color statusColor;
    IconData statusIcon;

    switch (status) {
      case 'verified':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'requires_review':
        statusColor = Colors.orange;
        statusIcon = Icons.pending;
        break;
      case 'flagged':
        statusColor = Colors.red;
        statusIcon = Icons.flag;
        break;
      case 'failed':
        statusColor = Colors.red;
        statusIcon = Icons.cancel;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help_outline;
    }

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Verification Result',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),
            Row(
              children: [
                Icon(statusIcon, size: 48, color: statusColor),
                const SizedBox(width: 16),
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        status.toString().toUpperCase().replaceAll('_', ' '),
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: statusColor,
                        ),
                      ),
                      Text(
                        verified ? 'Practitioner Verified' : 'Not Verified',
                        style: TextStyle(fontSize: 14, color: Colors.grey[600]),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 16),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildMetricBox(
                  'Confidence',
                  '${(confidence * 100).toStringAsFixed(1)}%',
                  Icons.analytics,
                  _getConfidenceColor(confidence),
                ),
                _buildMetricBox(
                  'Fraud Risk',
                  '${(fraudRisk * 100).toStringAsFixed(1)}%',
                  Icons.warning,
                  _getFraudRiskColor(fraudRisk),
                ),
                _buildMetricBox(
                  'Checks',
                  verificationResult['total_checks_performed'].toString(),
                  Icons.checklist,
                  Colors.blue,
                ),
              ],
            ),
            const SizedBox(height: 12),
            Text(
              verificationResult['summary'],
              style: TextStyle(fontSize: 14, color: Colors.grey[700]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildMetricBox(String label, String value, IconData icon, Color color) {
    return Column(
      children: [
        Icon(icon, color: color, size: 28),
        const SizedBox(height: 4),
        Text(
          value,
          style: TextStyle(
            fontSize: 18,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
        Text(
          label,
          style: TextStyle(fontSize: 12, color: Colors.grey[600]),
        ),
      ],
    );
  }

  Color _getConfidenceColor(double confidence) {
    if (confidence >= 0.8) return Colors.green;
    if (confidence >= 0.5) return Colors.orange;
    return Colors.red;
  }

  Color _getFraudRiskColor(double risk) {
    if (risk >= 0.7) return Colors.red;
    if (risk >= 0.3) return Colors.orange;
    return Colors.green;
  }

  Widget _buildCredentialResults() {
    final credResults = _result!['result']['credential_results'] as List;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Credential Verification',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...credResults.map((cred) => _buildCredentialTile(cred)),
          ],
        ),
      ),
    );
  }

  Widget _buildCredentialTile(Map<String, dynamic> cred) {
    final status = cred['status'];
    final confidence = cred['confidence'];

    Color statusColor;
    IconData statusIcon;

    switch (status) {
      case 'verified':
        statusColor = Colors.green;
        statusIcon = Icons.check_circle;
        break;
      case 'requires_review':
        statusColor = Colors.orange;
        statusIcon = Icons.pending;
        break;
      case 'flagged':
        statusColor = Colors.red;
        statusIcon = Icons.flag;
        break;
      default:
        statusColor = Colors.grey;
        statusIcon = Icons.help_outline;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 12),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: statusColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(8),
        border: Border.all(color: statusColor.withOpacity(0.3)),
      ),
      child: Row(
        children: [
          Icon(statusIcon, color: statusColor, size: 32),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  cred['credential_name'],
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  'Confidence: ${(confidence * 100).toStringAsFixed(1)}%',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
                if (cred['expiry_warning'] == true)
                  Container(
                    margin: const EdgeInsets.only(top: 4),
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: Colors.orange.shade100,
                      borderRadius: BorderRadius.circular(4),
                    ),
                    child: const Text(
                      'Expiring Soon',
                      style: TextStyle(fontSize: 10, color: Colors.orange),
                    ),
                  ),
              ],
            ),
          ),
          Chip(
            label: Text(
              status.toString().toUpperCase().replaceAll('_', ' '),
              style: TextStyle(fontSize: 10, color: statusColor),
            ),
            backgroundColor: statusColor.withOpacity(0.2),
          ),
        ],
      ),
    );
  }

  bool _hasIssues() {
    final issues = _result!['result']['issues'] as List;
    return issues.isNotEmpty;
  }

  Widget _buildIssuesCard() {
    final issues = _result!['result']['issues'] as List;

    return Card(
      color: Colors.orange.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.warning, color: Colors.orange),
                const SizedBox(width: 8),
                Text(
                  'Issues Found (${issues.length})',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...issues.map((issue) => _buildIssueTile(issue)),
          ],
        ),
      ),
    );
  }

  Widget _buildIssueTile(Map<String, dynamic> issue) {
    final severity = issue['severity'];
    Color severityColor;

    switch (severity) {
      case 'critical':
        severityColor = Colors.red.shade900;
        break;
      case 'high':
        severityColor = Colors.red;
        break;
      case 'medium':
        severityColor = Colors.orange;
        break;
      default:
        severityColor = Colors.grey;
    }

    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(8),
      decoration: BoxDecoration(
        color: Colors.white,
        borderRadius: BorderRadius.circular(4),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            children: [
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                decoration: BoxDecoration(
                  color: severityColor.withOpacity(0.2),
                  borderRadius: BorderRadius.circular(4),
                ),
                child: Text(
                  severity.toString().toUpperCase(),
                  style: TextStyle(
                    fontSize: 10,
                    fontWeight: FontWeight.bold,
                    color: severityColor,
                  ),
                ),
              ),
              const SizedBox(width: 8),
              Expanded(
                child: Text(
                  issue['issue_type'].toString().replaceAll('_', ' ').toUpperCase(),
                  style: const TextStyle(
                    fontSize: 12,
                    fontWeight: FontWeight.bold,
                  ),
                ),
              ),
            ],
          ),
          const SizedBox(height: 4),
          Text(
            issue['description'],
            style: TextStyle(fontSize: 12, color: Colors.grey[700]),
          ),
          if (issue['suggested_action'] != null &&
              issue['suggested_action'].toString().isNotEmpty) ...[
            const SizedBox(height: 4),
            Text(
              'Action: ${issue['suggested_action']}',
              style: TextStyle(fontSize: 11, color: Colors.blue[700]),
            ),
          ],
        ],
      ),
    );
  }

  bool _hasFraudIndicators() {
    final indicators = _result!['result']['fraud_indicators'] as List;
    return indicators.isNotEmpty;
  }

  Widget _buildFraudIndicators() {
    final indicators = _result!['result']['fraud_indicators'] as List;

    return Card(
      color: Colors.red.shade50,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.gpp_bad, color: Colors.red),
                const SizedBox(width: 8),
                Text(
                  'Fraud Indicators (${indicators.length})',
                  style: const TextStyle(
                    fontSize: 16,
                    fontWeight: FontWeight.bold,
                    color: Colors.red,
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...indicators.map((indicator) => Container(
                  margin: const EdgeInsets.only(bottom: 8),
                  padding: const EdgeInsets.all(8),
                  decoration: BoxDecoration(
                    color: Colors.white,
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        indicator['indicator_type']
                            .toString()
                            .replaceAll('_', ' ')
                            .toUpperCase(),
                        style: const TextStyle(
                          fontWeight: FontWeight.bold,
                          color: Colors.red,
                        ),
                      ),
                      const SizedBox(height: 4),
                      Text(
                        indicator['description'],
                        style: TextStyle(fontSize: 12, color: Colors.grey[700]),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  Widget _buildRecommendations() {
    final recommendations = _result!['result']['recommendations'] as List;

    if (recommendations.isEmpty) return const SizedBox.shrink();

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.lightbulb, color: Colors.amber),
                const SizedBox(width: 8),
                const Text(
                  'Recommendations',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            ...recommendations.map((rec) => Padding(
                  padding: const EdgeInsets.only(bottom: 8),
                  child: Row(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Icon(Icons.arrow_right, size: 20, color: Colors.grey),
                      const SizedBox(width: 8),
                      Expanded(
                        child: Text(
                          rec.toString(),
                          style: const TextStyle(fontSize: 14),
                        ),
                      ),
                    ],
                  ),
                )),
          ],
        ),
      ),
    );
  }

  bool _hasBadges() {
    final badges = _result!['result']['badges'] as List;
    return badges.isNotEmpty;
  }

  Widget _buildBadges() {
    final badges = _result!['result']['badges'] as List;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Icon(Icons.workspace_premium, color: Colors.amber),
                const SizedBox(width: 8),
                const Text(
                  'Badges Awarded',
                  style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Wrap(
              spacing: 8,
              runSpacing: 8,
              children: badges
                  .map((badge) => Chip(
                        avatar: Icon(Icons.verified, color: Colors.indigo),
                        label: Text(badge['display_text']),
                        backgroundColor: Colors.indigo.shade50,
                      ))
                  .toList(),
            ),
          ],
        ),
      ),
    );
  }
}
