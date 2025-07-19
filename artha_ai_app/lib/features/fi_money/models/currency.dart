class Currency {
  final String currencyCode;
  final String? units;
  final int? nanos;

  Currency({
    required this.currencyCode,
    this.units,
    this.nanos,
  });

  factory Currency.fromJson(Map<String, dynamic> json) {
    return Currency(
      currencyCode: json['currencyCode'] ?? 'INR',
      units: json['units']?.toString(),
      nanos: json['nanos']?.toInt(),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'currencyCode': currencyCode,
      'units': units,
      'nanos': nanos,
    };
  }

  /// Converts the currency to a double value
  double get value {
    final unitsValue = double.tryParse(units ?? '0') ?? 0;
    final nanosValue = (nanos ?? 0) / 1000000000;
    return unitsValue + nanosValue;
  }

  /// Formats the currency value as a string
  String get formatted {
    return '₹${value.toStringAsFixed(2)}';
  }

  /// Formats the currency value as a compact string (e.g., ₹1.2L, ₹1.2Cr)
  String get formattedCompact {
    final val = value;
    if (val >= 10000000) {
      return '₹${(val / 10000000).toStringAsFixed(1)}Cr';
    } else if (val >= 100000) {
      return '₹${(val / 100000).toStringAsFixed(1)}L';
    } else if (val >= 1000) {
      return '₹${(val / 1000).toStringAsFixed(1)}K';
    } else {
      return '₹${val.toStringAsFixed(0)}';
    }
  }
}