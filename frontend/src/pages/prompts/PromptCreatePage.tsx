import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Divider, Row, Col, Checkbox, Tag, Tooltip } from 'antd';
import { ArrowLeftOutlined, InfoCircleOutlined } from '@ant-design/icons';
import { useCreatePrompt } from '@/hooks/usePrompts';
import { useCustomerInfoList } from '@/hooks';
import type { PromptCreate, CustomerCategory, InjectionType } from '@/types';
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

export function PromptCreatePage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const createPrompt = useCreatePrompt();
  const { data: customerInfoList } = useCustomerInfoList();

  // Get categories that have data
  const categoriesWithData = new Set<CustomerCategory>();
  customerInfoList?.customer_info.forEach((info) => {
    if (info.details && info.details.length > 0) {
      categoriesWithData.add(info.category);
    }
  });

  const onFinish = async (values: PromptCreate & { selectedCategories?: CustomerCategory[] }) => {
    try {
      // Convert selected categories array to Record<string, boolean>
      const selected_customers: Record<string, boolean> = {};
      if (values.selectedCategories) {
        values.selectedCategories.forEach((cat) => {
          selected_customers[cat] = true;
        });
      }

      const promptData: PromptCreate = {
        ...values,
        selected_customers,
      };
      delete (promptData as { selectedCategories?: CustomerCategory[] }).selectedCategories;

      const prompt = await createPrompt.mutateAsync(promptData);
      message.success('Prompt created successfully');
      navigate(`/prompts/${prompt.id}`);
    } catch {
      message.error('Failed to create prompt');
    }
  };

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

      <Title level={2}>Create Prompt</Title>

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
            <TextArea
              rows={8}
              placeholder={`Write a compelling social media post about {topic}.\n\nThe tone should be {tone} and target {audience}.\n\nInclude a call to action.`}
            />
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
                loading={createPrompt.isPending}
              >
                Create Prompt
              </Button>
              <Button onClick={() => navigate('/prompts')}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
