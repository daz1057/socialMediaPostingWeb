import { useEffect, useMemo } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Spin, Divider, Row, Col, Checkbox, Tag, Tooltip } from 'antd';
import { ArrowLeftOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { usePrompt, useUpdatePrompt } from '@/hooks/usePrompts';
import { useCustomerInfoList } from '@/hooks';
import type { PromptUpdate, CustomerCategory, InjectionType } from '@/types';
import { CUSTOMER_CATEGORIES, getInjectionType } from '@/types';

const { Title, Text } = Typography;
const { TextArea } = Input;

// Injection type tag colors
const INJECTION_TYPE_COLORS: Record<InjectionType, string> = {
  random: 'blue',
  all: 'green',
  ignored: 'default',
};

const INJECTION_TYPE_LABELS: Record<InjectionType, string> = {
  random: 'Random',
  all: 'All',
  ignored: 'Ignored',
};

export function PromptEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const promptId = parseInt(id || '0', 10);
  const { data: prompt, isLoading } = usePrompt(promptId);
  const updatePrompt = useUpdatePrompt(promptId);
  const { data: customerInfoList } = useCustomerInfoList();

  // Get categories that have data
  const categoriesWithData = useMemo(() => {
    const set = new Set<CustomerCategory>();
    customerInfoList?.customer_info.forEach((info) => {
      if (info.details && info.details.length > 0) {
        set.add(info.category);
      }
    });
    return set;
  }, [customerInfoList]);

  // Convert selected_customers Record to array for checkbox group
  const getSelectedCategories = (selectedCustomers?: Record<string, boolean>): CustomerCategory[] => {
    if (!selectedCustomers) return [];
    return Object.entries(selectedCustomers)
      .filter(([_, enabled]) => enabled)
      .map(([category]) => category as CustomerCategory);
  };

  useEffect(() => {
    if (prompt) {
      form.setFieldsValue({
        name: prompt.name,
        details: prompt.details,
        artwork_description: prompt.artwork_description,
        url: prompt.url,
        example_image: prompt.example_image,
        media_file_path: prompt.media_file_path,
        aws_folder_url: prompt.aws_folder_url,
        selectedCategories: getSelectedCategories(prompt.selected_customers),
      });
    }
  }, [prompt, form]);

  const onFinish = async (values: PromptUpdate & { selectedCategories?: CustomerCategory[] }) => {
    try {
      // Convert selected categories array to Record<string, boolean>
      const selected_customers: Record<string, boolean> = {};
      if (values.selectedCategories) {
        values.selectedCategories.forEach((cat) => {
          selected_customers[cat] = true;
        });
      }

      const promptData: PromptUpdate = {
        ...values,
        selected_customers,
      };
      delete (promptData as { selectedCategories?: CustomerCategory[] }).selectedCategories;

      await updatePrompt.mutateAsync(promptData);
      message.success('Prompt updated successfully');
      navigate(`/prompts/${promptId}`);
    } catch {
      message.error('Failed to update prompt');
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
          onClick={() => navigate(`/prompts/${promptId}`)}
        >
          Back
        </Button>
      </Space>

      <Title level={2}>Edit Prompt</Title>

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
            <Input placeholder="e.g., Product Launch Tweet" />
          </Form.Item>

          <Form.Item
            name="details"
            label="Prompt Details"
            rules={[{ required: true, message: 'Please enter the prompt details' }]}
            extra="The main prompt template text. Use {variable} syntax for placeholders."
          >
            <TextArea rows={8} />
          </Form.Item>

          <Divider orientation="left">
            Customer Info{' '}
            <Tooltip title="Select which customer info categories to inject into this prompt during generation">
              <InfoCircleOutlined style={{ color: '#999' }} />
            </Tooltip>
          </Divider>

          <Form.Item
            name="selectedCategories"
            label={
              <Space>
                <span>Categories to Include</span>
                <Text type="secondary" style={{ fontWeight: 'normal' }}>
                  (only categories with data are shown)
                </Text>
              </Space>
            }
          >
            <Checkbox.Group style={{ width: '100%' }}>
              <Row gutter={[16, 8]}>
                {CUSTOMER_CATEGORIES.filter(cat => categoriesWithData.has(cat)).map((category) => {
                  const injectionType = getInjectionType(category);
                  return (
                    <Col span={12} key={category}>
                      <Checkbox value={category} disabled={injectionType === 'ignored'}>
                        <Space>
                          {category}
                          <Tag
                            color={INJECTION_TYPE_COLORS[injectionType]}
                            style={{ marginLeft: 4 }}
                          >
                            {INJECTION_TYPE_LABELS[injectionType]}
                          </Tag>
                        </Space>
                      </Checkbox>
                    </Col>
                  );
                })}
              </Row>
            </Checkbox.Group>
          </Form.Item>

          {categoriesWithData.size === 0 && (
            <Text type="secondary">
              No customer info categories have data yet.{' '}
              <a onClick={() => navigate('/settings/customer-info')}>
                Configure Customer Info
              </a>
            </Text>
          )}

          <Form.Item
            name="artwork_description"
            label="Artwork Description"
            tooltip="Description for image generation"
          >
            <TextArea
              rows={3}
              placeholder="Describe the visual style or artwork for this prompt..."
            />
          </Form.Item>

          <Divider orientation="left">References</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="url"
                label="Reference URL"
                tooltip="OneDrive or reference URL for brand assets"
              >
                <Input placeholder="https://..." />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="example_image"
                label="Example Image URL"
                tooltip="Reference image for style guidance"
              >
                <Input placeholder="https://... or S3 URL" />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="media_file_path"
                label="Media File Path"
                tooltip="Local media file path"
              >
                <Input placeholder="/path/to/media" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="aws_folder_url"
                label="AWS Folder URL"
                tooltip="S3 folder URL for media assets"
              >
                <Input placeholder="s3://bucket/folder" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={updatePrompt.isPending}
              >
                Save Changes
              </Button>
              <Button onClick={() => navigate(`/prompts/${promptId}`)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
