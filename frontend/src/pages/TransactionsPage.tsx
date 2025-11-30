import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query'
import { useState } from 'react'
import { transactionsApi } from '../api/transactions'
import { tagsApi } from '../api/tags'
import { format } from 'date-fns'

export default function TransactionsPage() {
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [selectedTags, setSelectedTags] = useState<string[]>([])
  const [page, setPage] = useState(1)
  const [editingTags, setEditingTags] = useState<string | null>(null)
  const pageSize = 50
  const queryClient = useQueryClient()

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['transactions', fromDate, toDate, page],
    queryFn: () => transactionsApi.getTransactions({
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    }),
  })

  const { data: allTags } = useQuery({
    queryKey: ['tags'],
    queryFn: () => tagsApi.listTags(),
  })

  const applyTagsMutation = useMutation({
    mutationFn: ({ transactionId, tagIds }: { transactionId: string; tagIds: string[] }) =>
      tagsApi.applyTags(transactionId, tagIds),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['transactions'] })
      setEditingTags(null)
    },
  })

  const formatCurrency = (amount: number, currency: string = 'PLN') => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'yyyy-MM-dd')
    } catch {
      return dateString
    }
  }

  const totalPages = data ? Math.ceil(data.total / pageSize) : 0

  // Filter transactions by selected tags (client-side)
  const filteredTransactions = data?.transactions.filter(transaction => {
    if (selectedTags.length === 0) return true
    return selectedTags.every(tagId =>
      transaction.tags.some(tag => tag.id === tagId)
    )
  }) || []

  return (
    <div className="container">
      <div className="card" style={{ marginBottom: '20px' }}>
        <h2 style={{ marginBottom: '20px' }}>Transactions</h2>

        {/* Filters */}
        <div style={{ display: 'flex', gap: '10px', marginBottom: '20px', flexWrap: 'wrap' }}>
          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
              From Date
            </label>
            <input
              type="date"
              className="input"
              value={fromDate}
              onChange={(e) => {
                setFromDate(e.target.value)
                setPage(1)
              }}
              style={{ width: 'auto' }}
            />
          </div>

          <div>
            <label style={{ display: 'block', marginBottom: '5px', fontSize: '14px', color: '#6b7280' }}>
              To Date
            </label>
            <input
              type="date"
              className="input"
              value={toDate}
              onChange={(e) => {
                setToDate(e.target.value)
                setPage(1)
              }}
              style={{ width: 'auto' }}
            />
          </div>

          <div style={{ display: 'flex', alignItems: 'flex-end' }}>
            <button
              className="btn btn-secondary"
              onClick={() => {
                setFromDate('')
                setToDate('')
                setSelectedTags([])
                setPage(1)
              }}
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Tag filters */}
        {allTags && allTags.tags.length > 0 && (
          <div style={{ marginBottom: '20px' }}>
            <label style={{ display: 'block', marginBottom: '8px', fontSize: '14px', color: '#6b7280' }}>
              Filter by Tags
            </label>
            <div style={{ display: 'flex', flexWrap: 'wrap', gap: '6px' }}>
              {allTags.tags.map((tag) => {
                const isSelected = selectedTags.includes(tag.id)
                return (
                  <button
                    key={tag.id}
                    onClick={() => {
                      setSelectedTags(prev =>
                        isSelected
                          ? prev.filter(id => id !== tag.id)
                          : [...prev, tag.id]
                      )
                      setPage(1)
                    }}
                    style={{
                      padding: '4px 10px',
                      borderRadius: '14px',
                      fontSize: '12px',
                      fontWeight: 500,
                      border: isSelected ? 'none' : '1px solid #d1d5db',
                      backgroundColor: isSelected ? (tag.color || '#e5e7eb') : 'transparent',
                      color: isSelected ? '#fff' : '#374151',
                      cursor: 'pointer',
                    }}
                  >
                    {isSelected && '✓ '}{tag.display_name} ({tag.transaction_count})
                  </button>
                )
              })}
            </div>
          </div>
        )}

        {/* Stats */}
        {data && (
          <div style={{ marginBottom: '20px', color: '#6b7280', fontSize: '14px' }}>
            Showing {filteredTransactions.length} of {data.total} transactions
            {selectedTags.length > 0 && ` (filtered by ${selectedTags.length} tag${selectedTags.length > 1 ? 's' : ''})`}
            {totalPages > 1 && ` (Page ${page} of ${totalPages})`}
          </div>
        )}
      </div>

      {/* Loading state */}
      {isLoading && (
        <div className="loading">Loading transactions...</div>
      )}

      {/* Error state */}
      {error && (
        <div className="error">
          Error loading transactions: {error.message}
        </div>
      )}

      {/* Transactions table */}
      {data && filteredTransactions.length > 0 && (
        <div className="card">
          <table className="table">
            <thead>
              <tr>
                <th>Date</th>
                <th>Merchant / Description</th>
                <th>Type</th>
                <th style={{ textAlign: 'right' }}>Amount</th>
                <th style={{ textAlign: 'right' }}>Balance</th>
              </tr>
            </thead>
            <tbody>
              {filteredTransactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    {formatDate(transaction.booking_date)}
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>
                      {transaction.normalized_merchant_name || transaction.title}
                    </div>
                    {transaction.store_identifier && (
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                        Store: {transaction.store_identifier}
                        {transaction.location_extracted && ` • ${transaction.location_extracted}`}
                      </div>
                    )}
                    {!transaction.store_identifier && transaction.location_extracted && (
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                        {transaction.location_extracted}
                      </div>
                    )}
                    {/* Tags */}
                    {transaction.tags && transaction.tags.length > 0 && (
                      <div style={{ display: 'flex', gap: '4px', marginTop: '8px', flexWrap: 'wrap' }}>
                        {transaction.tags.map((tag) => (
                          <span
                            key={tag.id}
                            style={{
                              padding: '2px 8px',
                              borderRadius: '12px',
                              fontSize: '11px',
                              fontWeight: 500,
                              backgroundColor: tag.color || '#e5e7eb',
                              color: '#fff',
                            }}
                          >
                            {tag.display_name}
                          </span>
                        ))}
                        <button
                          onClick={() => setEditingTags(transaction.id)}
                          style={{
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            border: '1px dashed #d1d5db',
                            backgroundColor: 'transparent',
                            color: '#6b7280',
                            cursor: 'pointer',
                          }}
                        >
                          + Edit
                        </button>
                      </div>
                    )}
                    {(!transaction.tags || transaction.tags.length === 0) && (
                      <div style={{ marginTop: '8px' }}>
                        <button
                          onClick={() => setEditingTags(transaction.id)}
                          style={{
                            padding: '2px 8px',
                            borderRadius: '12px',
                            fontSize: '11px',
                            border: '1px dashed #d1d5db',
                            backgroundColor: 'transparent',
                            color: '#6b7280',
                            cursor: 'pointer',
                          }}
                        >
                          + Add tags
                        </button>
                      </div>
                    )}
                    {/* Tag editing modal */}
                    {editingTags === transaction.id && allTags && (
                      <div style={{
                        position: 'fixed',
                        top: 0,
                        left: 0,
                        right: 0,
                        bottom: 0,
                        backgroundColor: 'rgba(0, 0, 0, 0.5)',
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                        zIndex: 1000,
                      }}>
                        <div style={{
                          backgroundColor: '#fff',
                          padding: '24px',
                          borderRadius: '8px',
                          maxWidth: '500px',
                          width: '90%',
                          maxHeight: '80vh',
                          overflow: 'auto',
                        }}>
                          <h3 style={{ marginBottom: '16px' }}>Edit Tags</h3>
                          <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px', marginBottom: '16px' }}>
                            {allTags.tags.map((tag) => {
                              const isSelected = transaction.tags.some(t => t.id === tag.id)
                              return (
                                <button
                                  key={tag.id}
                                  onClick={() => {
                                    const currentTagIds = transaction.tags.map(t => t.id)
                                    const newTagIds = isSelected
                                      ? currentTagIds.filter(id => id !== tag.id)
                                      : [...currentTagIds, tag.id]
                                    applyTagsMutation.mutate({
                                      transactionId: transaction.id,
                                      tagIds: newTagIds,
                                    })
                                  }}
                                  style={{
                                    padding: '6px 12px',
                                    borderRadius: '16px',
                                    fontSize: '13px',
                                    fontWeight: 500,
                                    border: isSelected ? 'none' : '1px solid #d1d5db',
                                    backgroundColor: isSelected ? (tag.color || '#e5e7eb') : 'transparent',
                                    color: isSelected ? '#fff' : '#374151',
                                    cursor: 'pointer',
                                  }}
                                >
                                  {isSelected && '✓ '}{tag.display_name}
                                </button>
                              )
                            })}
                          </div>
                          <button
                            onClick={() => setEditingTags(null)}
                            className="btn btn-secondary"
                            style={{ width: '100%' }}
                          >
                            Done
                          </button>
                        </div>
                      </div>
                    )}
                  </td>
                  <td style={{ fontSize: '13px', color: '#6b7280' }}>
                    {transaction.operation_type}
                  </td>
                  <td style={{ textAlign: 'right', fontWeight: 500 }}>
                    <span style={{ color: transaction.amount < 0 ? '#dc2626' : '#16a34a' }}>
                      {formatCurrency(transaction.amount, transaction.currency)}
                    </span>
                  </td>
                  <td style={{ textAlign: 'right', color: '#6b7280' }}>
                    {transaction.balance_after !== null && formatCurrency(transaction.balance_after, transaction.currency)}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>

          {/* Pagination */}
          {totalPages > 1 && (
            <div style={{ marginTop: '20px', display: 'flex', justifyContent: 'center', gap: '10px' }}>
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.max(1, p - 1))}
                disabled={page === 1}
                style={{ opacity: page === 1 ? 0.5 : 1 }}
              >
                Previous
              </button>
              <span style={{ padding: '10px 20px', color: '#6b7280' }}>
                Page {page} of {totalPages}
              </span>
              <button
                className="btn btn-secondary"
                onClick={() => setPage(p => Math.min(totalPages, p + 1))}
                disabled={page === totalPages}
                style={{ opacity: page === totalPages ? 0.5 : 1 }}
              >
                Next
              </button>
            </div>
          )}
        </div>
      )}

      {/* Empty state */}
      {data && filteredTransactions.length === 0 && !isLoading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <p>No transactions found.</p>
          <p style={{ marginTop: '10px' }}>
            {selectedTags.length > 0 || fromDate || toDate
              ? 'Try adjusting your filters.'
              : <>Try adjusting your filters or <a href="/import" style={{ color: '#2563eb' }}>import a CSV file</a>.</>
            }
          </p>
        </div>
      )}
    </div>
  )
}
