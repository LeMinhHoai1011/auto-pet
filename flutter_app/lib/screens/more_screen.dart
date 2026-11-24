import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import 'package:intl/intl.dart';
import '../services/app_state.dart';
import '../theme.dart';

class MoreScreen extends StatelessWidget {
  const MoreScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Thêm')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          _SectionHeader(title: 'Cảnh báo', trailing: _AlertBadge()),
          const SizedBox(height: 8),
          const _AlertsList(),
          const SizedBox(height: 24),
          const _SectionHeader(title: 'Cài đặt'),
          const SizedBox(height: 8),
          const _SettingsSection(),
          const SizedBox(height: 24),
          const _SectionHeader(title: 'Thông tin'),
          const SizedBox(height: 8),
          Card(
            child: Column(
              children: [
                const ListTile(
                  leading: Icon(Icons.info_outline),
                  title: Text('Pet Auto'),
                  subtitle: Text('v1.0.0 • ESP32 + FastAPI + Flutter'),
                ),
                ListTile(
                  leading: const Icon(Icons.refresh),
                  title: const Text('Làm mới dữ liệu'),
                  onTap: () => context.read<AppState>().refresh(),
                ),
              ],
            ),
          ),
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
        Text(title, style: const TextStyle(fontSize: 18, fontWeight: FontWeight.w700)),
        if (trailing != null) ...[const Spacer(), trailing!],
      ],
    );
  }
}

class _AlertBadge extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    final count = context.select<AppState, int>((s) => s.alerts.where((a) => !a.resolved).length);
    if (count == 0) return const SizedBox.shrink();
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
      decoration: BoxDecoration(color: AppColors.red, borderRadius: BorderRadius.circular(999)),
      child: Text('$count', style: const TextStyle(color: Colors.white, fontSize: 12, fontWeight: FontWeight.w700)),
    );
  }
}

class _AlertsList extends StatelessWidget {
  const _AlertsList();

  @override
  Widget build(BuildContext context) {
    final state = context.watch<AppState>();

    if (state.alerts.isEmpty) {
      return Card(
        child: Padding(
          padding: const EdgeInsets.all(24),
          child: Center(
            child: Text('Không có cảnh báo', style: TextStyle(color: AppColors.fgSecondary)),
          ),
        ),
      );
    }

    return Card(
      child: Column(
        children: [
          for (var i = 0; i < state.alerts.length && i < 5; i++) ...[
            if (i > 0) const Divider(height: 1),
            _AlertTile(alert: state.alerts[i]),
          ],
          if (state.alerts.length > 5)
            Padding(
              padding: const EdgeInsets.all(8),
              child: Text('+ ${state.alerts.length - 5} cảnh báo khác',
                  style: const TextStyle(fontSize: 12, color: AppColors.fgMuted)),
            ),
        ],
      ),
    );
  }
}

class _AlertTile extends StatelessWidget {
  final dynamic alert;
  const _AlertTile({required this.alert});

  @override
  Widget build(BuildContext context) {
    final color = alert.alertType == 'JAM'
        ? AppColors.red
        : alert.alertType == 'LOW_FOOD'
            ? AppColors.orange
            : AppColors.orange;
    final icon = alert.alertType == 'JAM'
        ? Icons.error
        : alert.alertType == 'LOW_FOOD'
            ? Icons.inventory_2
            : Icons.access_time;

    return ListTile(
      dense: true,
      leading: CircleAvatar(
        radius: 16,
        backgroundColor: color.withValues(alpha: 0.1),
        child: Icon(icon, color: color, size: 18),
      ),
      title: Text(alert.message, style: const TextStyle(fontSize: 14)),
      subtitle: Text(
        DateFormat('HH:mm dd/MM').format(alert.createdAt.toLocal()),
        style: const TextStyle(fontSize: 11, color: AppColors.fgMuted),
      ),
      trailing: alert.resolved
          ? const Icon(Icons.check_circle, color: AppColors.green, size: 20)
          : TextButton(
              onPressed: () => context.read<AppState>().resolveAlert(alert.id),
              style: TextButton.styleFrom(padding: EdgeInsets.zero, minimumSize: const Size(60, 30)),
              child: const Text('Xử lý', style: TextStyle(fontSize: 12)),
            ),
    );
  }
}

class _SettingsSection extends StatefulWidget {
  const _SettingsSection();

  @override
  State<_SettingsSection> createState() => _SettingsSectionState();
}

class _SettingsSectionState extends State<_SettingsSection> {
  late TextEditingController _urlCtrl;
  bool _testing = false;
  bool? _testOk;

  @override
  void initState() {
    super.initState();
    _urlCtrl = TextEditingController(text: context.read<AppState>().api.serverUrl);
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text('Server URL',
                style: TextStyle(fontSize: 14, fontWeight: FontWeight.w600)),
            const SizedBox(height: 8),
            TextField(
              controller: _urlCtrl,
              decoration: InputDecoration(
                hintText: 'http://192.168.1.100',
                suffixIcon: _testing
                    ? const Padding(
                        padding: EdgeInsets.all(12),
                        child: SizedBox(width: 20, height: 20, child: CircularProgressIndicator(strokeWidth: 2)))
                    : _testOk == null
                        ? null
                        : Icon(_testOk! ? Icons.check_circle : Icons.error,
                            color: _testOk! ? AppColors.green : AppColors.red),
              ),
              keyboardType: TextInputType.url,
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                OutlinedButton(
                  onPressed: _testing ? null : _testConnection,
                  child: const Text('Test'),
                ),
                const SizedBox(width: 8),
                FilledButton(
                  onPressed: _saveUrl,
                  child: const Text('Lưu'),
                ),
              ],
            ),
            if (_testOk == true)
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text('Kết nối OK', style: TextStyle(color: AppColors.green, fontSize: 13)),
              ),
            if (_testOk == false)
              const Padding(
                padding: EdgeInsets.only(top: 6),
                child: Text('Không kết nối được', style: TextStyle(color: AppColors.red, fontSize: 13)),
              ),
          ],
        ),
      ),
    );
  }

  Future<void> _testConnection() async {
    setState(() { _testing = true; _testOk = null; });
    final api = context.read<AppState>().api;
    await api.setServerUrl(_urlCtrl.text.trim());
    final ok = await api.checkHealth();
    if (mounted) setState(() { _testing = false; _testOk = ok; });
  }

  Future<void> _saveUrl() async {
    final app = context.read<AppState>();
    await app.api.setServerUrl(_urlCtrl.text.trim());
    await app.refresh();
    if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Đã lưu URL server')),
      );
    }
  }
}
