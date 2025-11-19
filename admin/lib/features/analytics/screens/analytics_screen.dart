import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class AnalyticsScreen extends StatelessWidget {
  const AnalyticsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Analytics', style: SanaTextStyles.heading1),
                DropdownButton<String>(value: 'Last 30 days', items: ['Last 7 days', 'Last 30 days', 'Last 90 days'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(), onChanged: (_) {}),
              ],
            ),
            const SizedBox(height: 32),
            Row(
              children: [
                Expanded(child: _MetricCard(title: 'Total Bookings', value: '8,924', change: '+15.4%', isUp: true)),
                const SizedBox(width: 16),
                Expanded(child: _MetricCard(title: 'Active Users', value: '12,458', change: '+8.2%', isUp: true)),
                const SizedBox(width: 16),
                Expanded(child: _MetricCard(title: 'Conversion Rate', value: '24.8%', change: '+2.1%', isUp: true)),
                const SizedBox(width: 16),
                Expanded(child: _MetricCard(title: 'Avg Session Value', value: '\$98', change: '+5.3%', isUp: true)),
              ],
            ),
            const SizedBox(height: 32),
            Row(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Expanded(flex: 2, child: _BookingsChart()),
                const SizedBox(width: 24),
                Expanded(child: _TopPractitioners()),
              ],
            ),
            const SizedBox(height: 32),
            _SpecialtyBreakdown(),
          ],
        ),
      ),
    );
  }
}

class _MetricCard extends StatelessWidget {
  final String title, value, change;
  final bool isUp;
  const _MetricCard({required this.title, required this.value, required this.change, required this.isUp});

  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(20),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(title, style: SanaTextStyles.caption),
          const SizedBox(height: 8),
          Text(value, style: SanaTextStyles.heading2),
          const SizedBox(height: 4),
          Row(children: [
            Icon(isUp ? Icons.arrow_upward : Icons.arrow_downward, size: 14, color: isUp ? SanaColors.success : SanaColors.error),
            Text(change, style: TextStyle(fontSize: 12, color: isUp ? SanaColors.success : SanaColors.error, fontWeight: FontWeight.w600)),
          ]),
        ],
      ),
    );
  }
}

class _BookingsChart extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Bookings Over Time', style: SanaTextStyles.heading3),
          const SizedBox(height: 24),
          SizedBox(
            height: 300,
            child: BarChart(BarChartData(
              barGroups: List.generate(7, (i) => BarChartGroupData(x: i, barRods: [BarChartRodData(toY: [120, 150, 180, 160, 200, 220, 190][i].toDouble(), color: SanaColors.primaryDark, width: 20, borderRadius: BorderRadius.circular(4))])),
              borderData: FlBorderData(show: false),
              gridData: FlGridData(show: true, drawVerticalLine: false),
            )),
          ),
        ],
      ),
    );
  }
}

class _TopPractitioners extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Top Practitioners', style: SanaTextStyles.heading3),
          const SizedBox(height: 16),
          ...List.generate(5, (i) => Padding(
            padding: const EdgeInsets.symmetric(vertical: 8),
            child: Row(
              children: [
                CircleAvatar(radius: 16, backgroundColor: SanaColors.primaryLightest, child: Text('${i + 1}', style: const TextStyle(fontSize: 12, color: SanaColors.primaryDark))),
                const SizedBox(width: 12),
                Expanded(child: Text(['Dr. Emily Chen', 'Dr. Michael Park', 'Dr. James Wilson', 'Dr. Lisa Wang', 'Dr. Sarah Lee'][i], style: SanaTextStyles.bodySmall)),
                Text(['\$12.4k', '\$10.8k', '\$9.6k', '\$8.2k', '\$7.5k'][i], style: SanaTextStyles.body.copyWith(fontWeight: FontWeight.w600)),
              ],
            ),
          )),
        ],
      ),
    );
  }
}

class _SpecialtyBreakdown extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(24),
      decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text('Bookings by Specialty', style: SanaTextStyles.heading3),
          const SizedBox(height: 16),
          Row(
            children: [
              ...['Acupuncture', 'Massage', 'Naturopathy', 'Chiropractic', 'Other'].asMap().entries.map((e) => Expanded(
                child: Column(
                  children: [
                    Text([35, 28, 18, 12, 7][e.key].toString() + '%', style: SanaTextStyles.heading3.copyWith(color: [SanaColors.primaryDark, SanaColors.primaryMedium, SanaColors.primaryLight, SanaColors.accent, SanaColors.grey500][e.key])),
                    Text(e.value, style: SanaTextStyles.caption),
                  ],
                ),
              )),
            ],
          ),
        ],
      ),
    );
  }
}
