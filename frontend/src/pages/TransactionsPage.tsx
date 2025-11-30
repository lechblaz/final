import { useQuery } from '@tanstack/react-query'
import { useState } from 'react'
import { transactionsApi } from '../api/transactions'
import { format } from 'date-fns'

export default function TransactionsPage() {
  const [fromDate, setFromDate] = useState('')
  const [toDate, setToDate] = useState('')
  const [page, setPage] = useState(1)
  const pageSize = 50

  const { data, isLoading, error, refetch } = useQuery({
    queryKey: ['transactions', fromDate, toDate, page],
    queryFn: () => transactionsApi.getTransactions({
      from_date: fromDate || undefined,
      to_date: toDate || undefined,
      limit: pageSize,
      offset: (page - 1) * pageSize,
    }),
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
                setPage(1)
              }}
            >
              Clear Filters
            </button>
          </div>
        </div>

        {/* Stats */}
        {data && (
          <div style={{ marginBottom: '20px', color: '#6b7280', fontSize: '14px' }}>
            Showing {data.transactions.length} of {data.total} transactions
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
      {data && data.transactions.length > 0 && (
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
              {data.transactions.map((transaction) => (
                <tr key={transaction.id}>
                  <td style={{ whiteSpace: 'nowrap' }}>
                    {formatDate(transaction.booking_date)}
                  </td>
                  <td>
                    <div style={{ fontWeight: 500 }}>
                      {transaction.normalized_merchant_name || transaction.title}
                    </div>
                    {transaction.normalized_merchant_name && transaction.title !== transaction.normalized_merchant_name && (
                      <div style={{ fontSize: '12px', color: '#6b7280', marginTop: '2px' }}>
                        {transaction.title}
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
      {data && data.transactions.length === 0 && !isLoading && (
        <div className="card" style={{ textAlign: 'center', padding: '40px', color: '#6b7280' }}>
          <p>No transactions found.</p>
          <p style={{ marginTop: '10px' }}>
            Try adjusting your filters or <a href="/import" style={{ color: '#2563eb' }}>import a CSV file</a>.
          </p>
        </div>
      )}
    </div>
  )
}
