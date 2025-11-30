import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface SankeyNode {
  id: string
  name: string
  color?: string
}

export interface SankeyLink {
  source: string
  target: string
  value: number
}

export interface SankeyData {
  nodes: SankeyNode[]
  links: SankeyLink[]
  totals: {
    income: number
    expense: number
    balance: number
  }
}

export interface DashboardSummary {
  total_transactions: number
  income: number
  expense: number
  balance: number
  top_expenses: Array<{
    category: string
    color: string
    amount: number
  }>
}

export const dashboardApi = {
  /**
   * Get Sankey diagram data
   */
  getSankeyData: async (): Promise<SankeyData> => {
    const response = await axios.get(`${API_URL}/api/v1/dashboard/sankey`)
    return response.data
  },

  /**
   * Get dashboard summary statistics
   */
  getSummary: async (): Promise<DashboardSummary> => {
    const response = await axios.get(`${API_URL}/api/v1/dashboard/summary`)
    return response.data
  },
}
