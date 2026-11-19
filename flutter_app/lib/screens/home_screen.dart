import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../widgets/status_card.dart';
import '../widgets/tile_row.dart';
import '../widgets/feed_button.dart';
import '../widgets/feed_history_chart.dart';
import 'schedule_screen.dart';
import 'alerts_screen.dart';
import 'settings_screen.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Pet Feeder'),
        centerTitle: false,
        actions: [
          if (state.alerts.any((a) => !a.resolved))
            IconButton(
              icon: Badge(
                label: Text(
                    '${state.alerts.where((a) => !a.resolved).length}'),
                child: const Icon(Icons.notifications),
              ),
              onPressed: () => Navigator.push(context,
                  MaterialPageRoute(builder: (_) => const AlertsScreen())),
            ),
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => Navigator.push(context,
                MaterialPageRoute(builder: (_) => const SettingsScreen())),
          ),
        ],
      ),
      body: RefreshIndicator(
        onRefresh: state.refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            StatusCard(
              online: state.device.online,
              connected: state.connected,
              updatedAt: state.device.updatedAt,
              error: state.error,
            ),
            const SizedBox(height: 16),
            TileRow(device: state.device),
            const SizedBox(height: 16),
            const FeedButton(),
            const SizedBox(height: 20),
            Text('Lịch sử cho ăn',
                style: theme.textTheme.titleMedium
                    ?.copyWith(fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            SizedBox(
              height: 200,
              child: FeedHistoryChart(history: state.feedHistory),
            ),
            const SizedBox(height: 20),
            _SectionHeader(
              title: 'Lịch cho ăn',
              trailing: TextButton(
                onPressed: () => Navigator.push(context,
                    MaterialPageRoute(builder: (_) => const ScheduleScreen())),
                child: const Text('Xem tất cả'),
              ),
            ),
            if (state.schedules.isEmpty)
              const Padding(
                padding: EdgeInsets.symmetric(vertical: 12),
                child: Text('Chưa có lịch', textAlign: TextAlign.center),
              )
            else
              ...state.schedules.take(3).map((s) => ListTile(
                    leading: Icon(
                      Icons.schedule,
                      color: s.enabled ? theme.colorScheme.primary : Colors.grey,
                    ),
                    title: Text(s.timeStr,
                        style: const TextStyle(
                            fontWeight: FontWeight.w700, fontSize: 20)),
                    subtitle: Text('${s.grams.toStringAsFixed(0)}g'),
                    trailing: Switch(
                      value: s.enabled,
                      onChanged: (v) =>
                          context.read<AppState>().toggleSchedule(s.id, v),
                    ),
                  )),
          ],
        ),
      ),
      bottomNavigationBar: BottomNavigationBar(
        currentIndex: 0,
        onTap: (i) {
          if (i == 1) {
            Navigator.push(context,
                MaterialPageRoute(builder: (_) => const ScheduleScreen()));
          } else if (i == 2) {
            Navigator.push(context,
                MaterialPageRoute(builder: (_) => const AlertsScreen()));
          }
        },
        items: const [
          BottomNavigationBarItem(icon: Icon(Icons.home), label: 'Trang chủ'),
          BottomNavigationBarItem(
              icon: Icon(Icons.calendar_month), label: 'Lịch'),
          BottomNavigationBarItem(
              icon: Icon(Icons.warning_amber), label: 'Cảnh báo'),
        ],
      ),
    );
  }
}

class _SectionHeader extends StatelessWidget {
  final String title;
  final Widget? trailing;
  const _SectionHeader({required this.title, this.trailing});

  @override
  Widget build(BuildContext context) {
    return Row(
      children: [
        Expanded(
          child: Text(title,
              style: Theme.of(context)
                  .textTheme
                  .titleMedium
                  ?.copyWith(fontWeight: FontWeight.w700)),
        ),
        ?trailing,
      ],
    );
  }
}
