import axios from 'axios'

const API_URL = import.meta.env.VITE_API_URL || 'http://localhost:8000'

export interface Tag {
  id: string
  name: string
  display_name: string
  color: string | null
  icon: string | null
  description: string | null
  usage_count: number
  created_at: string
  updated_at: string
}

export interface TagWithStats extends Tag {
  transaction_count: number
}

export interface TagListResponse {
  tags: TagWithStats[]
  total: number
}

export const tagsApi = {
  /**
   * List all tags
   */
  listTags: async (params?: {
    limit?: number
    offset?: number
    search?: string
  }): Promise<TagListResponse> => {
    const response = await axios.get(`${API_URL}/api/v1/tags`, {
      params,
    })
    return response.data
  },

  /**
   * Create a new tag
   */
  createTag: async (tag: {
    name: string
    display_name?: string
    color?: string
    icon?: string
    description?: string
  }): Promise<Tag> => {
    const response = await axios.post(`${API_URL}/api/v1/tags`, tag)
    return response.data
  },

  /**
   * Apply tags to a transaction
   */
  applyTags: async (transactionId: string, tagIds: string[]): Promise<void> => {
    await axios.post(`${API_URL}/api/v1/tags/apply?transaction_id=${transactionId}`, {
      tag_ids: tagIds,
    })
  },

  /**
   * Get tag suggestions for a transaction
   */
  suggestTags: async (transactionId: string): Promise<{
    transaction_id: string
    suggested_tags: Array<{
      id: string
      name: string
      display_name: string
      color: string
    }>
  }> => {
    const response = await axios.get(
      `${API_URL}/api/v1/tags/suggest/${transactionId}`
    )
    return response.data
  },
}
