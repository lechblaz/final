/**
 * Import API client
 */
import { apiClient } from './client';
import type { ImportBatch, ImportBatchListResponse } from '../types/transaction';

export const importsApi = {
  /**
   * Upload CSV file for import
   */
  async uploadCsv(file: File): Promise<ImportBatch> {
    const formData = new FormData();
    formData.append('file', file);

    const response = await apiClient.post<ImportBatch>(
      '/api/v1/imports/upload',
      formData,
      {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      }
    );
    return response.data;
  },

  /**
   * Get list of import batches
   */
  async getImports(params: { limit?: number; offset?: number; status?: string } = {}): Promise<ImportBatchListResponse> {
    const response = await apiClient.get<ImportBatchListResponse>('/api/v1/imports', { params });
    return response.data;
  },

  /**
   * Get single import batch by ID
   */
  async getImport(id: string): Promise<ImportBatch> {
    const response = await apiClient.get<ImportBatch>(`/api/v1/imports/${id}`);
    return response.data;
  },
};
