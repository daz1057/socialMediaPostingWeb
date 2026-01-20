import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Divider, Row, Col } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useCreatePrompt } from '@/hooks/usePrompts';
import type { PromptCreate } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function PromptCreatePage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const createPrompt = useCreatePrompt();

  const onFinish = async (values: PromptCreate) => {
    try {
      const prompt = await createPrompt.mutateAsync(values);
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
