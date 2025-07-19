class EpfDetailsResponse {
  final List<UanAccount> uanAccounts;

  EpfDetailsResponse({
    required this.uanAccounts,
  });

  factory EpfDetailsResponse.fromJson(Map<String, dynamic> json) {
    return EpfDetailsResponse(
      uanAccounts: (json['uanAccounts'] as List<dynamic>?)
          ?.map((e) => UanAccount.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'uanAccounts': uanAccounts.map((e) => e.toJson()).toList(),
    };
  }

  UanAccount? get primaryAccount => uanAccounts.isNotEmpty ? uanAccounts.first : null;
}

class UanAccount {
  final Map<String, dynamic> phoneNumber;
  final RawDetails rawDetails;

  UanAccount({
    required this.phoneNumber,
    required this.rawDetails,
  });

  factory UanAccount.fromJson(Map<String, dynamic> json) {
    return UanAccount(
      phoneNumber: json['phoneNumber'] ?? {},
      rawDetails: RawDetails.fromJson(json['rawDetails'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'phoneNumber': phoneNumber,
      'rawDetails': rawDetails.toJson(),
    };
  }
}

class RawDetails {
  final List<EstablishmentDetail> estDetails;
  final OverallPfBalance overallPfBalance;

  RawDetails({
    required this.estDetails,
    required this.overallPfBalance,
  });

  factory RawDetails.fromJson(Map<String, dynamic> json) {
    return RawDetails(
      estDetails: (json['est_details'] as List<dynamic>?)
          ?.map((e) => EstablishmentDetail.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
      overallPfBalance: OverallPfBalance.fromJson(json['overall_pf_balance'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'est_details': estDetails.map((e) => e.toJson()).toList(),
      'overall_pf_balance': overallPfBalance.toJson(),
    };
  }
}

class EstablishmentDetail {
  final String estName;
  final String memberId;
  final String office;
  final String dojEpf;
  final String doeEpf;
  final String doeEps;
  final PfBalance pfBalance;

  EstablishmentDetail({
    required this.estName,
    required this.memberId,
    required this.office,
    required this.dojEpf,
    required this.doeEpf,
    required this.doeEps,
    required this.pfBalance,
  });

  factory EstablishmentDetail.fromJson(Map<String, dynamic> json) {
    return EstablishmentDetail(
      estName: json['est_name'] ?? '',
      memberId: json['member_id'] ?? '',
      office: json['office'] ?? '',
      dojEpf: json['doj_epf'] ?? '',
      doeEpf: json['doe_epf'] ?? '',
      doeEps: json['doe_eps'] ?? '',
      pfBalance: PfBalance.fromJson(json['pf_balance'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'est_name': estName,
      'member_id': memberId,
      'office': office,
      'doj_epf': dojEpf,
      'doe_epf': doeEpf,
      'doe_eps': doeEps,
      'pf_balance': pfBalance.toJson(),
    };
  }

  DateTime? get dateOfJoining {
    try {
      final parts = dojEpf.split('-');
      if (parts.length == 3) {
        final day = int.parse(parts[0]);
        final month = int.parse(parts[1]);
        final year = int.parse(parts[2]);
        return DateTime(year, month, day);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  DateTime? get dateOfExit {
    try {
      final parts = doeEpf.split('-');
      if (parts.length == 3) {
        final day = int.parse(parts[0]);
        final month = int.parse(parts[1]);
        final year = int.parse(parts[2]);
        return DateTime(year, month, day);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  Duration? get serviceDuration {
    final joining = dateOfJoining;
    final exit = dateOfExit;
    if (joining != null && exit != null) {
      return exit.difference(joining);
    }
    return null;
  }

  String get formattedServiceDuration {
    final duration = serviceDuration;
    if (duration != null) {
      final years = duration.inDays ~/ 365;
      final months = (duration.inDays % 365) ~/ 30;
      return '$years years, $months months';
    }
    return 'N/A';
  }

  bool get isActive => doeEpf.isEmpty || doeEpf == '02-01-2022'; // Assuming current date logic
}

class PfBalance {
  final String? netBalance;
  final bool? isPfFullWithdrawn;
  final EmployeeShare employeeShare;
  final EmployerShare employerShare;

  PfBalance({
    this.netBalance,
    this.isPfFullWithdrawn,
    required this.employeeShare,
    required this.employerShare,
  });

  factory PfBalance.fromJson(Map<String, dynamic> json) {
    return PfBalance(
      netBalance: json['net_balance'],
      isPfFullWithdrawn: json['is_pf_full_withdrawn'],
      employeeShare: EmployeeShare.fromJson(json['employee_share'] ?? {}),
      employerShare: EmployerShare.fromJson(json['employer_share'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'net_balance': netBalance,
      'is_pf_full_withdrawn': isPfFullWithdrawn,
      'employee_share': employeeShare.toJson(),
      'employer_share': employerShare.toJson(),
    };
  }

  double get totalBalance {
    return employeeShare.balanceAmount + employerShare.balanceAmount;
  }

  String get formattedTotalBalance {
    final balance = totalBalance;
    if (balance >= 10000000) {
      return '₹${(balance / 10000000).toStringAsFixed(1)}Cr';
    } else if (balance >= 100000) {
      return '₹${(balance / 100000).toStringAsFixed(1)}L';
    } else if (balance >= 1000) {
      return '₹${(balance / 1000).toStringAsFixed(1)}K';
    } else {
      return '₹${balance.toStringAsFixed(0)}';
    }
  }
}

class EmployeeShare {
  final String? debit;
  final String? credit;
  final String? balance;

  EmployeeShare({
    this.debit,
    this.credit,
    this.balance,
  });

  factory EmployeeShare.fromJson(Map<String, dynamic> json) {
    return EmployeeShare(
      debit: json['debit'],
      credit: json['credit'],
      balance: json['balance'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debit': debit,
      'credit': credit,
      'balance': balance,
    };
  }

  double get balanceAmount => double.tryParse(balance ?? '0') ?? 0.0;
  double get creditAmount => double.tryParse(credit ?? '0') ?? 0.0;
  double get debitAmount => double.tryParse(debit ?? '0') ?? 0.0;
}

class EmployerShare {
  final String? debit;
  final String? credit;
  final String? balance;

  EmployerShare({
    this.debit,
    this.credit,
    this.balance,
  });

  factory EmployerShare.fromJson(Map<String, dynamic> json) {
    return EmployerShare(
      debit: json['debit'],
      credit: json['credit'],
      balance: json['balance'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debit': debit,
      'credit': credit,
      'balance': balance,
    };
  }

  double get balanceAmount => double.tryParse(balance ?? '0') ?? 0.0;
  double get creditAmount => double.tryParse(credit ?? '0') ?? 0.0;
  double get debitAmount => double.tryParse(debit ?? '0') ?? 0.0;
}

class OverallPfBalance {
  final String? pensionBalance;
  final String currentPfBalance;
  final EmployeeShareTotal employeeShareTotal;
  final EmployerShareTotal? employerShareTotal;

  OverallPfBalance({
    this.pensionBalance,
    required this.currentPfBalance,
    required this.employeeShareTotal,
    this.employerShareTotal,
  });

  factory OverallPfBalance.fromJson(Map<String, dynamic> json) {
    return OverallPfBalance(
      pensionBalance: json['pension_balance'],
      currentPfBalance: json['current_pf_balance'] ?? '0',
      employeeShareTotal: EmployeeShareTotal.fromJson(json['employee_share_total'] ?? {}),
      employerShareTotal: json['employer_share_total'] != null
          ? EmployerShareTotal.fromJson(json['employer_share_total'] as Map<String, dynamic>)
          : null,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'pension_balance': pensionBalance,
      'current_pf_balance': currentPfBalance,
      'employee_share_total': employeeShareTotal.toJson(),
      'employer_share_total': employerShareTotal?.toJson(),
    };
  }

  double get totalCurrentBalance => double.tryParse(currentPfBalance) ?? 0.0;
  double get totalPensionBalance => double.tryParse(pensionBalance ?? '0') ?? 0.0;

  String get formattedCurrentBalance {
    final balance = totalCurrentBalance;
    if (balance >= 10000000) {
      return '₹${(balance / 10000000).toStringAsFixed(1)}Cr';
    } else if (balance >= 100000) {
      return '₹${(balance / 100000).toStringAsFixed(1)}L';
    } else if (balance >= 1000) {
      return '₹${(balance / 1000).toStringAsFixed(1)}K';
    } else {
      return '₹${balance.toStringAsFixed(0)}';
    }
  }

  String get formattedPensionBalance {
    final balance = totalPensionBalance;
    if (balance >= 10000000) {
      return '₹${(balance / 10000000).toStringAsFixed(1)}Cr';
    } else if (balance >= 100000) {
      return '₹${(balance / 100000).toStringAsFixed(1)}L';
    } else if (balance >= 1000) {
      return '₹${(balance / 1000).toStringAsFixed(1)}K';
    } else {
      return '₹${balance.toStringAsFixed(0)}';
    }
  }

  /// Calculate estimated retirement corpus based on age and contribution rate
  double calculateRetirementCorpus(int currentAge, double monthlyContribution) {
    const int retirementAge = 58;
    const double interestRate = 0.085; // 8.5% annual interest rate
    
    final yearsToRetirement = retirementAge - currentAge;
    if (yearsToRetirement <= 0) return totalCurrentBalance;
    
    final monthlyRate = interestRate / 12;
    final totalMonths = yearsToRetirement * 12;
    
    // Future value of current balance
    final futureValueOfCurrent = totalCurrentBalance * 
        (1 + interestRate) * yearsToRetirement;
    
    // Future value of monthly contributions
    final futureValueOfContributions = monthlyContribution * 
        ((1 + monthlyRate) * totalMonths - 1) / monthlyRate;
    
    return futureValueOfCurrent + futureValueOfContributions;
  }

  String getRetirementProjection(int currentAge, double monthlyContribution) {
    final corpus = calculateRetirementCorpus(currentAge, monthlyContribution);
    if (corpus >= 10000000) {
      return '₹${(corpus / 10000000).toStringAsFixed(1)}Cr';
    } else if (corpus >= 100000) {
      return '₹${(corpus / 100000).toStringAsFixed(1)}L';
    } else {
      return '₹${corpus.toStringAsFixed(0)}';
    }
  }
}

class EmployeeShareTotal {
  final String? debit;
  final String? credit;
  final String? balance;

  EmployeeShareTotal({
    this.debit,
    this.credit,
    this.balance,
  });

  factory EmployeeShareTotal.fromJson(Map<String, dynamic> json) {
    return EmployeeShareTotal(
      debit: json['debit'],
      credit: json['credit'],
      balance: json['balance'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debit': debit,
      'credit': credit,
      'balance': balance,
    };
  }

  double get balanceAmount => double.tryParse(balance ?? '0') ?? 0.0;
  double get creditAmount => double.tryParse(credit ?? '0') ?? 0.0;
  double get debitAmount => double.tryParse(debit ?? '0') ?? 0.0;
}

class EmployerShareTotal {
  final String? debit;
  final String? credit;
  final String? balance;

  EmployerShareTotal({
    this.debit,
    this.credit,
    this.balance,
  });

  factory EmployerShareTotal.fromJson(Map<String, dynamic> json) {
    return EmployerShareTotal(
      debit: json['debit'],
      credit: json['credit'],
      balance: json['balance'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'debit': debit,
      'credit': credit,
      'balance': balance,
    };
  }

  double get balanceAmount => double.tryParse(balance ?? '0') ?? 0.0;
  double get creditAmount => double.tryParse(credit ?? '0') ?? 0.0;
  double get debitAmount => double.tryParse(debit ?? '0') ?? 0.0;
}