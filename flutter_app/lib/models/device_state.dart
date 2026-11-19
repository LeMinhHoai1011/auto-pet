class DeviceState {
  final double bowlGrams;
  final int hopperPct;
  final double temperature;
  final double humidity;
  final double staleScore;
  final bool online;
  final DateTime? lastFeedAt;
  final DateTime updatedAt;

  DeviceState({
    required this.bowlGrams,
    required this.hopperPct,
    required this.temperature,
    required this.humidity,
    required this.staleScore,
    required this.online,
    this.lastFeedAt,
    required this.updatedAt,
  });

  factory DeviceState.fromJson(Map<String, dynamic> json) {
    return DeviceState(
      bowlGrams: (json['bowl_grams'] as num).toDouble(),
      hopperPct: (json['hopper_pct'] as num).toInt(),
      temperature: (json['temperature'] as num).toDouble(),
      humidity: (json['humidity'] as num).toDouble(),
      staleScore: (json['stale_score'] as num).toDouble(),
      online: json['online'] as bool,
      lastFeedAt: json['last_feed_at'] != null
          ? DateTime.parse(json['last_feed_at'] as String)
          : null,
      updatedAt: DateTime.parse(json['updated_at'] as String),
    );
  }

  factory DeviceState.empty() => DeviceState(
        bowlGrams: 0,
        hopperPct: 0,
        temperature: 0,
        humidity: 0,
        staleScore: 0,
        online: false,
        updatedAt: DateTime.now(),
      );
}
