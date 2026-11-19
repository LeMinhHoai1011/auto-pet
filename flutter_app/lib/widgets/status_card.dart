import 'package:flutter/material.dart';
import 'package:intl/intl.dart';

class StatusCard extends StatelessWidget {
  final bool online;
  final bool connected;
  final DateTime updatedAt;
  final String? error;

  const StatusCard({
    super.key,
    required this.online,
    required this.connected,
    required this.updatedAt,
    this.error,
  });

  @override
  Widget build(BuildContext context) {
    final color = !connected
        ? Colors.grey
        : online
            ? Colors.green
            : Colors.red;
    final label = !connected
        ? 'Mất kết nối server'
        : online
            ? 'Thiết bị Online'
            : 'Thiết bị Offline';

    return Card(
      elevation: 0,
      shape: RoundedRectangleBorder(
        borderRadius: BorderRadius.circular(14),
        side: BorderSide(color: color.withValues(alpha: 0.3)),
      ),
      color: color.withValues(alpha: 0.08),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
        child: Row(
          children: [
            Container(
              width: 10,
              height: 10,
              decoration: BoxDecoration(shape: BoxShape.circle, color: color),
            ),
            const SizedBox(width: 10),
            Expanded(
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  Text(label,
                      style: TextStyle(
                          fontWeight: FontWeight.w600, color: color)),
                  if (error != null)
                    Text(error!,
                        style: TextStyle(fontSize: 12, color: color)),
                ],
              ),
            ),
            Text(
              DateFormat('HH:mm dd/MM').format(updatedAt.toLocal()),
              style: TextStyle(fontSize: 12, color: Colors.grey.shade600),
            ),
          ],
        ),
      ),
    );
  }
}
