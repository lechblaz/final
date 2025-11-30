/**
 * Transaction API client
 */
import { apiClient } from './client';
import type { Transaction, TransactionListResponse } from '../types/transaction';

export interface TransactionFilters {
  from_date?: string;
  to_date?: string;
  limit?: number;
  offset?: number;
}

export const transactionsApi = {
  /**
   * Get list of transactions with filters
   */
  async getTransactions(filters: TransactionFilters = {}): Promise<TransactionListResponse> {
    const response = await apiClient.get<TransactionListResponse>('/api/v1/transactions', {
      params: filters,
    });
    return response.data;
  },

  /**
   * Get single transaction by ID
   */
  async getTransaction(id: string): Promise<Transaction> {
    const response = await apiClient.get<Transaction>(`/api/v1/transactions/${id}`);
    return response.data;
  },

  /**
   * Update transaction
   */
  async updateTransaction(id: string, data: Partial<Transaction>): Promise<Transaction> {
    const response = await apiClient.patch<Transaction>(`/api/v1/transactions/${id}`, data);
    return response.data;
  },

  /**
   * Delete (hide) transaction
   */
  async deleteTransaction(id: string): Promise<void> {
    await apiClient.delete(`/api/v1/transactions/${id}`);
  },
};
