import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../../core/theme/app_colors.dart';
import '../../../core/theme/app_text_styles.dart';
import '../../../core/widgets/app_card.dart';
import '../../../core/widgets/main_layout.dart';
import '../../../core/services/navigation_service.dart';
import '../../fi_money/providers/fi_money_provider.dart';
import '../../fi_money/utils/data_formatters.dart';
import '../../fi_money/models/mf_transactions.dart';

class TransactionsScreen extends ConsumerStatefulWidget {
  const TransactionsScreen({Key? key}) : super(key: key);

  @override
  ConsumerState<TransactionsScreen> createState() => _TransactionsScreenState();
}

class _TransactionsScreenState extends ConsumerState<TransactionsScreen> {
  String selectedFilter = 'All';

  @override
  Widget build(BuildContext context) {
    final mfTransactionsState = ref.watch(mfTransactionsProvider);

    return AppScaffold(
      title: 'Transactions',
      body: Container(
        color: AppColors.background,
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24),
          child: Column(
            children: [
              _buildFilterChips(),
              const SizedBox(height: 16),
              _buildTransactionsList(mfTransactionsState),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildFilterChips() {
    return SingleChildScrollView(
      scrollDirection: Axis.horizontal,
      child: Row(
        children: [
          _buildFilterChip('All', selectedFilter == 'All'),
          const SizedBox(width: 8),
          _buildFilterChip('SIP', selectedFilter == 'SIP'),
          const SizedBox(width: 8),
          _buildFilterChip('Buy', selectedFilter == 'Buy'),
          const SizedBox(width: 8),
          _buildFilterChip('Sell', selectedFilter == 'Sell'),
        ],
      ),
    );
  }

  Widget _buildFilterChip(String label, bool isSelected) {
    return FilterChip(
      label: Text(label),
      selected: isSelected,
      onSelected: (selected) {
        if (selected) {
          setState(() {
            selectedFilter = label;
          });
        }
      },
      selectedColor: AppColors.primaryBlue.withOpacity(0.1),
      checkmarkColor: AppColors.primaryBlue,
    );
  }

  Widget _buildTransactionsList(MfTransactionsState mfTransactionsState) {
    if (mfTransactionsState.isLoading) {
      return _buildLoadingCard();
    } else if (mfTransactionsState.hasError) {
      return _buildErrorCard(mfTransactionsState.error!);
    } else if (mfTransactionsState.data != null) {
      return _buildTransactionsContent(mfTransactionsState.data!);
    } else {
      return _buildLoadingCard();
    }
  }

  Widget _buildTransactionsContent(MfTransactionsResponse transactions) {
    // Filter transactions based on selected filter
    List<MfTransaction> filteredTransactions = transactions.transactions;
    
    if (selectedFilter != 'All') {
      filteredTransactions = transactions.transactions.where((transaction) {
        switch (selectedFilter) {
          case 'SIP':
            return transaction.transactionMode.toLowerCase() == 'sip' || 
                   transaction.transactionMode.toLowerCase() == 'n';
          case 'Buy':
            return transaction.externalOrderType.toUpperCase() == 'BUY';
          case 'Sell':
            return transaction.externalOrderType.toUpperCase() == 'SELL';
          default:
            return true;
        }
      }).toList();
    }
    
    // Sort transactions by date (most recent first)
    filteredTransactions.sort((a, b) => 
        b.transactionDate.compareTo(a.transactionDate));

    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Row(
            mainAxisAlignment: MainAxisAlignment.spaceBetween,
            children: [
              Text(
                'Transactions',
                style: AppTextStyles.heading4,
              ),
              Text(
                '${filteredTransactions.length} transactions',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
            ],
          ),
          const SizedBox(height: 16),
          if (filteredTransactions.isEmpty)
            Center(
              child: Padding(
                padding: const EdgeInsets.all(32),
                child: Text(
                  'No transactions found for the selected filter',
                  style: AppTextStyles.bodyMedium.copyWith(
                    color: AppColors.grey600,
                  ),
                ),
              ),
            )
          else
            ...filteredTransactions.map((transaction) {
              String fundName = transaction.schemeName.length > 30
                  ? '${transaction.schemeName.substring(0, 27)}...'
                  : transaction.schemeName;
              
              String transactionType = _getTransactionTypeDisplay(transaction);
              String amount = DataFormatters.formatCurrency(transaction.transactionAmount.value);
              String date = DataFormatters.formatDate(transaction.transactionDate);
              bool isBuy = transaction.externalOrderType.toUpperCase() == 'BUY';
              
              return Padding(
                padding: const EdgeInsets.only(bottom: 12),
                child: _buildTransactionItem(
                  fundName,
                  transactionType,
                  amount,
                  date,
                  isBuy,
                  transaction,
                ),
              );
            }).toList(),
        ],
      ),
    );
  }

  String _getTransactionTypeDisplay(MfTransaction transaction) {
    String orderType = transaction.externalOrderType.toUpperCase();
    String mode = transaction.transactionMode.toLowerCase();
    
    if (mode == 'sip' || mode == 'n') {
      return 'SIP';
    } else if (orderType == 'BUY') {
      return 'Buy';
    } else if (orderType == 'SELL') {
      return 'Sell';
    } else {
      return orderType;
    }
  }

  Widget _buildLoadingCard() {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Transactions',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          const Center(
            child: CircularProgressIndicator(),
          ),
        ],
      ),
    );
  }

  Widget _buildErrorCard(String error) {
    return AppCard(
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          Text(
            'Transactions',
            style: AppTextStyles.heading4,
          ),
          const SizedBox(height: 16),
          Text(
            'Error loading transactions: $error',
            style: AppTextStyles.bodyMedium.copyWith(
              color: AppColors.error,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildTransactionItem(
    String fundName,
    String type,
    String amount,
    String date,
    bool isCredit,
    MfTransaction transaction,
  ) {
    return Row(
      children: [
        Container(
          padding: const EdgeInsets.all(8),
          decoration: BoxDecoration(
            color: isCredit
                ? AppColors.success.withOpacity(0.1)
                : AppColors.error.withOpacity(0.1),
            borderRadius: BorderRadius.circular(8),
          ),
          child: Icon(
            isCredit ? Icons.add : Icons.remove,
            color: isCredit ? AppColors.success : AppColors.error,
            size: 20,
          ),
        ),
        const SizedBox(width: 12),
        Expanded(
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                fundName,
                style: AppTextStyles.bodyMedium.copyWith(
                  fontWeight: FontWeight.w600,
                ),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 4),
              Row(
                children: [
                  Container(
                    padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 2),
                    decoration: BoxDecoration(
                      color: AppColors.grey200,
                      borderRadius: BorderRadius.circular(12),
                    ),
                    child: Text(
                      type,
                      style: AppTextStyles.labelSmall,
                    ),
                  ),
                  const SizedBox(width: 8),
                  Text(
                    date,
                    style: AppTextStyles.bodySmall.copyWith(
                      color: AppColors.grey600,
                    ),
                  ),
                  if (transaction.transactionUnits > 0) ...[
                    Text(
                      ' • ',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey400,
                      ),
                    ),
                    Text(
                      '${transaction.transactionUnits.toStringAsFixed(2)} units',
                      style: AppTextStyles.bodySmall.copyWith(
                        color: AppColors.grey600,
                      ),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
        Column(
          crossAxisAlignment: CrossAxisAlignment.end,
          children: [
            Text(
              amount,
              style: AppTextStyles.bodyMedium.copyWith(
                fontWeight: FontWeight.w600,
                color: isCredit ? AppColors.success : AppColors.error,
              ),
            ),
            if (transaction.purchasePrice.value > 0)
              Text(
                '@₹${transaction.purchasePrice.value.toStringAsFixed(2)}',
                style: AppTextStyles.bodySmall.copyWith(
                  color: AppColors.grey600,
                ),
              ),
          ],
        ),
      ],
    );
  }
}