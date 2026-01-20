import { useEffect, useState } from 'react'
import { Card, Typography, Spin, Alert } from 'antd'
import apiClient from '../api/client'

const { Title, Paragraph } = Typography

interface HealthStatus {
  status: string
  api_version?: string
}

function HomePage() {
  const [health, setHealth] = useState<HealthStatus | null>(null)
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)

  useEffect(() => {
    const checkHealth = async () => {
      try {
        const response = await apiClient.get('/health')
        setHealth(response.data)
      } catch (err) {
        setError('Failed to connect to backend API')
        console.error(err)
      } finally {
        setLoading(false)
      }
    }

    checkHealth()
  }, [])

  return (
    <div style={{ padding: '50px' }}>
      <Title>Social Media Posting Platform</Title>
      <Paragraph>
        AI-powered content creation for social media
      </Paragraph>

      <Card style={{ marginTop: '20px', maxWidth: '600px', margin: '20px auto' }}>
        <Title level={3}>Backend API Status</Title>
        {loading && <Spin />}
        {error && <Alert message={error} type="error" showIcon />}
        {health && (
          <Alert
            message={`Status: ${health.status}`}
            description={`API Version: ${health.api_version || 'v1'}`}
            type="success"
            showIcon
          />
        )}
      </Card>

      <Card style={{ marginTop: '20px', maxWidth: '600px', margin: '20px auto' }}>
        <Title level={4}>Getting Started</Title>
        <Paragraph>
          This is the foundation of your web application. The backend is running
          on port 8000 and the frontend is on port 3000.
        </Paragraph>
        <Paragraph>
          <strong>Next steps:</strong>
          <ul style={{ textAlign: 'left' }}>
            <li>Add authentication endpoints and login page</li>
            <li>Implement prompt management</li>
            <li>Build text generation features</li>
            <li>Add post curation capabilities</li>
          </ul>
        </Paragraph>
      </Card>
    </div>
  )
}

export default HomePage
