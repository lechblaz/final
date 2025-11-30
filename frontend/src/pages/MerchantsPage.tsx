import { useQuery } from '@tanstack/react-query'
import { merchantsApi, type MerchantWithStats } from '../api/merchants'

export default function MerchantsPage() {
  const { data, isLoading, error } = useQuery({
    queryKey: ['merchants', 'discover'],
    queryFn: () => merchantsApi.discoverMerchants({ limit: 100, min_transactions: 2 }),
  })

  const formatCurrency = (amount: number) => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: 'PLN',
    }).format(amount)
  }

  if (isLoading) {
    return (
      <div className="container">
        <h2>Merchants</h2>
        <p>Loading...</p>
      </div>
    )
  }

  if (error) {
    return (
      <div className="container">
        <h2>Merchants</h2>
        <div className="error">
          Error loading merchants: {error instanceof Error ? error.message : 'Unknown error'}
        </div>
      </div>
    )
  }

  if (!data || data.merchants.length === 0) {
    return (
      <div className="container">
        <h2>Merchants</h2>
        <p>No merchants found</p>
      </div>
    )
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '10px' }}>Merchant Statistics</h2>
      <p style={{ color: '#6b7280', marginBottom: '20px' }}>
        Top merchants by transaction count (minimum 2 transactions)
      </p>

      <div className="card">
        <table className="table">
          <thead>
            <tr>
              <th>Merchant</th>
              <th style={{ textAlign: 'right' }}>Transactions</th>
              <th style={{ textAlign: 'right' }}>Stores</th>
              <th style={{ textAlign: 'right' }}>Total Spent</th>
            </tr>
          </thead>
          <tbody>
            {data.merchants.map((merchant: MerchantWithStats) => (
              <tr key={merchant.normalized_name}>
                <td>
                  <div style={{ display: 'flex', flexDirection: 'column' }}>
                    <span style={{ fontWeight: 500, fontSize: '15px' }}>
                      {merchant.display_name}
                    </span>
                    {merchant.category && (
                      <span style={{ fontSize: '12px', color: '#6b7280' }}>
                        {merchant.category}
                      </span>
                    )}
                  </div>
                </td>
                <td style={{ textAlign: 'right', fontWeight: 500 }}>
                  {merchant.transaction_count}
                </td>
                <td style={{ textAlign: 'right', color: '#6b7280' }}>
                  {merchant.store_count > 0 ? merchant.store_count : '-'}
                </td>
                <td
                  style={{
                    textAlign: 'right',
                    fontWeight: 500,
                    color: merchant.total_spent < 0 ? '#dc2626' : '#16a34a',
                  }}
                >
                  {formatCurrency(merchant.total_spent)}
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      <div style={{ marginTop: '20px', color: '#6b7280', fontSize: '14px' }}>
        Total merchants: {data.total}
      </div>
    </div>
  )
}
