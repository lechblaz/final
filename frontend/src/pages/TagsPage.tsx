import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { tagsApi } from '../api/tags'

export default function TagsPage() {
  const [showCreateForm, setShowCreateForm] = useState(false)
  const [newTagName, setNewTagName] = useState('')
  const [newTagDisplayName, setNewTagDisplayName] = useState('')
  const [newTagColor, setNewTagColor] = useState('#3b82f6')
  const [newTagDescription, setNewTagDescription] = useState('')
  const queryClient = useQueryClient()

  const { data, isLoading, error } = useQuery({
    queryKey: ['tags'],
    queryFn: () => tagsApi.listTags(),
  })

  const createTagMutation = useMutation({
    mutationFn: tagsApi.createTag,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['tags'] })
      setShowCreateForm(false)
      setNewTagName('')
      setNewTagDisplayName('')
      setNewTagColor('#3b82f6')
      setNewTagDescription('')
    },
  })

  const handleCreateTag = () => {
    if (!newTagName.trim()) return

    createTagMutation.mutate({
      name: newTagName.toLowerCase().replace(/\s+/g, '-'),
      display_name: newTagDisplayName || newTagName,
      color: newTagColor,
      description: newTagDescription || undefined,
    })
  }

  return (
    <div className="container">
      <div className="card">
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <h2>Tags</h2>
          <button
            className="btn btn-primary"
            onClick={() => setShowCreateForm(!showCreateForm)}
          >
            {showCreateForm ? 'Cancel' : '+ Create Tag'}
          </button>
        </div>

        {/* Create tag form */}
        {showCreateForm && (
          <div className="card" style={{ marginBottom: '20px', backgroundColor: '#f9fafb' }}>
            <h3 style={{ marginBottom: '16px', fontSize: '16px' }}>Create New Tag</h3>
            <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
                  Tag Name (lowercase, no spaces)
                </label>
                <input
                  type="text"
                  className="input"
                  value={newTagName}
                  onChange={(e) => setNewTagName(e.target.value)}
                  placeholder="e.g., grocery, transport, coffee"
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
                  Display Name
                </label>
                <input
                  type="text"
                  className="input"
                  value={newTagDisplayName}
                  onChange={(e) => setNewTagDisplayName(e.target.value)}
                  placeholder="e.g., Grocery, Transport, Coffee"
                />
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
                  Color
                </label>
                <div style={{ display: 'flex', gap: '10px', alignItems: 'center' }}>
                  <input
                    type="color"
                    value={newTagColor}
                    onChange={(e) => setNewTagColor(e.target.value)}
                    style={{ width: '60px', height: '40px', cursor: 'pointer' }}
                  />
                  <span style={{ fontSize: '14px', color: '#6b7280' }}>{newTagColor}</span>
                </div>
              </div>
              <div>
                <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
                  Description (optional)
                </label>
                <textarea
                  className="input"
                  value={newTagDescription}
                  onChange={(e) => setNewTagDescription(e.target.value)}
                  placeholder="Description of this tag..."
                  rows={2}
                />
              </div>
              <button
                className="btn btn-primary"
                onClick={handleCreateTag}
                disabled={!newTagName.trim() || createTagMutation.isPending}
              >
                {createTagMutation.isPending ? 'Creating...' : 'Create Tag'}
              </button>
            </div>
          </div>
        )}

        {/* Loading state */}
        {isLoading && <div className="loading">Loading tags...</div>}

        {/* Error state */}
        {error && (
          <div className="error">
            Error loading tags: {error.message}
          </div>
        )}

        {/* Tags grid */}
        {data && (
          <>
            <div style={{ marginBottom: '16px', color: '#6b7280', fontSize: '14px' }}>
              {data.total} tag{data.total !== 1 ? 's' : ''}
            </div>
            <div style={{ display: 'grid', gap: '12px' }}>
              {data.tags.map((tag) => (
                <div
                  key={tag.id}
                  className="card"
                  style={{
                    padding: '16px',
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                  }}
                >
                  <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                    <div style={{ flex: 1 }}>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '12px', marginBottom: '8px' }}>
                        <span
                          style={{
                            padding: '4px 12px',
                            borderRadius: '14px',
                            fontSize: '13px',
                            fontWeight: 500,
                            backgroundColor: tag.color || '#e5e7eb',
                            color: '#fff',
                          }}
                        >
                          {tag.display_name}
                        </span>
                        <span style={{ fontSize: '13px', color: '#6b7280' }}>
                          {tag.name}
                        </span>
                      </div>
                      {tag.description && (
                        <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>
                          {tag.description}
                        </div>
                      )}
                      <div style={{ fontSize: '13px', color: '#9ca3af' }}>
                        Used in {tag.transaction_count} transaction{tag.transaction_count !== 1 ? 's' : ''}
                      </div>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </>
        )}

        {/* Empty state */}
        {data && data.tags.length === 0 && !isLoading && (
          <div style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
            <p>No tags yet.</p>
            <p style={{ marginTop: '10px' }}>
              Click "Create Tag" to add your first tag.
            </p>
          </div>
        )}
      </div>
    </div>
  )
}
