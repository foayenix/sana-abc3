import 'package:flutter/material.dart';
import '../services/api_client.dart';

class PlanningTestScreen extends StatefulWidget {
  const PlanningTestScreen({super.key});

  @override
  State<PlanningTestScreen> createState() => _PlanningTestScreenState();
}

class _PlanningTestScreenState extends State<PlanningTestScreen> {
  final ApiClient _apiClient = ApiClient();

  String _profile = 'balanced';
  int _timePerDay = 60;
  double _budgetPerWeek = 50.0;

  Map<String, dynamic>? _result;
  bool _isLoading = false;
  String? _errorMessage;

  Future<void> _generatePlan() async {
    setState(() {
      _isLoading = true;
      _errorMessage = null;
      _result = null;
    });

    try {
      final result = await _apiClient.testSHAMFullFlow(
          profile: _profile,
          timePerDay: _timePerDay,
          budgetPerWeek: _budgetPerWeek);

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
        title: const Text('SHAM - Wellness Plan Generator'),
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
            _buildControlsCard(),
            const SizedBox(height: 20),
            _buildGenerateButton(),
            const SizedBox(height: 20),
            if (_isLoading) _buildLoadingIndicator(),
            if (_errorMessage != null) _buildErrorCard(),
            if (_result != null) ...[
              _buildSISMSummary(),
              const SizedBox(height: 20),
              _buildPlanSummary(),
              const SizedBox(height: 20),
              _buildWeeklySchedule(),
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
                Icon(Icons.calendar_today, color: Colors.teal),
                const SizedBox(width: 8),
                const Text(
                  'About SHAM',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
                ),
              ],
            ),
            const SizedBox(height: 12),
            const Text(
              'SHAM generates personalized wellness plans using your SISM health scores and evidence-based interventions from the Health Graph.',
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
              'Plan Parameters',
              style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 16),

            // Profile selector
            DropdownButtonFormField<String>(
              value: _profile,
              decoration: const InputDecoration(
                labelText: 'Health Profile',
                border: OutlineInputBorder(),
              ),
              items: [
                'balanced',
                'struggling',
                'thriving',
                'physical_weak',
                'emotional_weak'
              ]
                  .map((p) =>
                      DropdownMenuItem(value: p, child: Text(p.toUpperCase())))
                  .toList(),
              onChanged: (value) => setState(() => _profile = value!),
            ),

            const SizedBox(height: 16),

            // Time slider
            Text('Time Available: $_timePerDay min/day'),
            Slider(
              value: _timePerDay.toDouble(),
              min: 15,
              max: 180,
              divisions: 11,
              label: '$_timePerDay min',
              onChanged: (value) =>
                  setState(() => _timePerDay = value.toInt()),
            ),

            const SizedBox(height: 16),

            // Budget slider
            Text('Budget: £${_budgetPerWeek.toStringAsFixed(0)}/week'),
            Slider(
              value: _budgetPerWeek,
              min: 0,
              max: 200,
              divisions: 20,
              label: '£${_budgetPerWeek.toStringAsFixed(0)}',
              onChanged: (value) => setState(() => _budgetPerWeek = value),
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildGenerateButton() {
    return SizedBox(
      width: double.infinity,
      height: 48,
      child: ElevatedButton.icon(
        onPressed: _isLoading ? null : _generatePlan,
        icon: const Icon(Icons.auto_awesome),
        label: const Text('Generate Wellness Plan'),
        style: ElevatedButton.styleFrom(
          backgroundColor: Colors.teal,
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
          Text('Generating your personalized plan...'),
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

  Widget _buildSISMSummary() {
    final sism = _result!['sism_output'];
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Your Health Score',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Text(
              'Overall: ${sism['overall_score'].toStringAsFixed(1)}',
              style: const TextStyle(
                  fontSize: 24,
                  fontWeight: FontWeight.bold,
                  color: Colors.teal),
            ),
            const SizedBox(height: 8),
            if ((sism['weak_domains'] as List).isNotEmpty) ...[
              const Text('Areas for Improvement:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 4),
              Wrap(
                spacing: 8,
                children: (sism['weak_domains'] as List)
                    .map((d) => Chip(label: Text(d.toString().toUpperCase())))
                    .toList(),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildPlanSummary() {
    final plan = _result!['sham_plan'];
    final schedule = plan['weekly_schedule'];

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Plan Summary',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: [
                _buildStatBox('Activities',
                    schedule['total_activities'].toString(), Icons.fitness_center),
                _buildStatBox(
                    'Time/Week',
                    '${schedule['total_time_minutes_per_week']} min',
                    Icons.access_time),
                _buildStatBox(
                    'Cost/Week',
                    '£${schedule['total_cost_pounds_per_week'].toStringAsFixed(0)}',
                    Icons.attach_money),
              ],
            ),
            const SizedBox(height: 16),
            if ((plan['priority_interventions'] as List).isNotEmpty) ...[
              const Text('Priority Activities:',
                  style: TextStyle(fontWeight: FontWeight.bold)),
              const SizedBox(height: 8),
              ...(plan['priority_interventions'] as List).map(
                (i) => Padding(
                  padding: const EdgeInsets.only(bottom: 4),
                  child: Row(
                    children: [
                      const Icon(Icons.star, size: 16, color: Colors.amber),
                      const SizedBox(width: 8),
                      Expanded(child: Text(i.toString())),
                    ],
                  ),
                ),
              ),
            ],
          ],
        ),
      ),
    );
  }

  Widget _buildStatBox(String label, String value, IconData icon) {
    return Column(
      children: [
        Icon(icon, color: Colors.teal),
        const SizedBox(height: 4),
        Text(value,
            style: const TextStyle(fontSize: 18, fontWeight: FontWeight.bold)),
        Text(label, style: TextStyle(fontSize: 12, color: Colors.grey[600])),
      ],
    );
  }

  Widget _buildWeeklySchedule() {
    final plan = _result!['sham_plan'];
    final schedule = plan['weekly_schedule'];
    final dailySchedules = schedule['daily_schedules'] as Map<String, dynamic>;

    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              'Weekly Schedule',
              style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold),
            ),
            const SizedBox(height: 12),
            ...dailySchedules.entries.map((entry) {
              final day = entry.key;
              final daySchedule = entry.value;
              final activities = daySchedule['activities'] as List;

              if (activities.isEmpty) return const SizedBox.shrink();

              return _buildDaySchedule(day, activities);
            }),
          ],
        ),
      ),
    );
  }

  Widget _buildDaySchedule(String day, List activities) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 16),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            day.toUpperCase(),
            style: const TextStyle(
                fontSize: 16,
                fontWeight: FontWeight.bold,
                color: Colors.teal),
          ),
          const SizedBox(height: 8),
          ...activities.map((activity) => _buildActivityTile(activity)),
        ],
      ),
    );
  }

  Widget _buildActivityTile(Map<String, dynamic> activity) {
    return Container(
      margin: const EdgeInsets.only(bottom: 8),
      padding: const EdgeInsets.all(12),
      decoration: BoxDecoration(
        color: Colors.teal.shade50,
        borderRadius: BorderRadius.circular(8),
      ),
      child: Row(
        children: [
          Icon(Icons.circle, size: 8, color: Colors.teal.shade700),
          const SizedBox(width: 12),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Text(
                  activity['intervention_name'],
                  style: const TextStyle(fontWeight: FontWeight.bold),
                ),
                Text(
                  '${activity['duration_minutes']} min • ${activity['time_of_day'].toString().split('.').last}',
                  style: TextStyle(fontSize: 12, color: Colors.grey[600]),
                ),
              ],
            ),
          ),
          Chip(
            label: Text(
              activity['evidence_strength'].toString().toUpperCase(),
              style: const TextStyle(fontSize: 10),
            ),
            backgroundColor: _getEvidenceColor(activity['evidence_strength']),
          ),
        ],
      ),
    );
  }

  Color _getEvidenceColor(String strength) {
    switch (strength.toLowerCase()) {
      case 'strong':
        return Colors.green.shade200;
      case 'moderate':
        return Colors.orange.shade200;
      default:
        return Colors.grey.shade200;
    }
  }
}
