import 'package:flutter/material.dart';
import '../models/device_state.dart';

class TileRow extends StatelessWidget {
  final DeviceState device;
  const TileRow({super.key, required this.device});

  @override
  Widget build(BuildContext context) {
    return Wrap(
      spacing: 10,
      runSpacing: 10,
      children: [
        _Tile(
          label: 'Bát',
          value: '${device.bowlGrams.toStringAsFixed(0)}g',
          color: device.bowlGrams < 5
              ? Colors.red
              : device.bowlGrams < 15
                  ? Colors.orange
                  : Colors.green,
          icon: Icons.scale,
        ),
        _Tile(
          label: 'Phễu',
          value: '${device.hopperPct}%',
          color: device.hopperPct < 15
              ? Colors.red
              : device.hopperPct < 30
                  ? Colors.orange
                  : Colors.green,
          icon: Icons.inventory_2,
        ),
        _Tile(
          label: 'Nhiệt độ',
          value: '${device.temperature.toStringAsFixed(1)}°',
          color: device.temperature > 32
              ? Colors.red
              : Colors.blue,
          icon: Icons.thermostat,
        ),
        _Tile(
          label: 'Độ ẩm',
          value: '${device.humidity.toStringAsFixed(0)}%',
          color: device.humidity > 70
              ? Colors.orange
              : Colors.teal,
          icon: Icons.water_drop,
        ),
      ],
    );
  }
}

class _Tile extends StatelessWidget {
  final String label;
  final String value;
  final Color color;
  final IconData icon;

  const _Tile({
    required this.label,
    required this.value,
    required this.color,
    required this.icon,
  });

  @override
  Widget build(BuildContext context) {
    final width = (MediaQuery.of(context).size.width - 42) / 2;
    return SizedBox(
      width: width,
      child: Card(
        elevation: 0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(12),
          side: BorderSide(color: Colors.grey.shade200),
        ),
        child: Padding(
          padding: const EdgeInsets.all(14),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Icon(icon, size: 16, color: color),
                  const SizedBox(width: 6),
                  Text(label,
                      style: TextStyle(
                          fontSize: 12, color: Colors.grey.shade600)),
                ],
              ),
              const SizedBox(height: 6),
              Text(value,
                  style: TextStyle(
                      fontSize: 26,
                      fontWeight: FontWeight.w700,
                      color: color)),
            ],
          ),
        ),
      ),
    );
  }
}
