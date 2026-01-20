import { useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Select, Switch, Row, Col, Divider } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { useCreatePost } from '@/hooks/usePosts';
import type { PostCreate, PostStatus } from '@/types';
import { GRAPHIC_TYPES } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function PostCreatePage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const createPost = useCreatePost();

  const onFinish = async (values: PostCreate) => {
    try {
      const post = await createPost.mutateAsync(values);
      message.success('Post created successfully');
      navigate(`/posts/${post.id}`);
    } catch {
      message.error('Failed to create post');
    }
  };

  return (
    <div>
      <Space className="tw-mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate('/posts')}
        >
          Back
        </Button>
      </Space>

      <Title level={2}>Create Post</Title>

      <Card style={{ maxWidth: 900 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
          initialValues={{ status: 'draft', keep: false, for_deletion: false }}
        >
          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter post content' }]}
          >
            <TextArea
              rows={6}
              placeholder="Write your social media post content here..."
              showCount
              maxLength={2000}
            />
          </Form.Item>

          <Form.Item
            name="caption"
            label="Caption"
            tooltip="Platform-specific caption (optional)"
          >
            <TextArea
              rows={3}
              placeholder="Platform-specific caption..."
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Form.Item
            name="alt_text"
            label="Alt Text"
            tooltip="Accessibility text for images"
          >
            <TextArea
              rows={2}
              placeholder="Describe the image for screen readers..."
              showCount
              maxLength={500}
            />
          </Form.Item>

          <Divider orientation="left">Metadata</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="status"
                label="Status"
              >
                <Select
                  options={[
                    { value: 'draft', label: 'Draft' },
                    { value: 'scheduled', label: 'Scheduled' },
                  ]}
                />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="graphic_type"
                label="Graphic Type"
              >
                <Select
                  placeholder="Select graphic type"
                  allowClear
                  options={GRAPHIC_TYPES.map((type) => ({ value: type, label: type }))}
                />
              </Form.Item>
            </Col>
          </Row>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="source_url"
                label="Source URL"
                tooltip="Reference URL for the content"
              >
                <Input placeholder="https://..." />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="original_prompt_name"
                label="Original Prompt Name"
                tooltip="Name of the prompt used to generate this post"
              >
                <Input placeholder="Prompt name..." />
              </Form.Item>
            </Col>
          </Row>

          <Divider orientation="left">Flags</Divider>

          <Row gutter={16}>
            <Col span={12}>
              <Form.Item
                name="keep"
                label="Ready to Publish"
                valuePropName="checked"
              >
                <Switch checkedChildren="Yes" unCheckedChildren="No" />
              </Form.Item>
            </Col>
            <Col span={12}>
              <Form.Item
                name="for_deletion"
                label="Mark for Deletion"
                valuePropName="checked"
              >
                <Switch checkedChildren="Yes" unCheckedChildren="No" />
              </Form.Item>
            </Col>
          </Row>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createPost.isPending}
              >
                Create Post
              </Button>
              <Button onClick={() => navigate('/posts')}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
