class CreditReportResponse {
  final List<CreditReport> creditReports;

  CreditReportResponse({
    required this.creditReports,
  });

  factory CreditReportResponse.fromJson(Map<String, dynamic> json) {
    return CreditReportResponse(
      creditReports: (json['creditReports'] as List<dynamic>?)
          ?.map((e) => CreditReport.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'creditReports': creditReports.map((e) => e.toJson()).toList(),
    };
  }

  CreditReport? get primaryReport => creditReports.isNotEmpty ? creditReports.first : null;
}

class CreditReport {
  final CreditReportData creditReportData;
  final String vendor;

  CreditReport({
    required this.creditReportData,
    required this.vendor,
  });

  factory CreditReport.fromJson(Map<String, dynamic> json) {
    return CreditReport(
      creditReportData: CreditReportData.fromJson(json['creditReportData'] ?? {}),
      vendor: json['vendor'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'creditReportData': creditReportData.toJson(),
      'vendor': vendor,
    };
  }
}

class CreditReportData {
  final UserMessage userMessage;
  final CreditProfileHeader creditProfileHeader;
  final CurrentApplication currentApplication;
  final CreditAccount creditAccount;
  final Score score;
  final TotalCapsSummary totalCapsSummary;
  final NonCreditCaps nonCreditCaps;
  final Caps caps;

  CreditReportData({
    required this.userMessage,
    required this.creditProfileHeader,
    required this.currentApplication,
    required this.creditAccount,
    required this.score,
    required this.totalCapsSummary,
    required this.nonCreditCaps,
    required this.caps,
  });

