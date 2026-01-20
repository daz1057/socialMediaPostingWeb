import { useNavigate } from 'react-router-dom';
import { Card, Row, Col, Statistic, Button, Space, Typography } from 'antd';
import {
  FileTextOutlined,
  SendOutlined,
  EditOutlined,
  PictureOutlined,
  PlusOutlined,
} from '@ant-design/icons';
import { usePrompts } from '@/hooks/usePrompts';
import { usePosts } from '@/hooks/usePosts';

const { Title, Text } = Typography;

export function DashboardPage() {
  const navigate = useNavigate();
  const { data: promptsData, isLoading: promptsLoading } = usePrompts({ limit: 1 });
  const { data: postsData, isLoading: postsLoading } = usePosts({ limit: 1 });

  return (
    <div>
      <Title level={2}>Dashboard</Title>
      <Text type="secondary">Welcome to your social media content generator.</Text>

      <Row gutter={[16, 16]} style={{ marginTop: 24 }}>
        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Prompts"
              value={promptsData?.total ?? 0}
              loading={promptsLoading}
              prefix={<FileTextOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Total Posts"
              value={postsData?.total ?? 0}
              loading={postsLoading}
              prefix={<SendOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Draft Posts"
              value={postsData?.items?.filter(p => p.status === 'draft').length ?? 0}
              loading={postsLoading}
              prefix={<EditOutlined />}
            />
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card>
            <Statistic
              title="Published Posts"
              value={postsData?.items?.filter(p => p.status === 'published').length ?? 0}
              loading={postsLoading}
              prefix={<SendOutlined />}
            />
          </Card>
        </Col>
      </Row>

      <Title level={3} style={{ marginTop: 32 }}>Quick Actions</Title>

      <Row gutter={[16, 16]}>
        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            onClick={() => navigate('/prompts/new')}
          >
            <Space>
              <PlusOutlined style={{ fontSize: 24, color: '#1890ff' }} />
              <div>
                <Text strong>Create Prompt</Text>
                <br />
                <Text type="secondary">Add a new prompt template</Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            onClick={() => navigate('/generate/text')}
          >
            <Space>
              <EditOutlined style={{ fontSize: 24, color: '#52c41a' }} />
              <div>
                <Text strong>Generate Text</Text>
                <br />
                <Text type="secondary">Create content with AI</Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            onClick={() => navigate('/generate/image')}
          >
            <Space>
              <PictureOutlined style={{ fontSize: 24, color: '#722ed1' }} />
              <div>
                <Text strong>Generate Image</Text>
                <br />
                <Text type="secondary">Create images with DALL-E/Flux</Text>
              </div>
            </Space>
          </Card>
        </Col>

        <Col xs={24} sm={12} lg={6}>
          <Card
            hoverable
            onClick={() => navigate('/posts/new')}
          >
            <Space>
              <SendOutlined style={{ fontSize: 24, color: '#fa8c16' }} />
              <div>
                <Text strong>Create Post</Text>
                <br />
                <Text type="secondary">Draft a new social post</Text>
              </div>
            </Space>
          </Card>
        </Col>
      </Row>

      <div style={{ marginTop: 32 }}>
        <Button type="primary" onClick={() => navigate('/settings/credentials')}>
          Setup API Credentials
        </Button>
        <Button style={{ marginLeft: 8 }} onClick={() => navigate('/settings/models')}>
          Configure Models
        </Button>
      </div>
    </div>
  );
}
