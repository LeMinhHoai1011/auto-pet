import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';

class ScheduleScreen extends StatelessWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(title: const Text('Lịch cho ăn')),
      body: state.schedules.isEmpty
          ? const Center(child: Text('Chưa có lịch'))
          : ListView.builder(
              padding: const EdgeInsets.all(16),
              itemCount: state.schedules.length,
              itemBuilder: (ctx, i) {
                final s = state.schedules[i];
                return Dismissible(
                  key: ValueKey(s.id),
                  direction: DismissDirection.endToStart,
                  background: Container(
                    alignment: Alignment.centerRight,
                    padding: const EdgeInsets.only(right: 20),
                    color: Colors.red,
                    child: const Icon(Icons.delete, color: Colors.white),
                  ),
                  confirmDismiss: (_) async {
                    return await showDialog<bool>(
                      context: ctx,
                      builder: (c) => AlertDialog(
                        title: const Text('Xóa lịch?'),
                        content: Text('Xóa lịch ${s.timeStr}?'),
                        actions: [
                          TextButton(
                              onPressed: () => Navigator.pop(c, false),
                              child: const Text('Hủy')),
                          TextButton(
                              onPressed: () => Navigator.pop(c, true),
                              child: const Text('Xóa',
                                  style: TextStyle(color: Colors.red))),
                        ],
                      ),
                    );
                  },
                  onDismissed: (_) =>
                      context.read<AppState>().removeSchedule(s.id),
                  child: Card(
                    margin: const EdgeInsets.only(bottom: 10),
                    child: ListTile(
                      leading: Icon(Icons.schedule,
                          color: s.enabled ? Colors.blue : Colors.grey,
                          size: 30),
                      title: Text(s.timeStr,
                          style: const TextStyle(
                              fontSize: 24, fontWeight: FontWeight.w700)),
                      subtitle: Text('${s.grams.toStringAsFixed(0)} grams'),
                      trailing: Switch(
                        value: s.enabled,
                        onChanged: (v) =>
                            context.read<AppState>().toggleSchedule(s.id, v),
                      ),
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAddDialog(context),
        child: const Icon(Icons.add),
      ),
    );
  }

  void _showAddDialog(BuildContext context) {
    TimeOfDay time = const TimeOfDay(hour: 7, minute: 0);
    double grams = 30;

    showDialog(
      context: context,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setDialogState) => AlertDialog(
          title: const Text('Thêm lịch'),
          content: Column(
            mainAxisSize: MainAxisSize.min,
            children: [
              ListTile(
                leading: const Icon(Icons.access_time),
                title: Text(
                    '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}',
                    style: const TextStyle(fontSize: 20)),
                onTap: () async {
                  final t = await showTimePicker(
                      context: ctx, initialTime: time);
                  if (t != null) setDialogState(() => time = t);
                },
              ),
              Row(
                children: [
                  const Text('Grams: '),
                  Expanded(
                    child: Slider(
                      value: grams,
                      min: 5,
                      max: 100,
                      divisions: 19,
                      label: '${grams.toStringAsFixed(0)}g',
                      onChanged: (v) => setDialogState(() => grams = v),
                    ),
                  ),
                  Text('${grams.toStringAsFixed(0)}g'),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(
                onPressed: () => Navigator.pop(ctx),
                child: const Text('Hủy')),
            FilledButton(
              onPressed: () {
                context
                    .read<AppState>()
                    .addSchedule(time.hour, time.minute, grams);
                Navigator.pop(ctx);
              },
              child: const Text('Thêm'),
            ),
          ],
        ),
      ),
    );
  }
}
