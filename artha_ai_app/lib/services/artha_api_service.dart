import 'dart:convert';
import 'package:http/http.dart' as http;
import 'package:flutter_secure_storage/flutter_secure_storage.dart';

class ArthaApiService {
  // Change this to your backend URL when deployed
  static const String baseUrl = 'http://localhost:5000';
  // For Android emulator, use: 'http://10.0.2.2:5000'
  // For iOS simulator, use: 'http://localhost:5000'
  // For physical device, use your computer's IP: 'http://192.168.1.xxx:5000'
  
  final _storage = const FlutterSecureStorage();
  late http.Client _client;

  ArthaApiService({http.Client? client}) {
    _client = client ?? http.Client();
  }

  Future<Map<String, String>> _getHeaders() async {
    return {
      'Content-Type': 'application/json',
      'Accept': 'application/json',
    };
  }

  Future<Map<String, dynamic>> sendChatMessage(
    String message, 
    {String? userId, String? sessionId}
  ) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/api/chat'),
        headers: await _getHeaders(),
        body: json.encode({
          'message': message,
          'user_id': userId ?? 'demo_user',
          'session_id': sessionId ?? _generateSessionId(),
        }),
      ).timeout(const Duration(seconds: 30));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Failed to send chat message: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getAgentDiscussion(String sessionId) async {
    try {
      final response = await _client.post(
        Uri.parse('$baseUrl/api/agent-discussion'),
        headers: await _getHeaders(),
        body: json.encode({
          'session_id': sessionId,
        }),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Failed to get agent discussion: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getFinancialData({String? userId}) async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/api/financial-data/${userId ?? 'demo_user'}'),
        headers: await _getHeaders(),
      ).timeout(const Duration(seconds: 15));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Failed to get financial data: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> getMarketData() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/api/market-data'),
        headers: await _getHeaders(),
      ).timeout(const Duration(seconds: 10));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Failed to get market data: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Network error: $e');
    }
  }

  Future<Map<String, dynamic>> checkHealth() async {
    try {
      final response = await _client.get(
        Uri.parse('$baseUrl/api/health'),
        headers: await _getHeaders(),
      ).timeout(const Duration(seconds: 5));

      if (response.statusCode == 200) {
        return json.decode(response.body);
      } else {
        throw ApiException('Health check failed: ${response.statusCode}');
      }
    } catch (e) {
      if (e is ApiException) rethrow;
      throw ApiException('Network error: $e');
    }
  }

  String _generateSessionId() {
    final timestamp = DateTime.now().millisecondsSinceEpoch;
    return 'session_$timestamp';
  }

  void dispose() {
    _client.close();
  }
}

class ApiException implements Exception {
  final String message;
  ApiException(this.message);

  @override
  String toString() => 'ApiException: $message';
}