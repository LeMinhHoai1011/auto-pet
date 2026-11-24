class Pet {
  final int id;
  final String name;
  final String breed;
  final String color;
  final int? ageMonths;
  final double? weightKg;
  final String notes;
  final String avatarPath;
  final bool active;
  final bool autoFeed;
  final double portionGrams;
  final double dailyLimitGrams;
  final int minFeedIntervalMin;
  final int embeddingCount;
  final DateTime? lastSeenAt;
  final DateTime? lastFedAt;
  final DateTime createdAt;

  Pet({
    required this.id,
    required this.name,
    this.breed = '',
    this.color = '',
    this.ageMonths,
    this.weightKg,
    this.notes = '',
    this.avatarPath = '',
    this.active = true,
    this.autoFeed = true,
    this.portionGrams = 30,
    this.dailyLimitGrams = 150,
    this.minFeedIntervalMin = 120,
    this.embeddingCount = 0,
    this.lastSeenAt,
    this.lastFedAt,
    required this.createdAt,
  });

  factory Pet.fromJson(Map<String, dynamic> json) {
    return Pet(
      id: json['id'] as int,
      name: json['name'] as String,
      breed: json['breed'] as String? ?? '',
      color: json['color'] as String? ?? '',
      ageMonths: json['age_months'] as int?,
      weightKg: (json['weight_kg'] as num?)?.toDouble(),
      notes: json['notes'] as String? ?? '',
      avatarPath: json['avatar_path'] as String? ?? '',
      active: json['active'] as bool? ?? true,
      autoFeed: json['auto_feed'] as bool? ?? true,
      portionGrams: (json['portion_grams'] as num?)?.toDouble() ?? 30,
      dailyLimitGrams: (json['daily_limit_grams'] as num?)?.toDouble() ?? 150,
      minFeedIntervalMin: json['min_feed_interval_min'] as int? ?? 120,
      embeddingCount: json['embedding_count'] as int? ?? 0,
      lastSeenAt: json['last_seen_at'] != null
          ? DateTime.parse(json['last_seen_at'] as String)
          : null,
      lastFedAt: json['last_fed_at'] != null
          ? DateTime.parse(json['last_fed_at'] as String)
          : null,
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }

  bool get isReady => embeddingCount >= 5;
}

class RecognitionSession {
  final int id;
  final String sessionId;
  final int trackerId;
  final String status;
  final int? suggestedPetId;
  final int? assignedPetId;
  final double similarityScore;
  final int imageCount;
  final DateTime startedAt;
  final DateTime? endedAt;

  RecognitionSession({
    required this.id,
    required this.sessionId,
    required this.trackerId,
    required this.status,
    this.suggestedPetId,
    this.assignedPetId,
    required this.similarityScore,
    required this.imageCount,
    required this.startedAt,
    this.endedAt,
  });

  factory RecognitionSession.fromJson(Map<String, dynamic> json) {
    return RecognitionSession(
      id: json['id'] as int,
      sessionId: json['session_id'] as String,
      trackerId: json['tracker_id'] as int,
      status: json['status'] as String,
      suggestedPetId: json['suggested_pet_id'] as int?,
      assignedPetId: json['assigned_pet_id'] as int?,
      similarityScore: (json['similarity_score'] as num).toDouble(),
      imageCount: json['image_count'] as int,
      startedAt: DateTime.parse(json['started_at'] as String),
      endedAt: json['ended_at'] != null
          ? DateTime.parse(json['ended_at'] as String)
          : null,
    );
  }
}

class RecognitionLog {
  final int id;
  final int? petId;
  final String status;
  final double similarity;
  final int? trackerId;
  final String? sessionId;
  final String imagePath;
  final DateTime createdAt;

  RecognitionLog({
    required this.id,
    this.petId,
    required this.status,
    required this.similarity,
    this.trackerId,
    this.sessionId,
    required this.imagePath,
    required this.createdAt,
  });

  factory RecognitionLog.fromJson(Map<String, dynamic> json) {
    return RecognitionLog(
      id: json['id'] as int,
      petId: json['pet_id'] as int?,
      status: json['status'] as String,
      similarity: (json['similarity'] as num).toDouble(),
      trackerId: json['tracker_id'] as int?,
      sessionId: json['session_id'] as String?,
      imagePath: json['image_path'] as String? ?? '',
      createdAt: DateTime.parse(json['created_at'] as String),
    );
  }
}
