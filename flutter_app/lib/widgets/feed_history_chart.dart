import 'package:flutter/material.dart';
import 'package:fl_chart/fl_chart.dart';
import 'package:intl/intl.dart';
import '../models/feeding_log.dart';

class FeedHistoryChart extends StatelessWidget {
  final List<FeedingLog> history;
  const FeedHistoryChart({super.key, required this.history});

  @override
  Widget build(BuildContext context) {
    if (history.isEmpty) {
      return const Center(child: Text('Chưa có dữ liệu'));
    }

    final byDay = <String, Map<String, double>>{};
    for (final f in history) {
      final day = DateFormat('MM-dd').format(f.createdAt.toLocal());
      byDay.putIfAbsent(day, () => {'schedule': 0, 'manual': 0, 'camera': 0, 'other': 0});
      final key = ['schedule', 'manual', 'camera'].contains(f.source)
          ? f.source
          : 'other';
      byDay[day]![key] = (byDay[day]![key] ?? 0) + f.actualGrams;
    }

    final days = byDay.keys.toList()..sort();
    final last7 = days.length > 7 ? days.sublist(days.length - 7) : days;

    return BarChart(
      BarChartData(
        alignment: BarChartAlignment.spaceAround,
        maxY: last7.fold<double>(0, (mx, d) {
              final m = byDay[d]!;
              final total =
                  (m['schedule']!) + (m['manual']!) + (m['camera']!) + (m['other']!);
              return total > mx ? total : mx;
            }) *
            1.15,
        barTouchData: BarTouchData(
          touchTooltipData: BarTouchTooltipData(
            getTooltipItem: (group, gi, rod, ri) {
              return BarTooltipItem(
                '${rod.toY.toStringAsFixed(0)}g',
                const TextStyle(
                    color: Colors.white,
                    fontWeight: FontWeight.w600,
                    fontSize: 12),
              );
            },
          ),
        ),
        titlesData: FlTitlesData(
          leftTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              reservedSize: 36,
              getTitlesWidget: (v, _) => Text('${v.toInt()}',
                  style: const TextStyle(fontSize: 10)),
            ),
          ),
          bottomTitles: AxisTitles(
            sideTitles: SideTitles(
              showTitles: true,
              getTitlesWidget: (v, _) {
                final i = v.toInt();
                if (i < 0 || i >= last7.length) return const SizedBox.shrink();
                return Padding(
                  padding: const EdgeInsets.only(top: 6),
                  child: Text(last7[i],
                      style: const TextStyle(fontSize: 10)),
                );
              },
            ),
          ),
          topTitles: const AxisTitles(sideTitles: SideTitles(showTitles: false)),
          rightTitles:
              const AxisTitles(sideTitles: SideTitles(showTitles: false)),
        ),
        gridData: FlGridData(
          horizontalInterval: 20,
          getDrawingHorizontalLine: (v) => FlLine(
            color: Colors.grey.shade200,
            strokeWidth: 1,
            dashArray: [4, 4],
          ),
        ),
        borderData: FlBorderData(show: false),
        barGroups: last7.asMap().entries.map((e) {
          final d = byDay[e.value]!;
          return BarChartGroupData(
            x: e.key,
            barRods: [
              BarChartRodData(
                toY: d['schedule']! + d['manual']! + d['camera']! + d['other']!,
                width: 18,
                borderRadius: const BorderRadius.vertical(top: Radius.circular(4)),
                rodStackItems: [
                  BarChartRodStackItem(0, d['schedule']!, Colors.blue),
                  BarChartRodStackItem(d['schedule']!,
                      d['schedule']! + d['manual']!, Colors.green),
                  BarChartRodStackItem(
                      d['schedule']! + d['manual']!,
                      d['schedule']! + d['manual']! + d['camera']!,
                      Colors.orange),
                  BarChartRodStackItem(
                      d['schedule']! + d['manual']! + d['camera']!,
                      d['schedule']! +
                          d['manual']! +
                          d['camera']! +
                          d['other']!,
                      Colors.purple),
                ],
              ),
            ],
          );
        }).toList(),
      ),
    );
  }
}
