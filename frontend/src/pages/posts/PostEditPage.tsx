import { useEffect } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, message, Space, Spin, Select, Switch, Row, Col, Divider } from 'antd';
import { ArrowLeftOutlined } from '@ant-design/icons';
import { usePost, useUpdatePost } from '@/hooks/usePosts';
import type { PostUpdate } from '@/types';
import { GRAPHIC_TYPES } from '@/types';

const { Title } = Typography;
const { TextArea } = Input;

export function PostEditPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();
  const [form] = Form.useForm();

  const postId = parseInt(id || '0', 10);
  const { data: post, isLoading } = usePost(postId);
  const updatePost = useUpdatePost(postId);

  useEffect(() => {
    if (post) {
      form.setFieldsValue({
        content: post.content,
        caption: post.caption,
        alt_text: post.alt_text,
        status: post.status,
        graphic_type: post.graphic_type,
        source_url: post.source_url,
        original_prompt_name: post.original_prompt_name,
        keep: post.keep,
        for_deletion: post.for_deletion,
      });
    }
  }, [post, form]);

  const onFinish = async (values: PostUpdate) => {
    try {
      await updatePost.mutateAsync(values);
      message.success('Post updated successfully');
      navigate(`/posts/${postId}`);
    } catch {
      message.error('Failed to update post');
    }
  };

  if (isLoading) {
    return (
      <div className="tw-flex tw-justify-center tw-items-center tw-h-64">
        <Spin size="large" />
      </div>
    );
  }

  if (!post) {
    return (
      <div>
        <Title level={4}>Post not found</Title>
        <Button onClick={() => navigate('/posts')}>Back to Posts</Button>
      </div>
    );
  }

  return (
    <div>
      <Space className="tw-mb-4">
        <Button
          icon={<ArrowLeftOutlined />}
          onClick={() => navigate(`/posts/${postId}`)}
        >
          Back
        </Button>
      </Space>

      <Title level={2}>Edit Post</Title>

      <Card style={{ maxWidth: 900 }}>
        <Form
          form={form}
          layout="vertical"
          onFinish={onFinish}
        >
          <Form.Item
            name="content"
            label="Content"
            rules={[{ required: true, message: 'Please enter post content' }]}
          >
            <TextArea
              rows={6}
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
                    { value: 'published', label: 'Published' },
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
                loading={updatePost.isPending}
              >
                Save Changes
              </Button>
              <Button onClick={() => navigate(`/posts/${postId}`)}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Card>
    </div>
  );
}
