import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class DashboardScreen extends StatelessWidget {
  const DashboardScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Dashboard', style: SanaTextStyles.heading1),
            const SizedBox(height: 8),
            Text('Welcome back, Admin', style: SanaTextStyles.subtitle),
            const SizedBox(height: 32),

            // Stats Cards
            Row(
              children: [
                _StatCard(title: 'Total Users', value: '12,458', change: '+8.2%', icon: Icons.people, color: SanaColors.primaryDark),
                const SizedBox(width: 24),
                _StatCard(title: 'Practitioners', value: '342', change: '+12', icon: Icons.verified_user, color: SanaColors.primaryMedium),
                const SizedBox(width: 24),
                _StatCard(title: 'Sessions', value: '8,924', change: '+15.4%', icon: Icons.calendar_today, color: SanaColors.success),
                const SizedBox(width: 24),
                _StatCard(title: 'Revenue', value: '\$284,500', change: '+22.1%', icon: Icons.attach_money, color: SanaColors.accent),
              ],
            ),
            const SizedBox(height: 32),

            // Charts
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 2, child: _RevenueChart()),
                const SizedBox(width: 24),
                Expanded(child: _PendingVerifications()),
              ],
            ),
            const SizedBox(height: 32),

            // Recent Activity
            _RecentActivity(),
          ],
        ),
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String title, value, change;
  final IconData icon;
  final Color color;

  const _StatCard({required this.title, required this.value, required this.change, required this.icon, required this.color});

  @override
  Widget build(BuildContext context) {
    return Expanded(
      child: Container(
        padding: const EdgeInsets.all(24),
        decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(title, style: SanaTextStyles.bodySmall),
                Icon(icon, color: color, size: 20),
              ],
            ),
            const SizedBox(height: 12),
            Text(value, style: SanaTextStyles.heading2),
            const SizedBox(height: 4),
            Text(change, style: TextStyle(fontSize: 12, color: SanaColors.success, fontWeight: FontWeight.w600)),
          ],
        ),
      ),
    );
  }
}

class _RevenueChart extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Revenue Overview', style: SanaTextStyles.heading3),
          const SizedBox(height: 24),
          SizedBox(
            height: 300,
            child: LineChart(
              LineChartData(
                gridData: FlGridData(show: true, drawVerticalLine: false),
                titlesData: FlTitlesData(rightTitles: AxisTitles(), topTitles: AxisTitles()),
                borderData: FlBorderData(show: false),
                lineBarsData: [
                  LineChartBarData(
                    spots: const [FlSpot(0, 20), FlSpot(1, 35), FlSpot(2, 28), FlSpot(3, 45), FlSpot(4, 42), FlSpot(5, 55), FlSpot(6, 60)],
                    isCurved: true,
                    color: SanaColors.primaryDark,
                    barWidth: 3,
                    dotData: FlDotData(show: false),
                    belowBarData: BarAreaData(show: true, color: SanaColors.primaryDark.withOpacity(0.1)),
                  ),
                ],
              ),
            ),
          ),
        ],
      ),
    );
  }
}

class _PendingVerifications extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text('Pending Verifications', style: SanaTextStyles.heading3),
              Container(
                padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                decoration: BoxDecoration(color: SanaColors.warningLight, borderRadius: BorderRadius.circular(12)),
                child: const Text('5', style: TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: SanaColors.warning)),
              ),
            ],
          ),
          const SizedBox(height: 16),
          ...List.generate(5, (i) => _VerificationItem(name: ['Dr. Sarah Lee', 'Dr. James Park', 'Dr. Maria Garcia', 'Dr. Robert Kim', 'Dr. Linda Chen'][i])),
        ],
      ),
    );
  }
}

class _VerificationItem extends StatelessWidget {
  final String name;
  const _VerificationItem({required this.name});

  @override
  Widget build(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 8),
      child: Row(
        children: [
          CircleAvatar(radius: 16, backgroundColor: SanaColors.primaryLightest, child: Text(name[4], style: const TextStyle(fontSize: 12, color: SanaColors.primaryDark))),
          const SizedBox(width: 12),
          Expanded(child: Text(name, style: SanaTextStyles.bodySmall)),
          TextButton(onPressed: () {}, child: const Text('Review', style: TextStyle(fontSize: 12))),
        ],
      ),
    );
  }
}

class _RecentActivity extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Recent Activity', style: SanaTextStyles.heading3),
          const SizedBox(height: 16),
          ...['New user registered: john.doe@email.com', 'Practitioner verified: Dr. Emily Chen', 'Payout processed: \$1,200 to Dr. Park', 'New booking: Sarah J. with Dr. Wilson', 'Support ticket resolved #1234']
              .map((text) => Padding(
                    padding: const EdgeInsets.symmetric(vertical: 8),
                    child: Row(
                      children: [
                        Container(width: 8, height: 8, decoration: const BoxDecoration(color: SanaColors.primaryMedium, shape: BoxShape.circle)),
                        const SizedBox(width: 12),
                        Expanded(child: Text(text, style: SanaTextStyles.bodySmall)),
                        Text('2m ago', style: SanaTextStyles.caption),
                      ],
                    ),
                  )),
        ],
      ),
    );
  }
}
