import 'package:flutter/material.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class PractitionersScreen extends StatelessWidget {
  const PractitionersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text('Practitioners', style: SanaTextStyles.heading1),
            const SizedBox(height: 24),
            Row(
              children: [
                Expanded(child: TextField(decoration: const InputDecoration(hintText: 'Search practitioners...', prefixIcon: Icon(Icons.search)))),
                const SizedBox(width: 16),
                DropdownButton<String>(
                  value: 'All',
                  items: ['All', 'Pending', 'Verified', 'Suspended'].map((e) => DropdownMenuItem(value: e, child: Text(e))).toList(),
                  onChanged: (_) {},
                ),
              ],
            ),
            const SizedBox(height: 24),
            Expanded(
              child: Container(
                decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Name')),
                    DataColumn(label: Text('Specialty')),
                    DataColumn(label: Text('Rating')),
                    DataColumn(label: Text('Outcomes')),
                    DataColumn(label: Text('Status')),
                    DataColumn(label: Text('Actions')),
                  ],
                  rows: List.generate(8, (i) => DataRow(cells: [
                    DataCell(Text(['Dr. Emily Chen', 'Dr. Michael Park', 'Dr. Sarah Lee', 'Dr. James Wilson', 'Dr. Lisa Wang', 'Dr. David Kim', 'Dr. Anna Smith', 'Dr. Robert Brown'][i])),
                    DataCell(Text(['Acupuncture', 'Massage', 'Naturopathy', 'Chiropractic', 'Herbalist', 'Nutrition', 'Yoga', 'Acupuncture'][i])),
                    DataCell(Text(['4.9', '4.8', '4.7', '4.9', '4.6', '4.8', '4.7', '4.8'][i])),
                    DataCell(Text(['92%', '88%', '85%', '90%', '82%', '87%', '84%', '89%'][i])),
                    DataCell(_StatusBadge(status: i < 5 ? 'Verified' : i < 7 ? 'Pending' : 'Suspended')),
                    DataCell(Row(children: [
                      if (i >= 5 && i < 7) TextButton(onPressed: () {}, child: const Text('Verify')),
                      IconButton(icon: const Icon(Icons.visibility, size: 18), onPressed: () {}),
                      IconButton(icon: const Icon(Icons.more_vert, size: 18), onPressed: () {}),
                    ])),
                  ])),
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}

class _StatusBadge extends StatelessWidget {
  final String status;
  const _StatusBadge({required this.status});

  @override
  Widget build(BuildContext context) {
    Color bg, fg;
    switch (status) {
      case 'Verified': bg = SanaColors.successLight; fg = SanaColors.success; break;
      case 'Pending': bg = SanaColors.warningLight; fg = SanaColors.warning; break;
      default: bg = SanaColors.errorLight; fg = SanaColors.error;
    }
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
      decoration: BoxDecoration(color: bg, borderRadius: BorderRadius.circular(12)),
      child: Text(status, style: TextStyle(fontSize: 12, color: fg, fontWeight: FontWeight.w600)),
    );
  }
}
