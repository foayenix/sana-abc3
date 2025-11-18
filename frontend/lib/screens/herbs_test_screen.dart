import 'package:flutter/material.dart';
import '../services/api_client.dart';

class HerbsTestScreen extends StatefulWidget {
  const HerbsTestScreen({super.key});

  @override
  State<HerbsTestScreen> createState() => _HerbsTestScreenState();
}

class _HerbsTestScreenState extends State<HerbsTestScreen> {
  final ApiClient _apiClient = ApiClient();

  bool _isLoading = false;
  String _selectedView = 'all_herbs';

  List<dynamic> _herbs = [];
  List<dynamic> _rankings = [];
  List<dynamic> _synergies = [];
  Map<String, dynamic>? _comparisonData;

  String _searchQuery = '';
  String _selectedCondition = 'Anxiety';
  int _minScore = 0;

  final List<String> _conditions = [
    'Anxiety',
    'Insomnia',
    'Depression',
    'Chronic Pain',
    'Fatigue',
  ];

  @override
  void initState() {
    super.initState();
    _loadAllHerbs();
  }

  Future<void> _loadAllHerbs() async {
    setState(() => _isLoading = true);
    try {
      final result = await _apiClient.getAllHerbs();
      setState(() {
        _herbs = result['herbs'] ?? [];
      });
    } catch (e) {
      _showError('Failed to load herbs: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _searchHerbs() async {
    setState(() => _isLoading = true);
    try {
      final result = await _apiClient.searchHerbs(
        query: _searchQuery.isNotEmpty ? _searchQuery : null,
        minScore: _minScore,
      );
      setState(() {
        _herbs = result['herbs'] ?? [];
      });
    } catch (e) {
      _showError('Failed to search herbs: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadRankings() async {
    setState(() => _isLoading = true);
    try {
      final result = await _apiClient.getHerbRankings(
        condition: _selectedCondition,
        metric: 'efficacy',
      );
      setState(() {
        _rankings = result['rankings'] ?? [];
      });
    } catch (e) {
      _showError('Failed to load rankings: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  Future<void> _loadSynergies() async {
    setState(() => _isLoading = true);
    try {
      final result = await _apiClient.findHerbSynergies(minScore: 50);
      setState(() {
        _synergies = result['combinations'] ?? [];
      });
    } catch (e) {
      _showError('Failed to load synergies: $e');
    } finally {
      setState(() => _isLoading = false);
    }
  }

  void _showError(String message) {
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text(message), backgroundColor: Colors.red),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('Herb Index Test'),
        backgroundColor: Colors.green[700],
        foregroundColor: Colors.white,
      ),
      body: Column(
        children: [
          _buildViewSelector(),
          Expanded(
            child: _isLoading
                ? const Center(child: CircularProgressIndicator())
                : _buildContent(),
          ),
        ],
      ),
    );
  }

  Widget _buildViewSelector() {
    return Container(
      padding: const EdgeInsets.all(16),
      color: Colors.green[50],
      child: Column(
        children: [
          Row(
            children: [
              Expanded(
                child: DropdownButtonFormField<String>(
                  value: _selectedView,
                  decoration: const InputDecoration(
                    labelText: 'View',
                    border: OutlineInputBorder(),
                    contentPadding: EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  ),
                  items: const [
                    DropdownMenuItem(value: 'all_herbs', child: Text('All Herbs')),
                    DropdownMenuItem(value: 'search', child: Text('Search')),
                    DropdownMenuItem(value: 'rankings', child: Text('Condition Rankings')),
                    DropdownMenuItem(value: 'synergies', child: Text('Synergies')),
                  ],
                  onChanged: (value) {
                    setState(() => _selectedView = value!);
                    switch (value) {
                      case 'all_herbs':
                        _loadAllHerbs();
                        break;
                      case 'rankings':
                        _loadRankings();
                        break;
                      case 'synergies':
                        _loadSynergies();
                        break;
                    }
                  },
                ),
              ),
            ],
          ),
          if (_selectedView == 'search') ...[
            const SizedBox(height: 12),
            _buildSearchControls(),
          ],
          if (_selectedView == 'rankings') ...[
            const SizedBox(height: 12),
            _buildRankingControls(),
          ],
        ],
      ),
    );
  }

  Widget _buildSearchControls() {
    return Row(
      children: [
        Expanded(
          flex: 2,
          child: TextField(
            decoration: const InputDecoration(
              labelText: 'Search herbs',
              border: OutlineInputBorder(),
              prefixIcon: Icon(Icons.search),
            ),
            onChanged: (value) => _searchQuery = value,
          ),
        ),
        const SizedBox(width: 8),
        Expanded(
          child: TextField(
            decoration: const InputDecoration(
              labelText: 'Min Score',
              border: OutlineInputBorder(),
            ),
            keyboardType: TextInputType.number,
            onChanged: (value) => _minScore = int.tryParse(value) ?? 0,
          ),
        ),
        const SizedBox(width: 8),
        ElevatedButton(
          onPressed: _searchHerbs,
          style: ElevatedButton.styleFrom(
            backgroundColor: Colors.green[700],
            foregroundColor: Colors.white,
          ),
          child: const Text('Search'),
        ),
      ],
    );
  }

  Widget _buildRankingControls() {
    return Row(
      children: [
        Expanded(
          child: DropdownButtonFormField<String>(
            value: _selectedCondition,
            decoration: const InputDecoration(
              labelText: 'Condition',
              border: OutlineInputBorder(),
            ),
            items: _conditions.map((c) =>
              DropdownMenuItem(value: c, child: Text(c))
            ).toList(),
            onChanged: (value) {
              setState(() => _selectedCondition = value!);
              _loadRankings();
            },
          ),
        ),
      ],
    );
  }

  Widget _buildContent() {
    switch (_selectedView) {
      case 'all_herbs':
      case 'search':
        return _buildHerbsList();
      case 'rankings':
        return _buildRankingsList();
      case 'synergies':
        return _buildSynergiesList();
      default:
        return const Center(child: Text('Select a view'));
    }
  }

  Widget _buildHerbsList() {
    if (_herbs.isEmpty) {
      return const Center(child: Text('No herbs found'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _herbs.length,
      itemBuilder: (context, index) {
        final herb = _herbs[index];
        return _buildHerbCard(herb);
      },
    );
  }

  Widget _buildHerbCard(Map<String, dynamic> herb) {
    final score = herb['overall_score'] ?? 0;
    final evidenceLevel = herb['evidence_level'] ?? 'unknown';

    Color scoreColor;
    if (score >= 70) {
      scoreColor = Colors.green;
    } else if (score >= 50) {
      scoreColor = Colors.orange;
    } else {
      scoreColor = Colors.red;
    }

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text(
                        herb['herb_name'] ?? 'Unknown',
                        style: const TextStyle(
                          fontSize: 18,
                          fontWeight: FontWeight.bold,
                        ),
                      ),
                      Text(
                        herb['botanical_name'] ?? '',
                        style: TextStyle(
                          fontSize: 14,
                          fontStyle: FontStyle.italic,
                          color: Colors.grey[600],
                        ),
                      ),
                    ],
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: scoreColor.withOpacity(0.1),
                    borderRadius: BorderRadius.circular(8),
                    border: Border.all(color: scoreColor),
                  ),
                  child: Column(
                    children: [
                      Text(
                        '$score',
                        style: TextStyle(
                          fontSize: 24,
                          fontWeight: FontWeight.bold,
                          color: scoreColor,
                        ),
                      ),
                      Text(
                        'SHI Score',
                        style: TextStyle(fontSize: 10, color: scoreColor),
                      ),
                    ],
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            _buildScoreBar('Evidence', herb['evidence_volume_score'] ?? 0, 25, Colors.blue),
            _buildScoreBar('Efficacy', herb['efficacy_score'] ?? 0, 40, Colors.green),
            _buildScoreBar('Safety', herb['safety_score'] ?? 0, 20, Colors.orange),
            _buildScoreBar('Data Quality', herb['data_quality_score'] ?? 0, 15, Colors.purple),
            const SizedBox(height: 8),
            Row(
              children: [
                _buildInfoChip('Cases: ${herb['total_cases'] ?? 0}'),
                const SizedBox(width: 8),
                _buildInfoChip('Practitioners: ${herb['unique_practitioners'] ?? 0}'),
                const SizedBox(width: 8),
                _buildEvidenceLevelChip(evidenceLevel),
              ],
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildScoreBar(String label, int value, int max, Color color) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 2),
      child: Row(
        children: [
          SizedBox(
            width: 80,
            child: Text(label, style: const TextStyle(fontSize: 12)),
          ),
          Expanded(
            child: LinearProgressIndicator(
              value: value / max,
              backgroundColor: Colors.grey[200],
              valueColor: AlwaysStoppedAnimation<Color>(color),
            ),
          ),
          const SizedBox(width: 8),
          SizedBox(
            width: 40,
            child: Text(
              '$value/$max',
              style: const TextStyle(fontSize: 11),
              textAlign: TextAlign.right,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildInfoChip(String text) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: Colors.grey[100],
        borderRadius: BorderRadius.circular(4),
      ),
      child: Text(text, style: const TextStyle(fontSize: 11)),
    );
  }

  Widget _buildEvidenceLevelChip(String level) {
    Color chipColor;
    switch (level.toLowerCase()) {
      case 'very_high':
        chipColor = Colors.green[700]!;
        break;
      case 'high':
        chipColor = Colors.green;
        break;
      case 'moderate':
        chipColor = Colors.orange;
        break;
      case 'low':
        chipColor = Colors.red[300]!;
        break;
      default:
        chipColor = Colors.grey;
    }

    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(
        color: chipColor.withOpacity(0.1),
        borderRadius: BorderRadius.circular(4),
        border: Border.all(color: chipColor),
      ),
      child: Text(
        level.replaceAll('_', ' ').toUpperCase(),
        style: TextStyle(fontSize: 10, color: chipColor, fontWeight: FontWeight.bold),
      ),
    );
  }

  Widget _buildRankingsList() {
    if (_rankings.isEmpty) {
      return const Center(child: Text('No rankings found'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _rankings.length,
      itemBuilder: (context, index) {
        final ranking = _rankings[index];
        return _buildRankingCard(ranking, index + 1);
      },
    );
  }

  Widget _buildRankingCard(Map<String, dynamic> ranking, int rank) {
    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: rank <= 3 ? Colors.amber : Colors.grey[300],
          child: Text(
            '#$rank',
            style: TextStyle(
              fontWeight: FontWeight.bold,
              color: rank <= 3 ? Colors.white : Colors.black,
            ),
          ),
        ),
        title: Text(
          ranking['herb_name'] ?? 'Unknown',
          style: const TextStyle(fontWeight: FontWeight.bold),
        ),
        subtitle: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Mean Improvement: ${(ranking['mean_improvement'] ?? 0).toStringAsFixed(1)}%'),
            Text('Effect Size: ${(ranking['effect_size'] ?? 0).toStringAsFixed(2)}'),
            Text('Sample: ${ranking['sample_size'] ?? 0} cases'),
          ],
        ),
        trailing: Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: Colors.green[50],
            borderRadius: BorderRadius.circular(8),
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                '${(ranking['mean_improvement'] ?? 0).toStringAsFixed(0)}%',
                style: TextStyle(
                  fontSize: 16,
                  fontWeight: FontWeight.bold,
                  color: Colors.green[700],
                ),
              ),
              const Text('improve', style: TextStyle(fontSize: 10)),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildSynergiesList() {
    if (_synergies.isEmpty) {
      return const Center(child: Text('No synergies found'));
    }

    return ListView.builder(
      padding: const EdgeInsets.all(16),
      itemCount: _synergies.length,
      itemBuilder: (context, index) {
        final synergy = _synergies[index];
        return _buildSynergyCard(synergy);
      },
    );
  }

  Widget _buildSynergyCard(Map<String, dynamic> synergy) {
    final herbs = (synergy['herb_names'] as List?)?.join(' + ') ?? 'Unknown';
    final score = synergy['synergy_score'] ?? 0;

    return Card(
      margin: const EdgeInsets.only(bottom: 12),
      color: Colors.purple[50],
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                Expanded(
                  child: Text(
                    herbs,
                    style: const TextStyle(
                      fontSize: 16,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 8),
                  decoration: BoxDecoration(
                    color: Colors.purple,
                    borderRadius: BorderRadius.circular(8),
                  ),
                  child: Text(
                    'Synergy: $score',
                    style: const TextStyle(
                      color: Colors.white,
                      fontWeight: FontWeight.bold,
                    ),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _buildSynergyMetric(
                  'Combined',
                  '${(synergy['mean_improvement'] ?? 0).toStringAsFixed(1)}%',
                  Colors.green,
                ),
                const SizedBox(width: 16),
                _buildSynergyMetric(
                  'Expected',
                  '${(synergy['expected_improvement'] ?? 0).toStringAsFixed(1)}%',
                  Colors.grey,
                ),
                const SizedBox(width: 16),
                _buildSynergyMetric(
                  'Boost',
                  '+${(synergy['synergy_boost'] ?? 0).toStringAsFixed(1)}%',
                  Colors.purple,
                ),
              ],
            ),
            const SizedBox(height: 8),
            Text(
              'Sample: ${synergy['sample_size'] ?? 0} cases | Lift: ${(synergy['lift'] ?? 0).toStringAsFixed(2)}',
              style: TextStyle(fontSize: 12, color: Colors.grey[600]),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildSynergyMetric(String label, String value, Color color) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(
          label,
          style: TextStyle(fontSize: 11, color: Colors.grey[600]),
        ),
        Text(
          value,
          style: TextStyle(
            fontSize: 16,
            fontWeight: FontWeight.bold,
            color: color,
          ),
        ),
      ],
    );
  }
}
