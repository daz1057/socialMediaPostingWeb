import { useNavigate, useParams } from 'react-router-dom';
import { Button, Card, Typography, Space, Spin, Tag, Descriptions, Popconfirm, message } from 'antd';
import { ArrowLeftOutlined, EditOutlined, DeleteOutlined, CopyOutlined } from '@ant-design/icons';
import { useTemplate, useDeleteTemplate } from '@/hooks/useTemplates';
import type { TemplateCategory } from '@/types';

const { Title, Paragraph } = Typography;

const categoryColors: Record<TemplateCategory, string> = {
  ocr: 'blue',
  manual: 'green',
  custom: 'purple',
};

export function TemplateDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const templateId = parseInt(id || '0', 10);
  const { data: template, isLoading } = useTemplate(templateId);
  const deleteTemplate = useDeleteTemplate();

  const handleDelete = async () => {
    try {
      await deleteTemplate.mutateAsync(templateId);
      message.success('Template deleted successfully');
      navigate('/templates');
    } catch {
      message.error('Failed to delete template');
    }
  };

  const handleCopyContent = () => {
    if (template) {
      navigator.clipboard.writeText(template.content);
      message.success('Content copied to clipboard');
    }
  };

  if (isLoading) {
    return (
      <div className="tw-flex tw-justify-center tw-items-center tw-h-64">
        <Spin size="large" />
      </div>
    );
  }

  if (!template) {
    return (
      <div>
        <Title level={4}>Template not found</Title>
        <Button onClick={() => navigate('/templates')}>Back to Templates</Button>
      </div>
    );
  }

  return (
    <div>
      <Space className="tw-mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/templates')}
        >
          Back
        </Button>
      </Space>

      <div className="tw-flex tw-justify-between tw-items-start tw-mb-4">
        <div>
          <Title level={2} style={{ margin: 0 }}>{template.name}</Title>
          <Space className="tw-mt-2">
            <Tag color={categoryColors[template.category]}>{template.category.toUpperCase()}</Tag>
            {template.tags.map((tag) => (
              <Tag key={tag}>{tag}</Tag>
            ))}
          </Space>
        </div>
        <Space>
          <Button
            icon={<CopyOutlined />}
            onClick={handleCopyContent}
          >
            Copy Content
          </Button>
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/templates/${templateId}/edit`)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this template?"
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

      <Card title="Content" style={{ marginBottom: 16 }}>
        <Paragraph
          style={{ whiteSpace: 'pre-wrap', marginBottom: 0 }}
        >
          {template.content}
        </Paragraph>
      </Card>

      <Card title="Details">
        <Descriptions column={2}>
          <Descriptions.Item label="Category">
            <Tag color={categoryColors[template.category]}>{template.category.toUpperCase()}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Tags">
            {template.tags.length > 0 ? (
              <Space wrap>
                {template.tags.map((tag) => (
                  <Tag key={tag}>{tag}</Tag>
                ))}
              </Space>
            ) : (
              '-'
            )}
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {new Date(template.created_at).toLocaleString()}
          </Descriptions.Item>
          <Descriptions.Item label="Updated">
            {new Date(template.updated_at).toLocaleString()}
          </Descriptions.Item>
        </Descriptions>
      </Card>
    </div>
  );
}
