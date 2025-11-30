import { useQuery } from '@tanstack/react-query'
import { dashboardApi } from '../api/dashboard'
import { Sankey, Tooltip, ResponsiveContainer } from 'recharts'

export default function DashboardPage() {
  const { data: summary, isLoading: summaryLoading } = useQuery({
    queryKey: ['dashboard-summary'],
    queryFn: dashboardApi.getSummary,
  })

  const { data: sankeyData, isLoading: sankeyLoading } = useQuery({
    queryKey: ['dashboard-sankey'],
    queryFn: dashboardApi.getSankeyData,
  })

  const formatCurrency = (amount: number, currency: string = 'PLN') => {
    return new Intl.NumberFormat('pl-PL', {
      style: 'currency',
      currency: currency,
    }).format(amount)
  }

  // Transform data for Recharts Sankey
  const sankeyChartData = sankeyData ? {
    nodes: sankeyData.nodes.map(node => ({
      name: node.name,
      ...node
    })),
    links: sankeyData.links.map(link => ({
      source: sankeyData.nodes.findIndex(n => n.id === link.source),
      target: sankeyData.nodes.findIndex(n => n.id === link.target),
      value: link.value
    }))
  } : null

  return (
    <div className="container">
      <h1 style={{ marginBottom: '24px' }}>Dashboard</h1>

      {/* Summary Cards */}
      {summaryLoading && <div className="loading">Loading summary...</div>}

      {summary && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(250px, 1fr))', gap: '16px', marginBottom: '24px' }}>
          {/* Total Transactions Card */}
          <div className="card">
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Transactions</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold' }}>{summary.total_transactions}</div>
          </div>

          {/* Income Card */}
          <div className="card" style={{ borderLeft: '4px solid #16a34a' }}>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Income</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#16a34a' }}>
              {formatCurrency(summary.income)}
            </div>
          </div>

          {/* Expense Card */}
          <div className="card" style={{ borderLeft: '4px solid #dc2626' }}>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Total Expenses</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: '#dc2626' }}>
              {formatCurrency(summary.expense)}
            </div>
          </div>

          {/* Balance Card */}
          <div className="card" style={{ borderLeft: `4px solid ${summary.balance >= 0 ? '#16a34a' : '#dc2626'}` }}>
            <div style={{ fontSize: '14px', color: '#6b7280', marginBottom: '8px' }}>Balance</div>
            <div style={{ fontSize: '32px', fontWeight: 'bold', color: summary.balance >= 0 ? '#16a34a' : '#dc2626' }}>
              {formatCurrency(summary.balance)}
            </div>
          </div>
        </div>
      )}

      {/* Sankey Diagram */}
      <div className="card" style={{ marginBottom: '24px' }}>
        <h2 style={{ marginBottom: '16px' }}>Money Flow</h2>
        <p style={{ color: '#6b7280', fontSize: '14px', marginBottom: '20px' }}>
          Visual representation of income sources and expense categories
        </p>

        {sankeyLoading && <div className="loading">Loading flow diagram...</div>}

        {sankeyChartData && (
          <div style={{ width: '100%', height: '600px' }}>
            <ResponsiveContainer>
              <Sankey
                data={sankeyChartData}
                nodeWidth={10}
                nodePadding={60}
                margin={{ top: 20, right: 160, bottom: 20, left: 160 }}
                link={{ stroke: '#77c6c9' }}
                node={{
                  fill: '#2563eb',
                  fillOpacity: 1,
                }}
              >
                <Tooltip
                  formatter={(value: number) => formatCurrency(value)}
                  contentStyle={{
                    backgroundColor: '#fff',
                    border: '1px solid #e5e7eb',
                    borderRadius: '6px',
                    padding: '8px 12px'
                  }}
                />
              </Sankey>
            </ResponsiveContainer>
          </div>
        )}
      </div>

      {/* Top Expenses */}
      {summary && summary.top_expenses.length > 0 && (
        <div className="card">
          <h2 style={{ marginBottom: '16px' }}>Top Expense Categories</h2>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
            {summary.top_expenses.map((expense, index) => (
              <div
                key={index}
                style={{
                  display: 'flex',
                  justifyContent: 'space-between',
                  alignItems: 'center',
                  padding: '12px',
                  backgroundColor: '#f9fafb',
                  borderRadius: '6px',
                  borderLeft: `4px solid ${expense.color || '#6b7280'}`
                }}
              >
                <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                  <div style={{ fontSize: '20px', fontWeight: 'bold', color: '#6b7280', minWidth: '30px' }}>
                    {index + 1}
                  </div>
                  <div>
                    <div style={{ fontWeight: 500 }}>{expense.category}</div>
                  </div>
                </div>
                <div style={{ fontSize: '18px', fontWeight: 'bold', color: '#dc2626' }}>
                  {formatCurrency(expense.amount)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}
