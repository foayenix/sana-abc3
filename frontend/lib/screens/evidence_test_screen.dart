import 'package:flutter/material.dart';
import '../services/api_client.dart';

class EvidenceTestScreen extends StatefulWidget {
  const EvidenceTestScreen({super.key});

  @override
  State<EvidenceTestScreen> createState() => _EvidenceTestScreenState();
}

class _EvidenceTestScreenState extends State<EvidenceTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _searchType = 'domain';
  String _searchValue = 'emotional';
  String _minEvidence = 'weak';

  List<dynamic>? _results;
  Map<String, dynamic>? _statistics;
  bool _isLoading = false;
  String? _errorMessage;

  @override
  void initState() {
    super.initState();
    _loadStatistics();
  }

  Future<void> _loadStatistics() async {
    try {
      final stats = await _apiClient.getGraphStatistics();
      setState(() {
        _statistics = stats;
      });
    } catch (e) {
      // Handle error silently for statistics
    }
  }

  Future<void> _search() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _results = null;
    });

    try {
      List<dynamic> results;

      if (_searchType == 'domain') {
        results = await _apiClient.searchInterventionsByDomain(
            _searchValue,
            minEvidence: _minEvidence);
      } else {
        results = await _apiClient.searchInterventionsByCondition(
            _searchValue,
            minEvidence: _minEvidence);
      }

      setState(() {
        _results = results;
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
        title: const Text('SANA Health Graph'),
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
            if (_statistics != null) _buildStatisticsCard(),
            const SizedBox(height: 20),
            _buildSearchControls(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_results != null) _buildResultsSection(),
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
                Icon(Icons.account_tree, color: Colors.teal),
                const SizedBox(width: 8),
                const Text(
                  'About Health Graph',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'The SANA Health Graph is a knowledge base linking wellness domains, conditions, and evidence-based CAM interventions.',
              style: TextStyle(fontSize: 14),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildStatisticsCard() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Graph Statistics',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text('Total Interventions: ${_statistics!['total_interventions']}'),
            Text(
                'Conditions Covered: ${_statistics!['total_conditions_covered']}'),
          ],
        ),
      ),
    );
  }

  Widget _buildSearchControls() {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Search Interventions',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Search type selector
            Row(
              children: [
                Expanded(
                  child: RadioListTile<String>(
                    title: const Text('By Domain'),
                    value: 'domain',
                    groupValue: _searchType,
                    onChanged: (value) {
                      setState(() {
                        _searchType = value!;
                        _searchValue = 'emotional';
                      });
                    },
                  ),
                ),
                Expanded(
                  child: RadioListTile<String>(
                    title: const Text('By Condition'),
                    value: 'condition',
                    groupValue: _searchType,
                    onChanged: (value) {
                      setState(() {
                        _searchType = value!;
                        _searchValue = 'anxiety';
                      });
                    },
                  ),
                ),
              ],
            ),

            const SizedBox(height: 12),

            // Search value input
            if (_searchType == 'domain')
              DropdownButtonFormField<String>(
                value: _searchValue,
                decoration: const InputDecoration(
                  labelText: 'Select Domain',
                  border: OutlineInputBorder(),
                ),
                items: [
                  'physical',
                  'emotional',
                  'social',
                  'cognitive',
                  'spiritual'
                ]
                    .map((domain) => DropdownMenuItem(
                          value: domain,
                          child: Text(domain.toUpperCase()),
                        ))
                    .toList(),
                onChanged: (value) {
                  setState(() {
                    _searchValue = value!;
                  });
                },
              )
            else
              TextFormField(
                initialValue: _searchValue,
                decoration: const InputDecoration(
                  labelText: 'Condition (e.g., anxiety, insomnia)',
                  border: OutlineInputBorder(),
                ),
                onChanged: (value) {
                  _searchValue = value;
                },
              ),

            const SizedBox(height: 12),

            // Evidence strength selector
            DropdownButtonFormField<String>(
              value: _minEvidence,
              decoration: const InputDecoration(
                labelText: 'Minimum Evidence Strength',
                border: OutlineInputBorder(),
              ),
              items: ['strong', 'moderate', 'weak', 'insufficient']
                  .map((evidence) => DropdownMenuItem(
                        value: evidence,
                        child: Text(evidence.toUpperCase()),
                      ))
                  .toList(),
              onChanged: (value) {
                setState(() {
                  _minEvidence = value!;
                });
              },
            ),

            const SizedBox(height: 16),

            SizedBox(
              width: double.infinity,
              height: 48,
              child: ElevatedButton.icon(
                onPressed: _isLoading ? null : _search,
                icon: const Icon(Icons.search),
                label: const Text('Search'),
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.teal,
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
    return const Center(child: CircularProgressIndicator());
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

  Widget _buildResultsSection() {
    if (_results!.isEmpty) {
      return const Card(
        child: Padding(
          padding: EdgeInsets.all(16.0),
          child: Text('No interventions found matching your criteria.'),
        ),
      );
    }

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          'Found ${_results!.length} Intervention(s)',
          style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
        ),
        const SizedBox(height: 12),
        ..._results!
            .map((intervention) => _buildInterventionCard(intervention))
            .toList(),
      ],
    );
  }

  Widget _buildInterventionCard(Map<String, dynamic> intervention) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ExpansionTile(
        title: Text(
          intervention['name'],
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Text(intervention['category'].toString().toUpperCase()),
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(intervention['description']),
                const SizedBox(height: 12),
                _buildEvidenceBadge(intervention['evidence_strength']),
                const SizedBox(height: 12),
                Text(
                    'Target Domains: ${(intervention['target_domains'] as List).join(', ')}'),
                const SizedBox(height: 8),
                Text(
                    'Target Conditions: ${(intervention['target_conditions'] as List).join(', ')}'),
                if (intervention['contraindications'] != null &&
                    (intervention['contraindications'] as List).isNotEmpty) ...[
                  const SizedBox(height: 12),
                  Row(
                    children: [
                      Icon(Icons.warning, color: Colors.orange, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Contraindications',
                        style: TextStyle(fontWeight: FontWeight.bold),
                      ),
                    ],
                  ),
                  const SizedBox(height: 4),
                  Text(
                    '${(intervention['contraindications'] as List).length} warning(s)',
                    style: TextStyle(color: Colors.grey[600]),
                  ),
                ],
                if (intervention['requires_practitioner'] == true) ...[
                  const SizedBox(height: 8),
                  Row(
                    children: [
                      Icon(Icons.person, color: Colors.blue, size: 20),
                      const SizedBox(width: 8),
                      const Text(
                        'Requires Practitioner',
                        style: TextStyle(color: Colors.blue),
                      ),
                    ],
                  ),
                ],
              ],
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildEvidenceBadge(String evidenceStrength) {
    Color color;
    switch (evidenceStrength.toLowerCase()) {
      case 'strong':
        color = Colors.green;
        break;
      case 'moderate':
        color = Colors.orange;
        break;
      default:
        color = Colors.grey;
    }

    return Chip(
      label: Text(
        'Evidence: ${evidenceStrength.toUpperCase()}',
        style: const TextStyle(color: Colors.white),
      ),
      backgroundColor: color,
    );
  }
}
