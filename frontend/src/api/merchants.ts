import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface MerchantWithStats {
  id: string
  normalized_name: string
  display_name: string
  category: string | null
  logo_url: string | null
  website: string | null
  created_at: string | null
  updated_at: string | null
  transaction_count: number
  store_count: number
  total_spent: number
}

export interface MerchantListResponse {
  merchants: MerchantWithStats[]
  total: number
}

export const merchantsApi = {
  /**
   * Discover merchants from transactions
   */
  discoverMerchants: async (params?: {
    limit?: number
    offset?: number
    min_transactions?: number
  }): Promise<MerchantListResponse> => {
    const response = await axios.get(`${API_URL}/api/v1/merchants/discover`, {
      params,
    })
    return response.data
  },

  /**
   * List merchants
   */
  listMerchants: async (params?: {
    limit?: number
    offset?: number
    search?: string
  }): Promise<MerchantListResponse> => {
    const response = await axios.get(`${API_URL}/api/v1/merchants`, {
      params,
    })
    return response.data
  },
}
