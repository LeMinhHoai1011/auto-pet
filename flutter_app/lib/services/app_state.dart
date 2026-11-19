import 'dart:async';
import 'package:flutter/foundation.dart';
import 'api_service.dart';
import '../models/device_state.dart';
import '../models/feeding_log.dart';
import '../models/schedule.dart';
import '../models/alert_log.dart';

class AppState extends ChangeNotifier {
  final ApiService api = ApiService();

  DeviceState device = DeviceState.empty();
  List<FeedingLog> feedHistory = [];
  List<Schedule> schedules = [];
  List<AlertLog> alerts = [];
  bool connected = false;
  bool loading = true;
  String? error;

  Timer? _timer;

  Future<void> init() async {
    await api.init();
    await refresh();
    _timer = Timer.periodic(const Duration(seconds: 30), (_) => refresh());
  }

  @override
  void dispose() {
    _timer?.cancel();
    super.dispose();
  }

  Future<void> refresh() async {
    loading = true;
    notifyListeners();

    connected = await api.checkHealth();
    if (!connected) {
      loading = false;
      error = 'Không kết nối được server';
      notifyListeners();
      return;
    }
    error = null;

    final results = await Future.wait([
      api.getDeviceStatus(),
      api.getFeedHistory(limit: 50),
      api.getSchedules(),
      api.getAlerts(limit: 20),
    ]);

    final ds = results[0] as DeviceState?;
    if (ds != null) device = ds;
    feedHistory = results[1] as List<FeedingLog>;
    schedules = results[2] as List<Schedule>;
    alerts = results[3] as List<AlertLog>;

    loading = false;
    notifyListeners();
  }

  Future<bool> feed(double grams) async {
    final ok = await api.triggerFeed(grams);
    if (ok) {
      await Future.delayed(const Duration(seconds: 3));
      await refresh();
    }
    return ok;
  }

  Future<bool> tare() async {
    final ok = await api.triggerTare();
    if (ok) await refresh();
    return ok;
  }

  Future<bool> addSchedule(int hour, int minute, double grams) async {
    final s = await api.createSchedule(hour, minute, grams);
    if (s != null) await refresh();
    return s != null;
  }

  Future<bool> toggleSchedule(int id, bool enabled) async {
    final ok = await api.updateSchedule(id, enabled: enabled);
    if (ok) await refresh();
    return ok;
  }

  Future<bool> removeSchedule(int id) async {
    final ok = await api.deleteSchedule(id);
    if (ok) await refresh();
    return ok;
  }

  Future<bool> resolveAlert(int id) async {
    final ok = await api.resolveAlert(id);
    if (ok) await refresh();
    return ok;
  }
}
