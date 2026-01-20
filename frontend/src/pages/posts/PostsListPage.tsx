import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Button,
  Input,
  Select,
  Space,
  Typography,
  Tag,
  Popconfirm,
  message,
  DatePicker,
  Tooltip,
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { usePosts, useDeletePost, useExportPostsCSV } from '@/hooks/usePosts';
import type { Post, PostStatus } from '@/types';

const { Title } = Typography;
const { RangePicker } = DatePicker;

const statusColors: Record<PostStatus, string> = {
  draft: 'default',
  scheduled: 'processing',
  published: 'success',
};

export function PostsListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<PostStatus | undefined>();
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading } = usePosts({
    skip: (page - 1) * pageSize,
    limit: pageSize,
    search: search || undefined,
    status,
  });

  const deletePost = useDeletePost();
  const exportCSV = useExportPostsCSV();

  const handleDelete = async (id: number) => {
    try {
      await deletePost.mutateAsync(id);
      message.success('Post deleted successfully');
    } catch {
      message.error('Failed to delete post');
    }
  };

  const handleExportCSV = async () => {
    try {
      await exportCSV.mutateAsync({ status });
      message.success('CSV exported successfully');
    } catch {
      message.error('Failed to export CSV');
    }
  };

  const columns: ColumnsType<Post> = [
    {
      title: 'Content',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content, record) => (
        <a onClick={() => navigate(`/posts/${record.id}`)}>
          {content.substring(0, 80)}
          {content.length > 80 ? '...' : ''}
        </a>
      ),
    },
    {
      title: 'Type',
      dataIndex: 'graphic_type',
      key: 'graphic_type',
      width: 100,
      render: (type: string | undefined) => type ? <Tag>{type}</Tag> : '-',
    },
    {
      title: 'Status',
      dataIndex: 'status',
      key: 'status',
      width: 100,
      render: (status: PostStatus) => (
        <Tag color={statusColors[status]}>{status.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Flags',
      key: 'flags',
      width: 80,
      render: (_, record) => (
        <Space>
          {record.keep && (
            <Tooltip title="Ready to Publish">
              <CheckCircleOutlined style={{ color: '#52c41a' }} />
            </Tooltip>
          )}
          {record.for_deletion && (
            <Tooltip title="Marked for Deletion">
              <CloseCircleOutlined style={{ color: '#ff4d4f' }} />
            </Tooltip>
          )}
          {!record.keep && !record.for_deletion && '-'}
        </Space>
      ),
    },
    {
      title: 'Media',
      dataIndex: 'media_urls',
      key: 'media',
      width: 70,
      render: (urls: string[]) => urls.length > 0 ? `${urls.length}` : '-',
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
      width: 100,
      render: (date) => new Date(date).toLocaleDateString(),
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            icon={<EyeOutlined />}
            size="small"
            onClick={() => navigate(`/posts/${record.id}`)}
          />
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/posts/${record.id}/edit`)}
          />
          <Popconfirm
            title="Delete this post?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.id)}
            okText="Delete"
            okType="danger"
          >
            <Button icon={<DeleteOutlined />} size="small" danger />
          </Popconfirm>
        </Space>
      ),
    },
  ];

  return (
    <div>
      <div className="tw-flex tw-justify-between tw-items-center tw-mb-4">
        <Title level={2} style={{ margin: 0 }}>Posts</Title>
        <Space>
          <Button
            icon={<DownloadOutlined />}
            onClick={handleExportCSV}
            loading={exportCSV.isPending}
          >
            Export CSV
          </Button>
          <Button
            type="primary"
            icon={<PlusOutlined />}
            onClick={() => navigate('/posts/new')}
          >
            New Post
          </Button>
        </Space>
      </div>

      <Space className="tw-mb-4" wrap>
        <Input
          placeholder="Search posts..."
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 250 }}
          allowClear
        />
        <Select
          placeholder="Filter by status"
          value={status}
          onChange={setStatus}
          style={{ width: 150 }}
          allowClear
          options={[
            { value: 'draft', label: 'Draft' },
            { value: 'scheduled', label: 'Scheduled' },
            { value: 'published', label: 'Published' },
          ]}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={data?.items}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: setPage,
          showSizeChanger: false,
          showTotal: (total) => `Total ${total} posts`,
        }}
      />
    </div>
  );
}
