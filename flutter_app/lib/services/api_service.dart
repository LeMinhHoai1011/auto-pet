import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:shared_preferences/shared_preferences.dart';
import '../models/device_state.dart';
import '../models/feeding_log.dart';
import '../models/schedule.dart';
import '../models/alert_log.dart';

class ApiService {
  static const _defaultHost = 'http://192.168.1.100';
  String _baseUrl = _defaultHost;

  Future<void> init() async {
    final prefs = await SharedPreferences.getInstance();
    _baseUrl = prefs.getString('server_url') ?? _defaultHost;
  }

  Future<void> setServerUrl(String url) async {
    _baseUrl = url;
    final prefs = await SharedPreferences.getInstance();
    await prefs.setString('server_url', url);
  }

  String get serverUrl => _baseUrl;

  Uri _uri(String path, [Map<String, String>? params]) =>
      Uri.parse('$_baseUrl$path').replace(queryParameters: params);

  Future<Map<String, dynamic>?> _get(String path,
      [Map<String, String>? params]) async {
    try {
      final r = await http
          .get(_uri(path, params))
          .timeout(const Duration(seconds: 10));
      if (r.statusCode == 200) {
        final body = jsonDecode(r.body);
        return body is Map<String, dynamic> ? body : null;
      }
    } catch (_) {}
    return null;
  }

  Future<List<dynamic>?> _getList(String path,
      [Map<String, String>? params]) async {
    try {
      final r = await http
          .get(_uri(path, params))
          .timeout(const Duration(seconds: 10));
      if (r.statusCode == 200) return jsonDecode(r.body) as List<dynamic>;
    } catch (_) {}
    return null;
  }

  Future<Map<String, dynamic>?> _post(String path,
      [Map<String, dynamic>? body]) async {
    try {
      final r = await http
          .post(_uri(path),
              headers: {'Content-Type': 'application/json'},
              body: body != null ? jsonEncode(body) : null)
          .timeout(const Duration(seconds: 10));
      if (r.statusCode == 200) return jsonDecode(r.body) as Map<String, dynamic>;
    } catch (_) {}
    return null;
  }

  // ── Health ──
  Future<bool> checkHealth() async {
    final r = await _get('/api/health');
    return r != null && r['status'] == 'ok';
  }

  // ── Device ──
  Future<DeviceState?> getDeviceStatus() async {
    final r = await _get('/api/device/status');
    if (r == null) return null;
    return DeviceState.fromJson(r);
  }

  // ── Feed ──
  Future<bool> triggerFeed(double grams) async {
    final r = await _post('/api/feed/', {'grams': grams});
    return r != null && r['ok'] == true;
  }

  Future<bool> triggerTare() async {
    final r = await _post('/api/feed/tare');
    return r != null && r['ok'] == true;
  }

  Future<List<FeedingLog>> getFeedHistory({int limit = 20}) async {
    final r = await _getList('/api/feed/history', {'limit': '$limit'});
    if (r == null) return [];
    return r.map((e) => FeedingLog.fromJson(e as Map<String, dynamic>)).toList();
  }

  // ── Schedule ──
  Future<List<Schedule>> getSchedules() async {
    final r = await _getList('/api/schedule/');
    if (r == null) return [];
    return r.map((e) => Schedule.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<Schedule?> createSchedule(int hour, int minute, double grams) async {
    final r = await _post(
        '/api/schedule/', {'hour': hour, 'minute': minute, 'grams': grams});
    if (r == null) return null;
    return Schedule.fromJson(r);
  }

  Future<bool> updateSchedule(int id,
      {int? hour, int? minute, double? grams, bool? enabled}) async {
    final body = <String, dynamic>{};
    if (hour != null) body['hour'] = hour;
    if (minute != null) body['minute'] = minute;
    if (grams != null) body['grams'] = grams;
    if (enabled != null) body['enabled'] = enabled;
    try {
      final r = await http
          .put(_uri('/api/schedule/$id'),
              headers: {'Content-Type': 'application/json'},
              body: jsonEncode(body))
          .timeout(const Duration(seconds: 10));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  Future<bool> deleteSchedule(int id) async {
    try {
      final r = await http
          .delete(_uri('/api/schedule/$id'))
          .timeout(const Duration(seconds: 10));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Alerts ──
  Future<List<AlertLog>> getAlerts({int limit = 20}) async {
    final r = await _getList('/api/alerts/', {'limit': '$limit'});
    if (r == null) return [];
    return r.map((e) => AlertLog.fromJson(e as Map<String, dynamic>)).toList();
  }

  Future<bool> resolveAlert(int id) async {
    try {
      final r = await http
          .put(_uri('/api/alerts/$id/resolve'))
          .timeout(const Duration(seconds: 10));
      return r.statusCode == 200;
    } catch (_) {
      return false;
    }
  }

  // ── Push ──
  Future<bool> registerFcmToken(String token, {String deviceName = ''}) async {
    final r = await _post(
        '/api/push/register', {'token': token, 'device_name': deviceName});
    return r != null;
  }
}
