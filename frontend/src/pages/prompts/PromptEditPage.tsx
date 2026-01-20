import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Spin, Divider, Row, Col } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePrompt, useUpdatePrompt } from '@/hooks/usePrompts';
import type { PromptUpdate } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function PromptEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const promptId = parseInt(id || '0', 10);
  const { data: prompt, isLoading } = usePrompt(promptId);
  const updatePrompt = useUpdatePrompt(promptId);

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
      });
    }
  }, [prompt, form]);

  const onFinish = async (values: PromptUpdate) => {
    try {
      await updatePrompt.mutateAsync(values);
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
