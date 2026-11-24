import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../theme.dart';

class ScheduleScreen extends StatelessWidget {
  const ScheduleScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(
        title: const Text('Lịch cho ăn'),
        actions: [
          IconButton(
            icon: const Icon(Icons.add_circle_outline),
            onPressed: () => _showAddDialog(context),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: state.refresh,
        child: state.schedules.isEmpty
            ? ListView(children: [
                const SizedBox(height: 120),
                Center(
                  child: Column(
                    children: [
                      Icon(Icons.schedule, size: 64, color: AppColors.fgMuted),
                      const SizedBox(height: 12),
                      const Text('Chưa có lịch cho ăn',
                          style: TextStyle(fontSize: 16, color: AppColors.fgSecondary)),
                      const SizedBox(height: 16),
                      FilledButton.icon(
                        onPressed: () => _showAddDialog(context),
                        icon: const Icon(Icons.add),
                        label: const Text('Thêm lịch'),
                      ),
                    ],
                  ),
                ),
              ])
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
                      decoration: BoxDecoration(
                        color: AppColors.red,
                        borderRadius: BorderRadius.circular(14),
                      ),
                      child: const Icon(Icons.delete, color: Colors.white),
                    ),
                    confirmDismiss: (_) async {
                      return await showDialog<bool>(
                        context: ctx,
                        builder: (c) => AlertDialog(
                          title: const Text('Xóa lịch?'),
                          content: Text('Xóa lịch ${s.timeStr}?'),
                          actions: [
                            TextButton(onPressed: () => Navigator.pop(c, false), child: const Text('Hủy')),
                            FilledButton(
                              onPressed: () => Navigator.pop(c, true),
                              style: FilledButton.styleFrom(backgroundColor: AppColors.red),
                              child: const Text('Xóa'),
                            ),
                          ],
                        ),
                      );
                    },
                    onDismissed: (_) => context.read<AppState>().removeSchedule(s.id),
                    child: Card(
                      margin: const EdgeInsets.only(bottom: 10),
                      child: Padding(
                        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                        child: Row(
                          children: [
                            Expanded(
                              child: Column(
                                crossAxisAlignment: CrossAxisAlignment.start,
                                children: [
                                  Text(s.timeStr,
                                      style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w700)),
                                  Text('${s.grams.toStringAsFixed(0)} gram',
                                      style: const TextStyle(fontSize: 14, color: AppColors.fgSecondary)),
                                ],
                              ),
                            ),
                            Switch(
                              value: s.enabled,
                              activeThumbColor: AppColors.green,
                              onChanged: (v) => context.read<AppState>().toggleSchedule(s.id, v),
                            ),
                          ],
                        ),
                      ),
                    ),
                  );
                },
              ),
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
              InkWell(
                onTap: () async {
                  final t = await showTimePicker(context: ctx, initialTime: time);
                  if (t != null) setDialogState(() => time = t);
                },
                child: Container(
                  padding: const EdgeInsets.symmetric(vertical: 16),
                  child: Row(
                    mainAxisAlignment: MainAxisAlignment.center,
                    children: [
                      const Icon(Icons.access_time, color: AppColors.green),
                      const SizedBox(width: 10),
                      Text(
                        '${time.hour.toString().padLeft(2, '0')}:${time.minute.toString().padLeft(2, '0')}',
                        style: const TextStyle(fontSize: 32, fontWeight: FontWeight.w700),
                      ),
                    ],
                  ),
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  const Text('Grams: ', style: TextStyle(fontSize: 13)),
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
                  Text('${grams.toStringAsFixed(0)}g',
                      style: const TextStyle(fontWeight: FontWeight.w600)),
                ],
              ),
            ],
          ),
          actions: [
            TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Hủy')),
            FilledButton(
              onPressed: () {
                context.read<AppState>().addSchedule(time.hour, time.minute, grams);
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
