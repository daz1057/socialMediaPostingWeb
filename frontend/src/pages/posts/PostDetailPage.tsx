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
  Image,
} from 'antd';
import {
  ArrowLeftOutlined,
  EditOutlined,
  DeleteOutlined,
  CheckCircleOutlined,
} from '@ant-design/icons';
import { usePost, useDeletePost, usePublishPost } from '@/hooks/usePosts';
import type { PostStatus } from '@/types';

const { Title, Paragraph } = Typography;

const statusColors: Record<PostStatus, string> = {
  draft: 'default',
  scheduled: 'processing',
  published: 'success',
};

export function PostDetailPage() {
  const { id } = useParams<{ id: string }>();
  const navigate = useNavigate();

  const postId = parseInt(id || '0', 10);
  const { data: post, isLoading } = usePost(postId);
  const deletePost = useDeletePost();
  const publishPost = usePublishPost();

  const handleDelete = async () => {
    try {
      await deletePost.mutateAsync(postId);
      message.success('Post deleted successfully');
      navigate('/posts');
    } catch {
      message.error('Failed to delete post');
    }
  };

  const handlePublish = async () => {
    try {
      await publishPost.mutateAsync(postId);
      message.success('Post published successfully');
    } catch {
      message.error('Failed to publish post');
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
          onClick={() => navigate('/posts')}
        >
          Back
        </Button>
      </Space>

      <div className="tw-flex tw-justify-between tw-items-start tw-mb-4">
        <div>
          <Title level={2} style={{ margin: 0 }}>Post Details</Title>
          <Tag color={statusColors[post.status]} style={{ marginTop: 8 }}>
            {post.status.toUpperCase()}
          </Tag>
        </div>
        <Space>
          {post.status === 'draft' && (
            <Popconfirm
              title="Publish this post?"
              description="Mark this post as published."
              onConfirm={handlePublish}
              okText="Publish"
            >
              <Button
                type="primary"
                icon={<CheckCircleOutlined />}
                loading={publishPost.isPending}
              >
                Publish
              </Button>
            </Popconfirm>
          )}
          <Button
            icon={<EditOutlined />}
            onClick={() => navigate(`/posts/${post.id}/edit`)}
          >
            Edit
          </Button>
          <Popconfirm
            title="Delete this post?"
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
          <Descriptions.Item label="Status">
            <Tag color={statusColors[post.status]}>{post.status.toUpperCase()}</Tag>
          </Descriptions.Item>
          <Descriptions.Item label="Created">
            {new Date(post.created_at).toLocaleString()}
          </Descriptions.Item>
          {post.scheduled_at && (
            <Descriptions.Item label="Scheduled For">
              {new Date(post.scheduled_at).toLocaleString()}
            </Descriptions.Item>
          )}
          {post.published_at && (
            <Descriptions.Item label="Published At">
              {new Date(post.published_at).toLocaleString()}
            </Descriptions.Item>
          )}
          {post.updated_at && (
            <Descriptions.Item label="Last Updated">
              {new Date(post.updated_at).toLocaleString()}
            </Descriptions.Item>
          )}
        </Descriptions>
      </Card>

      <Card title="Content" style={{ marginTop: 16 }}>
        <Paragraph>
          <pre style={{
            whiteSpace: 'pre-wrap',
            wordWrap: 'break-word',
            background: '#f5f5f5',
            padding: 16,
            borderRadius: 8,
            margin: 0,
          }}>
            {post.content}
          </pre>
        </Paragraph>
      </Card>

      {post.media_urls.length > 0 && (
        <Card title="Media" style={{ marginTop: 16 }}>
          <Image.PreviewGroup>
            <Space wrap>
              {post.media_urls.map((url, index) => (
                <Image
                  key={index}
                  src={url}
                  width={150}
                  height={150}
                  style={{ objectFit: 'cover', borderRadius: 8 }}
                />
              ))}
            </Space>
          </Image.PreviewGroup>
        </Card>
      )}
    </div>
  );
}
