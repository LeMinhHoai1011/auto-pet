import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/app_state.dart';

class AlertsScreen extends StatelessWidget {
  const AlertsScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(title: const Text('Cảnh báo')),
      body: state.alerts.isEmpty
          ? const Center(child: Text('Không có cảnh báo'))
          : RefreshIndicator(
              onRefresh: state.refresh,
              child: ListView.builder(
                padding: const EdgeInsets.all(16),
                itemCount: state.alerts.length,
                itemBuilder: (ctx, i) {
                  final a = state.alerts[i];
                  final color = a.alertType == 'JAM'
                      ? Colors.red
                      : a.alertType == 'LOW_FOOD'
                          ? Colors.orange
                          : Colors.amber;
                  final icon = a.alertType == 'JAM'
                      ? Icons.error
                      : a.alertType == 'LOW_FOOD'
                          ? Icons.inventory_2
                          : Icons.access_time;

                  return Card(
                    margin: const EdgeInsets.only(bottom: 10),
                    child: ListTile(
                      leading: CircleAvatar(
                        backgroundColor: color.withValues(alpha: 0.15),
                        child: Icon(icon, color: color),
                      ),
                      title: Text(a.message),
                      subtitle: Text(
                        '${a.alertType} • ${DateFormat('HH:mm dd/MM').format(a.createdAt.toLocal())}',
                        style: TextStyle(
                            fontSize: 12, color: Colors.grey.shade600),
                      ),
                      trailing: a.resolved
                          ? const Chip(
                              label: Text('Đã xử lý',
                                  style: TextStyle(fontSize: 11)),
                              backgroundColor: Color(0xFFD1FAE5),
                            )
                          : TextButton(
                              onPressed: () => context
                                  .read<AppState>()
                                  .resolveAlert(a.id),
                              child: const Text('Xử lý'),
                            ),
                    ),
                  );
                },
              ),
            ),
    );
  }
}
