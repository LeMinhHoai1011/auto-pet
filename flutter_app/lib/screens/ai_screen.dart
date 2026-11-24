import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../models/pet.dart';
import '../theme.dart';

class AIScreen extends StatelessWidget {
  const AIScreen({super.key});

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    return Scaffold(
      appBar: AppBar(title: const Text('Nhận diện AI')),
      body: RefreshIndicator(
        onRefresh: state.refresh,
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            _StatusCard(state: state),
            const SizedBox(height: 16),
            if (state.pendingSessions.isNotEmpty) ...[
              const Text('Phiên chờ xác nhận',
                  style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
              const SizedBox(height: 10),
              ...state.pendingSessions.map((s) => _SessionCard(session: s, pets: state.pets)),
              const SizedBox(height: 16),
            ],
            const Text('Nhật ký nhận diện',
                style: TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
            const SizedBox(height: 10),
            if (state.recognitionLogs.isEmpty)
              const Center(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Text('Chưa có nhật ký', style: TextStyle(color: AppColors.fgSecondary)),
                ),
              )
            else
              ...state.recognitionLogs.map((log) => _LogCard(log: log)),
          ],
        ),
      ),
    );
  }
}

class _StatusCard extends StatelessWidget {
  final AppState state;
  const _StatusCard({required this.state});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.smart_toy, color: AppColors.green),
                const SizedBox(width: 8),
                const Expanded(
                  child: Text('Trung tâm AI',
                      style: TextStyle(fontSize: 17, fontWeight: FontWeight.w700)),
                ),
                Container(
                  padding: const EdgeInsets.symmetric(horizontal: 10, vertical: 4),
                  decoration: BoxDecoration(
                    color: AppColors.greenLight,
                    borderRadius: BorderRadius.circular(999),
                  ),
                  child: Text(
                    '${state.pets.where((p) => p.isReady).length} mèo đã đăng ký',
                    style: const TextStyle(fontSize: 12, fontWeight: FontWeight.w600, color: AppColors.green),
                  ),
                ),
              ],
            ),
            const SizedBox(height: 12),
            Row(
              children: [
                _MiniStat(label: 'Tổng log', value: '${state.recognitionLogs.length}'),
                const SizedBox(width: 16),
                _MiniStat(label: 'Chờ duyệt', value: '${state.pendingSessions.length}'),
                const SizedBox(width: 16),
                _MiniStat(label: 'Thú cưng', value: '${state.pets.length}'),
              ],
            ),
          ],
        ),
      ),
    );
  }
}

class _MiniStat extends StatelessWidget {
  final String label;
  final String value;
  const _MiniStat({required this.label, required this.value});

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Text(value, style: const TextStyle(fontSize: 22, fontWeight: FontWeight.w700)),
        Text(label, style: const TextStyle(fontSize: 12, color: AppColors.fgSecondary)),
      ],
    );
  }
}

class _SessionCard extends StatelessWidget {
  final RecognitionSession session;
  final List<Pet> pets;
  const _SessionCard({required this.session, required this.pets});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.only(bottom: 10),
      child: Padding(
        padding: const EdgeInsets.all(14),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const Icon(Icons.help_outline, color: AppColors.orange, size: 20),
                const SizedBox(width: 6),
                Expanded(
                  child: Text(
                    'Phiên #${session.trackerId} • ${session.imageCount} ảnh',
                    style: const TextStyle(fontSize: 14, fontWeight: FontWeight.w600),
                  ),
                ),
                Text(
                  '${(session.similarityScore * 100).toStringAsFixed(0)}%',
                  style: const TextStyle(fontSize: 13, fontWeight: FontWeight.w700, color: AppColors.orange),
                ),
              ],
            ),
            if (session.suggestedPetId != null) ...[
              const SizedBox(height: 6),
              Text(
                'Gợi ý: ${_petName(session.suggestedPetId!)}',
                style: const TextStyle(fontSize: 13, color: AppColors.fgSecondary),
              ),
            ],
            const SizedBox(height: 10),
            Row(
              children: [
                Expanded(
                  child: OutlinedButton(
                    onPressed: () => _showAssignDialog(context),
                    child: const Text('Xác nhận'),
                  ),
                ),
                const SizedBox(width: 8),
                OutlinedButton(
                  onPressed: () => context.read<AppState>().rejectSession(session.sessionId),
                  style: OutlinedButton.styleFrom(foregroundColor: AppColors.red),
                  child: const Text('Bỏ qua'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }

  String _petName(int id) {
    final match = pets.where((p) => p.id == id);
    return match.isNotEmpty ? match.first.name : 'Mèo #$id';
  }

  void _showAssignDialog(BuildContext context) {
    final state = context.read<AppState>();
    final newNameCtrl = TextEditingController();

    showDialog(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Gán thú cưng'),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          children: [
            if (pets.isNotEmpty) ...[
              const Align(
                alignment: Alignment.centerLeft,
                child: Text('Chọn thú cưng:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
              ),
              const SizedBox(height: 6),
              ...pets.map((p) => ListTile(
                    dense: true,
                    leading: CircleAvatar(
                      radius: 16,
                      backgroundColor: AppColors.greenLight,
                      child: Text(p.name[0], style: const TextStyle(color: AppColors.green, fontWeight: FontWeight.w700)),
                    ),
                    title: Text(p.name),
                    onTap: () {
                      Navigator.pop(ctx);
                      state.assignSession(session.sessionId, petId: p.id);
                    },
                  )),
              const Divider(),
            ],
            const Align(
              alignment: Alignment.centerLeft,
              child: Text('Hoặc tạo mới:', style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            ),
            const SizedBox(height: 6),
            TextField(
              controller: newNameCtrl,
              decoration: const InputDecoration(hintText: 'Tên thú cưng mới'),
            ),
          ],
        ),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx), child: const Text('Hủy')),
          FilledButton(
            onPressed: () {
              final name = newNameCtrl.text.trim();
              if (name.isEmpty) return;
              Navigator.pop(ctx);
              state.assignSession(session.sessionId, newPetName: name);
            },
            child: const Text('Tạo & gán'),
          ),
        ],
      ),
    );
  }
}

class _LogCard extends StatelessWidget {
  final RecognitionLog log;
  const _LogCard({required this.log});

  @override
  Widget build(BuildContext context) {
    final color = log.status == 'KNOWN'
        ? AppColors.green
        : log.status == 'UNCERTAIN'
            ? AppColors.orange
            : AppColors.red;

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: CircleAvatar(
          backgroundColor: color.withValues(alpha: 0.1),
          child: Icon(
            log.status == 'KNOWN' ? Icons.check : log.status == 'UNCERTAIN' ? Icons.help_outline : Icons.close,
            color: color,
            size: 20,
          ),
        ),
        title: Text(
          log.petId != null ? 'Mèo #${log.petId}' : 'Không xác định',
          style: const TextStyle(fontWeight: FontWeight.w600),
        ),
        subtitle: Text(
          '${log.status} • ${(log.similarity * 100).toStringAsFixed(0)}%',
          style: const TextStyle(fontSize: 12, color: AppColors.fgSecondary),
        ),
        trailing: Text(
          _fmtTime(log.createdAt),
          style: const TextStyle(fontSize: 12, color: AppColors.fgMuted),
        ),
      ),
    );
  }

  String _fmtTime(DateTime dt) {
    return '${dt.hour.toString().padLeft(2, '0')}:${dt.minute.toString().padLeft(2, '0')}';
  }
}
