class AlertLog {
  final int id;
  final String alertType;
  final String message;
  final bool resolved;
  final DateTime createdAt;

  AlertLog({
    required this.id,
    required this.alertType,
    required this.message,
    required this.resolved,
    required this.createdAt,
  });

  factory AlertLog.fromJson(Map<String, dynamic> json) {
    return AlertLog(
      id: json['id'] as int,
      alertType: json['alert_type'] as String,
      message: json['message'] as String,
      resolved: json['resolved'] as bool,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
