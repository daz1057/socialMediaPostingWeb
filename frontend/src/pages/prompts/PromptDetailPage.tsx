import { useNavigate, useParams } from 'react-router-dom';
import {
  Card,
  Button,
  Typography,
  Space,
  Spin,
  Descriptions,
  Tag,
  Popconfirm,
  message,
} from 'antd';
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, PlayCircleOutlined } from '@ant-design/icons';
import { usePrompt, useDeletePrompt } from '@/hooks/usePrompts';

const { Title, Paragraph, Text } = Typography;

export function PromptDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const promptId = parseInt(id || '0', 10);
  const { data: prompt, isLoading } = usePrompt(promptId);
  const deletePrompt = useDeletePrompt();

  const handleDelete = async () => {
    try {
      await deletePrompt.mutateAsync(promptId);
      message.success('Prompt deleted successfully');
      navigate('/prompts');
    } catch {
      message.error('Failed to delete prompt');
    }
  };

  if (isLoading) {
    return (
      <div className="tw-flex tw-justify-center tw-items-center tw-h-64">
        <Spin size="large" />
      </div>
    );
  }

  if (!prompt) {
    return (
      <div>
        <Title level={4}>Prompt not found</Title>
        <Button onClick={() => navigate('/prompts')}>Back to Prompts</Button>
      </div>
    );
  }

  return (
    <div>
      <Space className="tw-mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/prompts')}
        >
          Back
        </Button>
      </Space>

      <div className="tw-flex tw-justify-between tw-items-start tw-mb-4">
        <Title level={2} style={{ margin: 0 }}>{prompt.name}</Title>
        <Space>
          <Button
            type="primary"
            icon={<PlayCircleOutlined />}
            onClick={() => navigate('/generate/text', { state: { promptId: prompt.id } })}
          >
            Use in Generation
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/prompts/${prompt.id}/edit`)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this prompt?"
            description="This action cannot be undone."
            onConfirm={handleDelete}
            okText="Delete"
            okType="danger"
          >
            <Button icon={<DeleteOutlined />} danger>
              Delete
            </Button>
          </Popconfirm>
        </Space>
      </div>

      <Card>
        <Descriptions column={1} bordered>
          <Descriptions.Item label="Description">
            {prompt.description || <Text type="secondary">No description</Text>}
          </Descriptions.Item>
          <Descriptions.Item label="Tags">
            {prompt.tags.length > 0 ? (
              prompt.tags.map((tag) => <Tag key={tag.id}>{tag.name}</Tag>)
            ) : (
              <Text type="secondary">No tags</Text>
            )}
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {new Date(prompt.created_at).toLocaleString()}
          </Descriptions.Item>
          {prompt.updated_at && (
            <Descriptions.Item label="Last Updated">
              {new Date(prompt.updated_at).toLocaleString()}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      <Card title="Prompt Content" style={{ marginTop: 16 }}>
        <Paragraph>
          <pre style={{
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 8,
            margin: 0,
          }}>
            {prompt.content}
          </pre>
        </Paragraph>
      </Card>
    </div>
  );
}
