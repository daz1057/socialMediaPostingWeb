import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Spin, Select } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useTemplate, useUpdateTemplate, useTemplateTags } from '@/hooks/useTemplates';
import type { TemplateUpdate } from '@/types';
import { TEMPLATE_CATEGORIES } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function TemplateEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const templateId = parseInt(id || '0', 10);
  const { data: template, isLoading } = useTemplate(templateId);
  const updateTemplate = useUpdateTemplate(templateId);
  const { data: availableTags } = useTemplateTags();

  useEffect(() => {
    if (template) {
      form.setFieldsValue({
        name: template.name,
        category: template.category,
        tags: template.tags,
        content: template.content,
      });
    }
  }, [template, form]);

  const onFinish = async (values: TemplateUpdate) => {
    try {
      await updateTemplate.mutateAsync(values);
      message.success('Template updated successfully');
      navigate(`/templates/${templateId}`);
    } catch {
      message.error('Failed to update template');
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
          onClick={() => navigate(`/templates/${templateId}`)}
        >
          Back
        </Button>
      </Space>

      <Title level={2}>Edit Template</Title>

      <Card style={{ maxWidth: 900 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
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
              showCount
            />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={updateTemplate.isPending}
              >
                Save Changes
              </Button>
              <Button onClick={() => navigate(`/templates/${templateId}`)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
