import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../services/app_state.dart';
import '../theme.dart';

class FeedButton extends StatefulWidget {
  const FeedButton({super.key});

  @override
  State<FeedButton> createState() => _FeedButtonState();
}

class _FeedButtonState extends State<FeedButton> {
  double _grams = 30;
  bool _sending = false;

  Future<void> _confirmAndFeed() async {
    final state = context.read<AppState>();
    if (!state.connected || !state.device.online) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Thiết bị offline — không thể cho ăn'), backgroundColor: AppColors.red),
      );
      return;
    }

    final confirmed = await showDialog<bool>(
      context: context,
      builder: (ctx) => AlertDialog(
        title: const Text('Xác nhận cho ăn'),
        content: Text('Xả ${_grams.toStringAsFixed(0)}g thức ăn ngay bây giờ?'),
        actions: [
          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy')),
          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Cho ăn')),
        ],
      ),
    );
    if (confirmed != true || !mounted) return;

    setState(() => _sending = true);
    final ok = await state.feed(_grams);
    if (mounted) {
      setState(() => _sending = false);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(
          content: Text(ok ? 'Đã gửi lệnh cho ăn ${_grams.toStringAsFixed(0)}g' : 'Lỗi gửi lệnh'),
          backgroundColor: ok ? AppColors.green : AppColors.red,
        ),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    return Card(
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
                      const Text('Cho ăn ngay',
                          style: TextStyle(fontSize: 16, fontWeight: FontWeight.w700)),
                      const SizedBox(height: 4),
                      Text('${_grams.toStringAsFixed(0)} grams',
                          style: const TextStyle(color: AppColors.fgSecondary)),
                    ],
                  ),
                ),
                FilledButton.icon(
                  onPressed: _sending ? null : _confirmAndFeed,
                  icon: _sending
                      ? const SizedBox(
                          width: 18, height: 18,
                          child: CircularProgressIndicator(strokeWidth: 2, color: Colors.white))
                      : const Icon(Icons.pets),
                  label: Text(_sending ? 'Đang gửi...' : 'Cho ăn'),
                ),
              ],
            ),
            const SizedBox(height: 10),
            Row(
              children: [
                const Text('10g', style: TextStyle(fontSize: 12, color: AppColors.fgMuted)),
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
                const Text('100g', style: TextStyle(fontSize: 12, color: AppColors.fgMuted)),
              ],
            ),
            Row(
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                TextButton(
                  onPressed: () async {
                    final ok = await context.read<AppState>().tare();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text(ok ? 'Đã tare cân' : 'Lỗi tare'),
                        backgroundColor: ok ? AppColors.green : AppColors.red,
                      ));
                    }
                  },
                  child: const Text('Tare cân'),
                ),
                const SizedBox(width: 8),
                TextButton.icon(
                  onPressed: () async {
                    final confirmed = await showDialog<bool>(
                      context: context,
                      builder: (ctx) => AlertDialog(
                        title: const Text('Đã ăn xong?'),
                        content: const Text('Reset bát về 0g để sẵn sàng cho ăn tiếp.'),
                        actions: [
                          TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Hủy')),
                          FilledButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Xác nhận')),
                        ],
                      ),
                    );
                    if (confirmed != true || !context.mounted) return;
                    final ok = await context.read<AppState>().tare();
                    if (context.mounted) {
                      ScaffoldMessenger.of(context).showSnackBar(SnackBar(
                        content: Text(ok ? 'Đã reset bát — sẵn sàng cho ăn tiếp' : 'Lỗi'),
                        backgroundColor: ok ? AppColors.green : AppColors.red,
                      ));
                    }
                  },
                  icon: const Icon(Icons.check_circle_outline, size: 18),
                  label: const Text('Đã ăn xong'),
                  style: TextButton.styleFrom(foregroundColor: AppColors.green),
                ),
              ],
            ),
          ],
        ),
      ),
    );
  }
}
