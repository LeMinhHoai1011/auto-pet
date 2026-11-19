import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';

class SettingsScreen extends StatefulWidget {
  const SettingsScreen({super.key});

  @override
  State<SettingsScreen> createState() => _SettingsScreenState();
}

class _SettingsScreenState extends State<SettingsScreen> {
  late TextEditingController _urlCtrl;
  bool _testing = false;
  bool? _testOk;

  @override
  void initState() {
    super.initState();
    final api = context.read<AppState>().api;
    _urlCtrl = TextEditingController(text: api.serverUrl);
  }

  @override
  void dispose() {
    _urlCtrl.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: const Text('Cài đặt')),
      body: ListView(
        padding: const EdgeInsets.all(16),
        children: [
          Text('Server URL',
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          TextField(
            controller: _urlCtrl,
            decoration: InputDecoration(
              hintText: 'http://192.168.1.100',
              border: const OutlineInputBorder(),
              suffixIcon: _testing
                  ? const Padding(
                      padding: EdgeInsets.all(12),
                      child: SizedBox(
                          width: 20,
                          height: 20,
                          child: CircularProgressIndicator(strokeWidth: 2)))
                  : _testOk == null
                      ? null
                      : Icon(
                          _testOk! ? Icons.check_circle : Icons.error,
                          color: _testOk! ? Colors.green : Colors.red,
                        ),
            ),
            keyboardType: TextInputType.url,
          ),
          const SizedBox(height: 12),
          Row(
            children: [
              OutlinedButton(
                onPressed: _testing ? null : _testConnection,
                child: const Text('Test kết nối'),
              ),
              const SizedBox(width: 10),
              FilledButton(
                onPressed: _saveUrl,
                child: const Text('Lưu'),
              ),
            ],
          ),
          if (_testOk == true)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text('Kết nối thành công!',
                  style: TextStyle(color: Colors.green)),
            ),
          if (_testOk == false)
            const Padding(
              padding: EdgeInsets.only(top: 8),
              child: Text('Không kết nối được server',
                  style: TextStyle(color: Colors.red)),
            ),
          const Divider(height: 40),
          Text('Thông tin',
              style: Theme.of(context)
                  .textTheme
                  .titleSmall
                  ?.copyWith(fontWeight: FontWeight.w600)),
          const SizedBox(height: 8),
          const ListTile(
            leading: Icon(Icons.info_outline),
            title: Text('Pet Feeder App'),
            subtitle: Text('v1.0.0 • ESP32 + FastAPI + Flutter'),
          ),
        ],
      ),
    );
  }

  Future<void> _testConnection() async {
    setState(() {
      _testing = true;
      _testOk = null;
    });
    final api = context.read<AppState>().api;
    await api.setServerUrl(_urlCtrl.text.trim());
    final ok = await api.checkHealth();
    if (mounted) {
      setState(() {
        _testing = false;
        _testOk = ok;
      });
    }
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
