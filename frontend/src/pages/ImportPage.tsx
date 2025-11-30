import { useState } from 'react'
import { useMutation, useQuery } from '@tanstack/react-query'
import { importsApi } from '../api/imports'
import { format } from 'date-fns'
import { useNavigate } from 'react-router-dom'

export default function ImportPage() {
  const [selectedFile, setSelectedFile] = useState<File | null>(null)
  const [uploadError, setUploadError] = useState<string | null>(null)
  const [uploadSuccess, setUploadSuccess] = useState<string | null>(null)
  const navigate = useNavigate()

  // Get recent imports
  const { data: imports } = useQuery({
    queryKey: ['imports'],
    queryFn: () => importsApi.getImports({ limit: 10 }),
  })

  // Upload mutation
  const uploadMutation = useMutation({
    mutationFn: (file: File) => importsApi.uploadCsv(file),
    onSuccess: (data) => {
      setUploadSuccess(
        `Successfully imported ${data.transactions_imported} transactions. ` +
        `${data.duplicates_skipped} duplicates were skipped.`
      )
      setUploadError(null)
      setSelectedFile(null)

      // Redirect to transactions page after 2 seconds
      setTimeout(() => {
        navigate('/')
      }, 2000)
    },
    onError: (error: any) => {
      setUploadError(error.response?.data?.detail || error.message || 'Upload failed')
      setUploadSuccess(null)
    },
  })

  const handleFileChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0]
    if (file) {
      if (!file.name.endsWith('.csv')) {
        setUploadError('Please select a CSV file')
        return
      }
      setSelectedFile(file)
      setUploadError(null)
      setUploadSuccess(null)
    }
  }

  const handleUpload = () => {
    if (!selectedFile) {
      setUploadError('Please select a file first')
      return
    }

    uploadMutation.mutate(selectedFile)
  }

  const formatDate = (dateString: string) => {
    try {
      return format(new Date(dateString), 'yyyy-MM-dd HH:mm')
    } catch {
      return dateString
    }
  }

  const getStatusColor = (status: string) => {
    switch (status) {
      case 'completed':
        return '#16a34a'
      case 'processing':
        return '#eab308'
      case 'failed':
        return '#dc2626'
      default:
        return '#6b7280'
    }
  }

  return (
    <div className="container">
      <h2 style={{ marginBottom: '20px' }}>Import CSV File</h2>

      {/* Upload section */}
      <div className="card" style={{ marginBottom: '30px' }}>
        <h3 style={{ marginBottom: '15px' }}>Upload mBank Statement</h3>
        <p style={{ color: '#6b7280', marginBottom: '20px' }}>
          Select a CSV file exported from mBank to import your transactions.
        </p>

        <div style={{ marginBottom: '20px' }}>
          <input
            type="file"
            accept=".csv"
            onChange={handleFileChange}
            style={{
              padding: '10px',
              border: '1px solid #d1d5db',
              borderRadius: '4px',
              width: '100%',
              maxWidth: '400px',
            }}
          />
        </div>

        {selectedFile && (
          <div style={{ marginBottom: '20px', color: '#6b7280', fontSize: '14px' }}>
            Selected: {selectedFile.name} ({(selectedFile.size / 1024).toFixed(2)} KB)
          </div>
        )}

        <button
          className="btn btn-primary"
          onClick={handleUpload}
          disabled={!selectedFile || uploadMutation.isPending}
        >
          {uploadMutation.isPending ? 'Uploading...' : 'Upload & Import'}
        </button>

        {/* Success message */}
        {uploadSuccess && (
          <div className="success" style={{ marginTop: '20px' }}>
            {uploadSuccess}
            <div style={{ marginTop: '10px', fontSize: '14px' }}>
              Redirecting to transactions...
            </div>
          </div>
        )}

        {/* Error message */}
        {uploadError && (
          <div className="error" style={{ marginTop: '20px' }}>
            {uploadError}
          </div>
        )}
      </div>

      {/* Recent imports */}
      {imports && imports.imports.length > 0 && (
        <div className="card">
          <h3 style={{ marginBottom: '15px' }}>Recent Imports</h3>

          <table className="table">
            <thead>
              <tr>
                <th>File Name</th>
                <th>Imported At</th>
                <th>Period</th>
                <th style={{ textAlign: 'right' }}>Transactions</th>
                <th style={{ textAlign: 'right' }}>Duplicates</th>
                <th>Status</th>
              </tr>
            </thead>
            <tbody>
              {imports.imports.map((imp) => (
                <tr key={imp.id}>
                  <td style={{ fontWeight: 500 }}>{imp.file_name}</td>
                  <td style={{ whiteSpace: 'nowrap', color: '#6b7280' }}>
                    {formatDate(imp.created_at)}
                  </td>
                  <td style={{ color: '#6b7280', fontSize: '13px' }}>
                    {imp.period_start && imp.period_end
                      ? `${imp.period_start} to ${imp.period_end}`
                      : '-'}
                  </td>
                  <td style={{ textAlign: 'right', color: '#16a34a', fontWeight: 500 }}>
                    {imp.transactions_imported}
                  </td>
                  <td style={{ textAlign: 'right', color: '#6b7280' }}>
                    {imp.duplicates_skipped}
                  </td>
                  <td>
                    <span
                      style={{
                        padding: '4px 8px',
                        borderRadius: '4px',
                        fontSize: '12px',
                        fontWeight: 500,
                        backgroundColor: `${getStatusColor(imp.import_status)}22`,
                        color: getStatusColor(imp.import_status),
                      }}
                    >
                      {imp.import_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  )
}