  factory CreditReportData.fromJson(Map<String, dynamic> json) {
    return CreditReportData(
      userMessage: UserMessage.fromJson(json['userMessage'] ?? {}),
      creditProfileHeader: CreditProfileHeader.fromJson(json['creditProfileHeader'] ?? {}),
      currentApplication: CurrentApplication.fromJson(json['currentApplication'] ?? {}),
      creditAccount: CreditAccount.fromJson(json['creditAccount'] ?? {}),
      score: Score.fromJson(json['score'] ?? {}),
      totalCapsSummary: TotalCapsSummary.fromJson(json['totalCapsSummary'] ?? {}),
      nonCreditCaps: NonCreditCaps.fromJson(json['nonCreditCaps'] ?? {}),
      caps: Caps.fromJson(json['caps'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userMessage': userMessage.toJson(),
      'creditProfileHeader': creditProfileHeader.toJson(),
      'currentApplication': currentApplication.toJson(),
      'creditAccount': creditAccount.toJson(),
      'score': score.toJson(),
      'totalCapsSummary': totalCapsSummary.toJson(),
      'nonCreditCaps': nonCreditCaps.toJson(),
      'caps': caps.toJson(),
    };
  }
}

class UserMessage {
  final String userMessageText;

  UserMessage({
    required this.userMessageText,
  });

  factory UserMessage.fromJson(Map<String, dynamic> json) {
    return UserMessage(
      userMessageText: json['userMessageText'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'userMessageText': userMessageText,
    };
  }
}

class CreditProfileHeader {
  final String reportDate;
  final String reportTime;

  CreditProfileHeader({
    required this.reportDate,
    required this.reportTime,
  });

  factory CreditProfileHeader.fromJson(Map<String, dynamic> json) {
    return CreditProfileHeader(
      reportDate: json['reportDate'] ?? '',
      reportTime: json['reportTime'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'reportDate': reportDate,
      'reportTime': reportTime,
    };
  }

  DateTime get reportDateTime {
    try {
      final dateStr = reportDate.length == 8 ? reportDate : '${reportDate}01';
      final timeStr = reportTime.length == 6 ? reportTime : '${reportTime}00';
      
      final year = int.parse(dateStr.substring(0, 4));
      final month = int.parse(dateStr.substring(4, 6));
      final day = int.parse(dateStr.substring(6, 8));
      
      final hour = int.parse(timeStr.substring(0, 2));
      final minute = int.parse(timeStr.substring(2, 4));
      final second = int.parse(timeStr.substring(4, 6));
      
      return DateTime(year, month, day, hour, minute, second);
    } catch (e) {
      return DateTime.now();
    }
  }
}

class CurrentApplication {
  final CurrentApplicationDetails currentApplicationDetails;

  CurrentApplication({
    required this.currentApplicationDetails,
  });

  factory CurrentApplication.fromJson(Map<String, dynamic> json) {
    return CurrentApplication(
      currentApplicationDetails: CurrentApplicationDetails.fromJson(
        json['currentApplicationDetails'] ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'currentApplicationDetails': currentApplicationDetails.toJson(),
    };
  }
}

class CurrentApplicationDetails {
  final String enquiryReason;
  final String amountFinanced;
  final String durationOfAgreement;
  final CurrentApplicantDetails currentApplicantDetails;

  CurrentApplicationDetails({
    required this.enquiryReason,
    required this.amountFinanced,
    required this.durationOfAgreement,
    required this.currentApplicantDetails,
  });

  factory CurrentApplicationDetails.fromJson(Map<String, dynamic> json) {
    return CurrentApplicationDetails(
      enquiryReason: json['enquiryReason'] ?? '',
      amountFinanced: json['amountFinanced'] ?? '',
      durationOfAgreement: json['durationOfAgreement'] ?? '',
      currentApplicantDetails: CurrentApplicantDetails.fromJson(
        json['currentApplicantDetails'] ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'enquiryReason': enquiryReason,
      'amountFinanced': amountFinanced,
      'durationOfAgreement': durationOfAgreement,
      'currentApplicantDetails': currentApplicantDetails.toJson(),
    };
  }
}

class CurrentApplicantDetails {
  final String dateOfBirthApplicant;

  CurrentApplicantDetails({
    required this.dateOfBirthApplicant,
  });

  factory CurrentApplicantDetails.fromJson(Map<String, dynamic> json) {
    return CurrentApplicantDetails(
      dateOfBirthApplicant: json['dateOfBirthApplicant'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'dateOfBirthApplicant': dateOfBirthApplicant,
    };
  }

  DateTime? get dateOfBirth {
    try {
      if (dateOfBirthApplicant.length == 8) {
        final year = int.parse(dateOfBirthApplicant.substring(0, 4));
        final month = int.parse(dateOfBirthApplicant.substring(4, 6));
        final day = int.parse(dateOfBirthApplicant.substring(6, 8));
        return DateTime(year, month, day);
      }
      return null;
    } catch (e) {
      return null;
    }
  }

  int? get age {
    final dob = dateOfBirth;
    if (dob != null) {
      final now = DateTime.now();
      int age = now.year - dob.year;
      if (now.month < dob.month || (now.month == dob.month && now.day < dob.day)) {
        age--;
      }
      return age;
    }
    return null;
  }
}

class CreditAccount {
  final CreditAccountSummary creditAccountSummary;
  final List<CreditAccountDetail> creditAccountDetails;

  CreditAccount({
    required this.creditAccountSummary,
    required this.creditAccountDetails,
  });

  factory CreditAccount.fromJson(Map<String, dynamic> json) {
    return CreditAccount(
      creditAccountSummary: CreditAccountSummary.fromJson(
        json['creditAccountSummary'] ?? {}
      ),
      creditAccountDetails: (json['creditAccountDetails'] as List<dynamic>?)
          ?.map((e) => CreditAccountDetail.fromJson(e as Map<String, dynamic>))
          .toList() ?? [],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'creditAccountSummary': creditAccountSummary.toJson(),
      'creditAccountDetails': creditAccountDetails.map((e) => e.toJson()).toList(),
    };
  }
}

class CreditAccountSummary {
  final Account account;
  final TotalOutstandingBalance totalOutstandingBalance;

  CreditAccountSummary({
    required this.account,
    required this.totalOutstandingBalance,
  });

  factory CreditAccountSummary.fromJson(Map<String, dynamic> json) {
    return CreditAccountSummary(
      account: Account.fromJson(json['account'] ?? {}),
      totalOutstandingBalance: TotalOutstandingBalance.fromJson(
        json['totalOutstandingBalance'] ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'account': account.toJson(),
      'totalOutstandingBalance': totalOutstandingBalance.toJson(),
    };
  }
}

class Account {
  final String creditAccountTotal;
  final String creditAccountActive;
  final String creditAccountDefault;
  final String creditAccountClosed;
  final String cadSuitFiledCurrentBalance;

  Account({
    required this.creditAccountTotal,
    required this.creditAccountActive,
    required this.creditAccountDefault,
    required this.creditAccountClosed,
    required this.cadSuitFiledCurrentBalance,
  });

  factory Account.fromJson(Map<String, dynamic> json) {
    return Account(
      creditAccountTotal: json['creditAccountTotal'] ?? '0',
      creditAccountActive: json['creditAccountActive'] ?? '0',
      creditAccountDefault: json['creditAccountDefault'] ?? '0',
      creditAccountClosed: json['creditAccountClosed'] ?? '0',
      cadSuitFiledCurrentBalance: json['cadSuitFiledCurrentBalance'] ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'creditAccountTotal': creditAccountTotal,
      'creditAccountActive': creditAccountActive,
      'creditAccountDefault': creditAccountDefault,
      'creditAccountClosed': creditAccountClosed,
      'cadSuitFiledCurrentBalance': cadSuitFiledCurrentBalance,
    };
  }

  int get totalAccounts => int.tryParse(creditAccountTotal) ?? 0;
  int get activeAccounts => int.tryParse(creditAccountActive) ?? 0;
  int get defaultAccounts => int.tryParse(creditAccountDefault) ?? 0;
  int get closedAccounts => int.tryParse(creditAccountClosed) ?? 0;
}

class TotalOutstandingBalance {
  final String outstandingBalanceSecured;
  final String outstandingBalanceSecuredPercentage;
  final String outstandingBalanceUnSecured;
  final String outstandingBalanceUnSecuredPercentage;
  final String outstandingBalanceAll;

  TotalOutstandingBalance({
    required this.outstandingBalanceSecured,
    required this.outstandingBalanceSecuredPercentage,
    required this.outstandingBalanceUnSecured,
    required this.outstandingBalanceUnSecuredPercentage,
    required this.outstandingBalanceAll,
  });

  factory TotalOutstandingBalance.fromJson(Map<String, dynamic> json) {
    return TotalOutstandingBalance(
      outstandingBalanceSecured: json['outstandingBalanceSecured'] ?? '0',
      outstandingBalanceSecuredPercentage: json['outstandingBalanceSecuredPercentage'] ?? '0',
      outstandingBalanceUnSecured: json['outstandingBalanceUnSecured'] ?? '0',
      outstandingBalanceUnSecuredPercentage: json['outstandingBalanceUnSecuredPercentage'] ?? '0',
      outstandingBalanceAll: json['outstandingBalanceAll'] ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'outstandingBalanceSecured': outstandingBalanceSecured,
      'outstandingBalanceSecuredPercentage': outstandingBalanceSecuredPercentage,
      'outstandingBalanceUnSecured': outstandingBalanceUnSecured,
      'outstandingBalanceUnSecuredPercentage': outstandingBalanceUnSecuredPercentage,
      'outstandingBalanceAll': outstandingBalanceAll,
    };
  }

  double get totalOutstanding => double.tryParse(outstandingBalanceAll) ?? 0.0;
  double get securedAmount => double.tryParse(outstandingBalanceSecured) ?? 0.0;
  double get unsecuredAmount => double.tryParse(outstandingBalanceUnSecured) ?? 0.0;
}

class CreditAccountDetail {
  final String subscriberName;
  final String portfolioType;
  final String accountType;
  final String openDate;
  final String? creditLimitAmount;
  final String highestCreditOrOriginalLoanAmount;
  final String accountStatus;
  final String paymentRating;
  final String paymentHistoryProfile;
  final String currentBalance;
  final String amountPastDue;
  final String dateReported;
  final String? rateOfInterest;
  final String repaymentTenure;
  final String dateOfAddition;
  final String currencyCode;
  final String accountHolderTypeCode;

  CreditAccountDetail({
    required this.subscriberName,
    required this.portfolioType,
    required this.accountType,
    required this.openDate,
    this.creditLimitAmount,
    required this.highestCreditOrOriginalLoanAmount,
    required this.accountStatus,
    required this.paymentRating,
    required this.paymentHistoryProfile,
    required this.currentBalance,
    required this.amountPastDue,
    required this.dateReported,
    this.rateOfInterest,
    required this.repaymentTenure,
    required this.dateOfAddition,
    required this.currencyCode,
    required this.accountHolderTypeCode,
  });

  factory CreditAccountDetail.fromJson(Map<String, dynamic> json) {
    return CreditAccountDetail(
      subscriberName: json['subscriberName'] ?? '',
      portfolioType: json['portfolioType'] ?? '',
      accountType: json['accountType'] ?? '',
      openDate: json['openDate'] ?? '',
      creditLimitAmount: json['creditLimitAmount'],
      highestCreditOrOriginalLoanAmount: json['highestCreditOrOriginalLoanAmount'] ?? '',
      accountStatus: json['accountStatus'] ?? '',
      paymentRating: json['paymentRating'] ?? '',
      paymentHistoryProfile: json['paymentHistoryProfile'] ?? '',
      currentBalance: json['currentBalance'] ?? '',
      amountPastDue: json['amountPastDue'] ?? '',
      dateReported: json['dateReported'] ?? '',
      rateOfInterest: json['rateOfInterest'],
      repaymentTenure: json['repaymentTenure'] ?? '',
      dateOfAddition: json['dateOfAddition'] ?? '',
      currencyCode: json['currencyCode'] ?? '',
      accountHolderTypeCode: json['accountHolderTypeCode'] ?? '',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'subscriberName': subscriberName,
      'portfolioType': portfolioType,
      'accountType': accountType,
      'openDate': openDate,
      'creditLimitAmount': creditLimitAmount,
      'highestCreditOrOriginalLoanAmount': highestCreditOrOriginalLoanAmount,
      'accountStatus': accountStatus,
      'paymentRating': paymentRating,
      'paymentHistoryProfile': paymentHistoryProfile,
      'currentBalance': currentBalance,
      'amountPastDue': amountPastDue,
      'dateReported': dateReported,
      'rateOfInterest': rateOfInterest,
      'repaymentTenure': repaymentTenure,
      'dateOfAddition': dateOfAddition,
      'currencyCode': currencyCode,
      'accountHolderTypeCode': accountHolderTypeCode,
    };
  }

  String get accountTypeName {
    switch (accountType) {
      case '01':
        return 'Auto Loan';
      case '02':
        return 'Housing Loan';
      case '03':
        return 'Property Loan';
      case '04':
        return 'Loan Against Property';
      case '05':
        return 'Overdraft';
      case '06':
        return 'Credit Card';
      case '07':
        return 'Personal Loan';
      case '08':
        return 'Consumer Loan';
      case '09':
        return 'Gold Loan';
      case '10':
        return 'Credit Card';
      case '53':
        return 'Business Loan';
      default:
        return 'Other';
    }
  }

  String get statusName {
    switch (accountStatus) {
      case '11':
        return 'Active';
      case '21':
        return 'Closed';
      case '71':
        return 'Settled';
      case '78':
        return 'Written Off';
      case '82':
        return 'Default';
      case '83':
        return 'Suit Filed';
      default:
        return 'Unknown';
    }
  }

  double get currentBalanceAmount => double.tryParse(currentBalance) ?? 0.0;
  double get pastDueAmount => double.tryParse(amountPastDue) ?? 0.0;
  double get interestRate => double.tryParse(rateOfInterest ?? '0') ?? 0.0;
  double get creditLimit => double.tryParse(creditLimitAmount ?? '0') ?? 0.0;
  double get originalLoanAmount => double.tryParse(highestCreditOrOriginalLoanAmount) ?? 0.0;

  bool get isActive => accountStatus == '11';
  bool get isDefaulter => pastDueAmount > 0;
  bool get isCreditCard => accountType == '10' || accountType == '06';
}

class Score {
  final String bureauScore;
  final String? bureauScoreConfidenceLevel;

  Score({
    required this.bureauScore,
    this.bureauScoreConfidenceLevel,
  });

  factory Score.fromJson(Map<String, dynamic> json) {
    return Score(
      bureauScore: json['bureauScore'] ?? '0',
      bureauScoreConfidenceLevel: json['bureauScoreConfidenceLevel'],
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'bureauScore': bureauScore,
      'bureauScoreConfidenceLevel': bureauScoreConfidenceLevel,
    };
  }

  int get score => int.tryParse(bureauScore) ?? 0;

  String get scoreCategory {
    final scoreValue = score;
    if (scoreValue >= 750) return 'Excellent';
    if (scoreValue >= 700) return 'Good';
    if (scoreValue >= 650) return 'Fair';
    if (scoreValue >= 600) return 'Poor';
    return 'Very Poor';
  }

  String get scoreDescription {
    final scoreValue = score;
    if (scoreValue >= 750) return 'You have an excellent credit score. You\'re likely to get the best rates and terms.';
    if (scoreValue >= 700) return 'You have a good credit score. You should qualify for competitive rates.';
    if (scoreValue >= 650) return 'You have a fair credit score. You may face some challenges getting the best rates.';
    if (scoreValue >= 600) return 'You have a poor credit score. Consider working on improving it.';
    return 'You have a very poor credit score. Focus on improving your credit habits.';
  }
}

class TotalCapsSummary {
  final String totalCapsLast7Days;
  final String totalCapsLast30Days;
  final String totalCapsLast90Days;
  final String totalCapsLast180Days;

  TotalCapsSummary({
    required this.totalCapsLast7Days,
    required this.totalCapsLast30Days,
    required this.totalCapsLast90Days,
    required this.totalCapsLast180Days,
  });

  factory TotalCapsSummary.fromJson(Map<String, dynamic> json) {
    return TotalCapsSummary(
      totalCapsLast7Days: json['totalCapsLast7Days'] ?? '0',
      totalCapsLast30Days: json['totalCapsLast30Days'] ?? '0',
      totalCapsLast90Days: json['totalCapsLast90Days'] ?? '0',
      totalCapsLast180Days: json['totalCapsLast180Days'] ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'totalCapsLast7Days': totalCapsLast7Days,
      'totalCapsLast30Days': totalCapsLast30Days,
      'totalCapsLast90Days': totalCapsLast90Days,
      'totalCapsLast180Days': totalCapsLast180Days,
    };
  }

  int get inquiries7Days => int.tryParse(totalCapsLast7Days) ?? 0;
  int get inquiries30Days => int.tryParse(totalCapsLast30Days) ?? 0;
  int get inquiries90Days => int.tryParse(totalCapsLast90Days) ?? 0;
  int get inquiries180Days => int.tryParse(totalCapsLast180Days) ?? 0;
}

class NonCreditCaps {
  final NonCreditCapsSummary nonCreditCapsSummary;

  NonCreditCaps({
    required this.nonCreditCapsSummary,
  });

  factory NonCreditCaps.fromJson(Map<String, dynamic> json) {
    return NonCreditCaps(
      nonCreditCapsSummary: NonCreditCapsSummary.fromJson(
        json['nonCreditCapsSummary'] ?? {}
      ),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nonCreditCapsSummary': nonCreditCapsSummary.toJson(),
    };
  }
}

class NonCreditCapsSummary {
  final String nonCreditCapsLast7Days;
  final String nonCreditCapsLast30Days;
  final String nonCreditCapsLast90Days;
  final String nonCreditCapsLast180Days;

  NonCreditCapsSummary({
    required this.nonCreditCapsLast7Days,
    required this.nonCreditCapsLast30Days,
    required this.nonCreditCapsLast90Days,
    required this.nonCreditCapsLast180Days,
  });

  factory NonCreditCapsSummary.fromJson(Map<String, dynamic> json) {
    return NonCreditCapsSummary(
      nonCreditCapsLast7Days: json['nonCreditCapsLast7Days'] ?? '0',
      nonCreditCapsLast30Days: json['nonCreditCapsLast30Days'] ?? '0',
      nonCreditCapsLast90Days: json['nonCreditCapsLast90Days'] ?? '0',
      nonCreditCapsLast180Days: json['nonCreditCapsLast180Days'] ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'nonCreditCapsLast7Days': nonCreditCapsLast7Days,
      'nonCreditCapsLast30Days': nonCreditCapsLast30Days,
      'nonCreditCapsLast90Days': nonCreditCapsLast90Days,
      'nonCreditCapsLast180Days': nonCreditCapsLast180Days,
    };
  }
}

class Caps {
  final CapsSummary capsSummary;

  Caps({
    required this.capsSummary,
  });

  factory Caps.fromJson(Map<String, dynamic> json) {
    return Caps(
      capsSummary: CapsSummary.fromJson(json['capsSummary'] ?? {}),
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'capsSummary': capsSummary.toJson(),
    };
  }
}

class CapsSummary {
  final String capsLast7Days;
  final String capsLast30Days;
  final String capsLast90Days;
  final String capsLast180Days;

  CapsSummary({
    required this.capsLast7Days,
    required this.capsLast30Days,
    required this.capsLast90Days,
    required this.capsLast180Days,
  });

  factory CapsSummary.fromJson(Map<String, dynamic> json) {
    return CapsSummary(
      capsLast7Days: json['capsLast7Days'] ?? '0',
      capsLast30Days: json['capsLast30Days'] ?? '0',
      capsLast90Days: json['capsLast90Days'] ?? '0',
      capsLast180Days: json['capsLast180Days'] ?? '0',
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'capsLast7Days': capsLast7Days,
      'capsLast30Days': capsLast30Days,
      'capsLast90Days': capsLast90Days,
      'capsLast180Days': capsLast180Days,
    };
  }
}