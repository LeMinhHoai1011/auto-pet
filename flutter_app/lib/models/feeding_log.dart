class FeedingLog {
  final int id;
  final String source;
  final String result;
  final double actualGrams;
  final DateTime createdAt;

  FeedingLog({
    required this.id,
    required this.source,
    required this.result,
    required this.actualGrams,
    required this.createdAt,
  });

  factory FeedingLog.fromJson(Map<String, dynamic> json) {
    return FeedingLog(
      id: json['id'] as int,
      source: json['source'] as String,
      result: json['result'] as String,
      actualGrams: (json['actual_grams'] as num).toDouble(),
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
