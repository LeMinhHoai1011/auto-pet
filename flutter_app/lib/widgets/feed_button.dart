import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';

class FeedButton extends StatefulWidget {
  const FeedButton({super.key});

  @override
  State<FeedButton> createState() => _FeedButtonState();
}

class _FeedButtonState extends State<FeedButton> {
  double _grams = 30;
  bool _sending = false;

  @override
  Widget build(BuildContext context) {
    final theme = Theme.of(context);
    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: theme.colorScheme.primary.withValues(alpha: 0.2)),
      ),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Row(
              children: [
                Expanded(
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('Cho ăn ngay',
                          style: theme.textTheme.titleMedium
                              ?.copyWith(fontWeight: FontWeight.w700)),
                      const SizedBox(height: 4),
                      Text('${_grams.toStringAsFixed(0)} grams',
                          style: TextStyle(color: Colors.grey.shade600)),
                    ],
                  ),
                ),
                FilledButton.icon(
                  onPressed: _sending
                      ? null
                      : () async {
                          setState(() => _sending = true);
                          final ok =
                              await context.read<AppState>().feed(_grams);
                          if (context.mounted) {
                            setState(() => _sending = false);
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(
                                content: Text(ok
                                    ? 'Đã gửi lệnh cho ăn ${_grams.toStringAsFixed(0)}g'
                                    : 'Lỗi gửi lệnh'),
                                backgroundColor: ok ? Colors.green : Colors.red,
                              ),
                            );
                          }
                        },
                  icon: _sending
                      ? const SizedBox(
                          width: 18,
                          height: 18,
                          child: CircularProgressIndicator(
                              strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.pets),
                  label: Text(_sending ? 'Đang gửi...' : 'Cho ăn'),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Text('10g'),
                Expanded(
                  child: Slider(
                    value: _grams,
                    min: 10,
                    max: 100,
                    divisions: 18,
                    label: '${_grams.toStringAsFixed(0)}g',
                    onChanged: (v) => setState(() => _grams = v),
                  ),
                ),
                const Text('100g'),
              ],
            ),
            const SizedBox(height: 4),
            Row(
              children: [
                const Spacer(),
                TextButton(
                  onPressed: () async {
                    final ok = await context.read<AppState>().tare();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text(ok ? 'Đã tare cân' : 'Lỗi tare'),
                        backgroundColor: ok ? Colors.green : Colors.red,
                      ));
                    }
                  },
                  child: const Text('Tare cân'),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
