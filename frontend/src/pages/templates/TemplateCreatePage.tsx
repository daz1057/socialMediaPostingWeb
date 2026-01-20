import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Select } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useCreateTemplate, useTemplateTags } from '@/hooks/useTemplates';
import type { TemplateCreate } from '@/types';
import { TEMPLATE_CATEGORIES } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function TemplateCreatePage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const createTemplate = useCreateTemplate();
  const { data: availableTags } = useTemplateTags();

  const onFinish = async (values: TemplateCreate) => {
    try {
      const template = await createTemplate.mutateAsync(values);
      message.success('Template created successfully');
      navigate(`/templates/${template.id}`);
    } catch {
      message.error('Failed to create template');
    }
  };

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

      <Title level={2}>Create Template</Title>

      <Card style={{ maxWidth: 900 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ category: 'manual', tags: [] }}
        >
          <Form.Item
            name="name"
            label="Name"
            rules={[{ required: true, message: 'Please enter a name' }]}
          >
            <Input placeholder="e.g., Email Signature, Social Bio" />
          </Form.Item>

          <Form.Item
            name="category"
            label="Category"
            rules={[{ required: true, message: 'Please select a category' }]}
          >
            <Select options={TEMPLATE_CATEGORIES} />
          </Form.Item>

          <Form.Item
            name="tags"
            label="Tags"
            tooltip="Add tags to organize and filter templates"
          >
            <Select
              mode="tags"
              placeholder="Add tags..."
              options={availableTags?.map((tag) => ({ value: tag, label: tag })) || []}
            />
          </Form.Item>

          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter the template content' }]}
          >
            <TextArea
              rows={12}
              placeholder="Enter your reusable text snippet here..."
              showCount
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createTemplate.isPending}
              >
                Create Template
              </Button>
              <Button onClick={() => navigate('/templates')}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
