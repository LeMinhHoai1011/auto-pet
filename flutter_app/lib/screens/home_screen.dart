import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../theme.dart';
import '../widgets/feed_button.dart';

class HomeScreen extends StatelessWidget {
  const HomeScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();
    final d = state.device;

    return Scaffold(
      body: SafeArea(
        child: RefreshIndicator(
          onRefresh: state.refresh,
          child: ListView(
            padding: const EdgeInsets.all(16),
            children: [
              // Header
              Row(
                children: [
                  Expanded(
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        const Text('Pet Auto',
                            style: TextStyle(fontSize: 26, fontWeight: FontWeight.w700)),
                        Text(_greeting(),
                            style: const TextStyle(fontSize: 14, color: AppColors.fgSecondary)),
                      ],
                    ),
                  ),
                  _StatusBadge(online: d.online, connected: state.connected),
                ],
              ),
              const SizedBox(height: 16),

              // Device card
              Container(
                padding: const EdgeInsets.all(18),
                decoration: BoxDecoration(
                  gradient: const LinearGradient(
                    colors: [Color(0xFF1E293B), Color(0xFF334155)],
                    begin: Alignment.topLeft,
                    end: Alignment.bottomRight,
                  ),
                  borderRadius: BorderRadius.circular(16),
                ),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    const Text('Máy cho ăn #01',
                        style: TextStyle(color: Colors.white70, fontSize: 13, fontWeight: FontWeight.w600)),
                    const SizedBox(height: 8),
                    Row(
                      crossAxisAlignment: CrossAxisAlignment.end,
                      children: [
                        Expanded(
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text('${d.bowlGrams.toStringAsFixed(0)} g',
                                  style: const TextStyle(color: Colors.white, fontSize: 36, fontWeight: FontWeight.w700)),
                              const Text('Thức ăn trong bát',
                                  style: TextStyle(color: Colors.white60, fontSize: 12)),
                            ],
                          ),
                        ),
                        Text('Phễu còn: ${d.hopperPct}%',
                            style: const TextStyle(color: Colors.white70, fontSize: 14, fontWeight: FontWeight.w600)),
                      ],
                    ),
                  ],
                ),
              ),
              const SizedBox(height: 14),

              // Feed button
              const FeedButton(),
              const SizedBox(height: 20),

              // Today stats
              const Text('Hôm nay',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              const SizedBox(height: 10),
              Row(
                children: [
                  Expanded(child: _StatCard(
                    label: 'Đã xả',
                    value: '${_todayGrams(state)} g',
                    sub: '${_todayFeeds(state)} lần',
                  )),
                  const SizedBox(width: 10),
                  Expanded(child: _StatCard(
                    label: 'Lần tiếp',
                    value: _nextSchedule(state),
                    sub: _nextScheduleGrams(state),
                  )),
                ],
              ),
              const SizedBox(height: 20),

              // Latest recognition
              if (state.latestRecognition != null) ...[
                _RecognitionCard(log: state.latestRecognition!),
                const SizedBox(height: 10),
              ],
            ],
          ),
        ),
      ),
    );
  }

  String _greeting() {
    final h = DateTime.now().hour;
    if (h < 12) return 'Chào buổi sáng!';
    if (h < 18) return 'Chào buổi chiều!';
    return 'Chào buổi tối!';
  }

  int _todayGrams(AppState s) {
    final today = DateTime.now();
    return s.feedHistory
        .where((f) => f.createdAt.day == today.day && f.createdAt.month == today.month && f.result == 'OK')
        .fold(0, (sum, f) => sum + f.actualGrams.round());
  }

  int _todayFeeds(AppState s) {
    final today = DateTime.now();
    return s.feedHistory
        .where((f) => f.createdAt.day == today.day && f.createdAt.month == today.month && f.result == 'OK')
        .length;
  }

  String _nextSchedule(AppState s) {
    final enabled = s.schedules.where((sc) => sc.enabled).toList();
    if (enabled.isEmpty) return '--:--';
    final now = TimeOfDay.now();
    final upcoming = enabled.where((sc) =>
        sc.hour > now.hour || (sc.hour == now.hour && sc.minute > now.minute)).toList();
    final next = upcoming.isNotEmpty ? upcoming.first : enabled.first;
    return '${next.hour.toString().padLeft(2, '0')}:${next.minute.toString().padLeft(2, '0')}';
  }

  String _nextScheduleGrams(AppState s) {
    final enabled = s.schedules.where((sc) => sc.enabled).toList();
    if (enabled.isEmpty) return '';
    final now = TimeOfDay.now();
    final upcoming = enabled.where((sc) =>
        sc.hour > now.hour || (sc.hour == now.hour && sc.minute > now.minute)).toList();
    final next = upcoming.isNotEmpty ? upcoming.first : enabled.first;
    return '${next.grams.toStringAsFixed(0)} gram';
  }
}

class _StatusBadge extends StatelessWidget {
  final bool online;
  final bool connected;
  const _StatusBadge({required this.online, required this.connected});

  @override
  Widget build(BuildContext context) {
    final color = !connected ? Colors.grey : online ? AppColors.green : AppColors.red;
    final text = !connected ? 'Offline' : online ? 'Online' : 'Offline';
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 6),
      decoration: BoxDecoration(
        color: color.withValues(alpha: 0.1),
        borderRadius: BorderRadius.circular(999),
        border: Border.all(color: color.withValues(alpha: 0.3)),
      ),
      child: Row(
        mainAxisSize: MainAxisSize.min,
        children: [
          Container(width: 8, height: 8, decoration: BoxDecoration(shape: BoxShape.circle, color: color)),
          const SizedBox(width: 6),
          Text(text, style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: color)),
        ],
      ),
    );
  }
}

class _StatCard extends StatelessWidget {
  final String label;
  final String value;
  final String sub;
  const _StatCard({required this.label, required this.value, required this.sub});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Text(label, style: const TextStyle(fontSize: 12, color: AppColors.fgSecondary)),
            const SizedBox(height: 4),
            Text(value, style: const TextStyle(fontSize: 28, fontWeight: FontWeight.w700)),
            Text(sub, style: const TextStyle(fontSize: 12, color: AppColors.fgMuted)),
          ],
        ),
      ),
    );
  }
}

class _RecognitionCard extends StatelessWidget {
  final dynamic log;
  const _RecognitionCard({required this.log});

  @override
  Widget build(BuildContext context) {
    final status = log.status as String;
    final color = status == 'KNOWN' ? AppColors.green : status == 'UNCERTAIN' ? AppColors.orange : AppColors.red;
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Nhận diện gần nhất',
                style: TextStyle(fontSize: 15, fontWeight: FontWeight.w700)),
            const SizedBox(height: 8),
            Text(log.petId != null ? 'Mèo #${log.petId}' : 'Unknown',
                style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
            Text(status,
                style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: color)),
            Text('Đã xác minh lúc ${_fmtTime(log.createdAt)}',
                style: const TextStyle(fontSize: 12, color: AppColors.fgMuted)),
            const SizedBox(height: 8),
            GestureDetector(
              onTap: () {
                // Navigate to AI tab would be handled by parent
              },
              child: const Text('Mở trung tâm AI',
                  style: TextStyle(fontSize: 13, fontWeight: FontWeight.w600, color: AppColors.fgSecondary)),
            ),
          ],
        ),
      ),
    );
  }

  String _fmtTime(DateTime dt) {
    return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
