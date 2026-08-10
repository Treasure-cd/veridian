-- migrations/032_vfs_indexes.sql
CREATE INDEX idx_wallet_accounts_customer ON wallet_accounts(customer_id);
CREATE INDEX idx_wallet_accounts_account_ref ON wallet_accounts(account_ref_id);

CREATE INDEX idx_wallet_txn_wallet ON wallet_transactions(wallet_id);
CREATE INDEX idx_wallet_txn_date ON wallet_transactions(transaction_date);

CREATE INDEX idx_loans_customer ON loans(borrower_customer_id);
CREATE INDEX idx_loans_supplier ON loans(borrower_supplier_id);
CREATE INDEX idx_loans_status ON loans(status);

CREATE INDEX idx_repayments_loan ON loan_repayments(loan_id);
CREATE INDEX idx_repayments_due_date ON loan_repayments(due_date);

CREATE INDEX idx_kyc_customer ON kyc_records(customer_id);

CREATE INDEX idx_settlements_division ON merchant_settlements(division_id);
