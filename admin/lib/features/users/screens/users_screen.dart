import 'package:flutter/material.dart';
import '../../../config/colors.dart';
import '../../../config/theme.dart';

class UsersScreen extends StatelessWidget {
  const UsersScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      backgroundColor: SanaColors.background,
      body: Padding(
        padding: const EdgeInsets.all(32),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text('Users', style: SanaTextStyles.heading1),
                ElevatedButton.icon(onPressed: () {}, icon: const Icon(Icons.add), label: const Text('Add User')),
              ],
            ),
            const SizedBox(height: 24),
            TextField(decoration: const InputDecoration(hintText: 'Search users...', prefixIcon: Icon(Icons.search))),
            const SizedBox(height: 24),
            Expanded(
              child: Container(
                decoration: BoxDecoration(color: SanaColors.surface, borderRadius: BorderRadius.circular(12), border: Border.all(color: SanaColors.grey200)),
                child: DataTable(
                  columns: const [
                    DataColumn(label: Text('Name')),
                    DataColumn(label: Text('Email')),
                    DataColumn(label: Text('Role')),
                    DataColumn(label: Text('Status')),
                    DataColumn(label: Text('Actions')),
                  ],
                  rows: List.generate(10, (i) => DataRow(cells: [
                    DataCell(Text(['John Doe', 'Jane Smith', 'Mike Johnson', 'Sarah Lee', 'Tom Brown', 'Lisa Wang', 'David Kim', 'Anna Chen', 'Robert Park', 'Emily Davis'][i])),
                    DataCell(Text('user${i + 1}@email.com')),
                    DataCell(Text(i < 2 ? 'Admin' : 'User')),
                    DataCell(Container(
                      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                      decoration: BoxDecoration(color: i % 3 == 0 ? SanaColors.successLight : SanaColors.grey100, borderRadius: BorderRadius.circular(12)),
                      child: Text(i % 3 == 0 ? 'Active' : 'Inactive', style: TextStyle(fontSize: 12, color: i % 3 == 0 ? SanaColors.success : SanaColors.textSecondary)),
                    )),
                    DataCell(Row(children: [
                      IconButton(icon: const Icon(Icons.edit, size: 18), onPressed: () {}),
                      IconButton(icon: const Icon(Icons.delete, size: 18), onPressed: () {}),
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
