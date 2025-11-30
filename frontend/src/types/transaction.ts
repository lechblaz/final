/**
 * Transaction types matching backend API
 */

export interface Transaction {
  id: string;
  user_id: string;
  transaction_hash: string;
  booking_date: string;
  transaction_date: string;
  operation_type: string;
  title: string;
  sender_recipient: string | null;
  account_number: string | null;
  amount: number;
  balance_after: number | null;
  currency: string;
  // Merchant enrichment (Phase 2)
  normalized_merchant_name: string | null;
  store_identifier: string | null;
  location_extracted: string | null;
  raw_merchant_text: string | null;
  merchant_confidence: number | null;
  notes: string | null;
  is_hidden: boolean;
  created_at: string;
  updated_at: string;
}

export interface TransactionListResponse {
  transactions: Transaction[];
  total: number;
  page: number;
  page_size: number;
}

export interface ImportBatch {
  id: string;
  user_id: string;
  file_name: string;
  file_hash: string;
  account_number: string | null;
  account_type: string | null;
  currency: string;
  period_start: string | null;
  period_end: string | null;
  transactions_imported: number;
  duplicates_skipped: number;
  import_status: string;
  error_message: string | null;
  created_at: string;
}

export interface ImportBatchListResponse {
  imports: ImportBatch[];
  total: number;
}
