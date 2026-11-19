class Schedule {
  final int id;
  final int hour;
  final int minute;
  final double grams;
  final bool enabled;

  Schedule({
    required this.id,
    required this.hour,
    required this.minute,
    required this.grams,
    required this.enabled,
  });

  factory Schedule.fromJson(Map<String, dynamic> json) {
    return Schedule(
      id: json['id'] as int,
      hour: json['hour'] as int,
      minute: json['minute'] as int,
      grams: (json['grams'] as num).toDouble(),
      enabled: json['enabled'] as bool,
    );
  }

  String get timeStr =>
      '${hour.toString().padLeft(2, '0')}:${minute.toString().padLeft(2, '0')}';
}
