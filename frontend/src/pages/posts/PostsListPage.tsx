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
  Tooltip,
  Tabs,
} from 'antd';
import type { TableRowSelection } from 'antd/es/table/interface';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  DownloadOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  InboxOutlined,
  UndoOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  usePosts,
  useDeletePost,
  useExportPostsCSV,
  useArchivePost,
  useRestorePost,
  useBulkArchivePosts,
  useBulkRestorePosts,
} from '@/hooks/usePosts';
import type { Post, PostStatus } from '@/types';

const { Title } = Typography;

const statusColors: Record<PostStatus, string> = {
  draft: 'default',
  scheduled: 'processing',
  published: 'success',
};

export function PostsListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [status, setStatus] = useState<PostStatus | undefined>();
  const [isArchived, setIsArchived] = useState(false);
  const [page, setPage] = useState(1);
  const [selectedRowKeys, setSelectedRowKeys] = useState<number[]>([]);
  const pageSize = 10;

  const { data, isLoading } = usePosts({
    skip: (page - 1) * pageSize,
    limit: pageSize,
    search: search || undefined,
    status,
    isArchived,
  });

  const deletePost = useDeletePost();
  const exportCSV = useExportPostsCSV();
  const archivePost = useArchivePost();
  const restorePost = useRestorePost();
  const bulkArchive = useBulkArchivePosts();
  const bulkRestore = useBulkRestorePosts();

  const handleTabChange = (key: string) => {
    setIsArchived(key === 'archived');
    setPage(1);
    setSelectedRowKeys([]);
    setStatus(undefined);
  };

  const handleDelete = async (id: number) => {
    try {
      await deletePost.mutateAsync(id);
      message.success('Post deleted successfully');
    } catch {
      message.error('Failed to delete post');
    }
  };

  const handleArchive = async (id: number) => {
    try {
      await archivePost.mutateAsync(id);
      message.success('Post archived successfully');
    } catch {
      message.error('Failed to archive post');
    }
  };

  const handleRestore = async (id: number) => {
    try {
      await restorePost.mutateAsync(id);
      message.success('Post restored successfully');
    } catch {
      message.error('Failed to restore post');
    }
  };

  const handleBulkArchive = async () => {
    try {
      const result = await bulkArchive.mutateAsync(selectedRowKeys);
      message.success(result.message);
      setSelectedRowKeys([]);
    } catch {
      message.error('Failed to archive posts');
    }
  };

  const handleBulkRestore = async () => {
    try {
      const result = await bulkRestore.mutateAsync(selectedRowKeys);
      message.success(result.message);
      setSelectedRowKeys([]);
    } catch {
      message.error('Failed to restore posts');
    }
  };

  const handleExportCSV = async () => {
    try {
      await exportCSV.mutateAsync({ status, isArchived });
      message.success('CSV exported successfully');
    } catch {
      message.error('Failed to export CSV');
    }
  };

  const rowSelection: TableRowSelection<Post> = {
    selectedRowKeys,
    onChange: (keys) => setSelectedRowKeys(keys as number[]),
    getCheckboxProps: (record) => ({
      // Only allow archiving published posts (when viewing active posts)
      disabled: !isArchived && record.status !== 'published',
    }),
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
      width: 150,
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
          {/* Archive button - only for published, non-archived posts */}
          {!isArchived && record.status === 'published' && (
            <Popconfirm
              title="Archive this post?"
              description="The post will be moved to the archive."
              onConfirm={() => handleArchive(record.id)}
              okText="Archive"
            >
              <Tooltip title="Archive">
                <Button
                  icon={<InboxOutlined />}
                  size="small"
                  loading={archivePost.isPending}
                />
              </Tooltip>
            </Popconfirm>
          )}
          {/* Restore button - only for archived posts */}
          {isArchived && (
            <Popconfirm
              title="Restore this post?"
              description="The post will be restored to active posts."
              onConfirm={() => handleRestore(record.id)}
              okText="Restore"
            >
              <Tooltip title="Restore">
                <Button
                  icon={<UndoOutlined />}
                  size="small"
                  type="primary"
                  ghost
                  loading={restorePost.isPending}
                />
              </Tooltip>
            </Popconfirm>
          )}
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

      <Tabs
        activeKey={isArchived ? 'archived' : 'active'}
        onChange={handleTabChange}
        items={[
          { key: 'active', label: 'Active Posts' },
          { key: 'archived', label: 'Archived Posts' },
        ]}
      />

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
        {/* Bulk action buttons */}
        {selectedRowKeys.length > 0 && (
          <>
            {!isArchived ? (
              <Popconfirm
                title={`Archive ${selectedRowKeys.length} posts?`}
                description="Selected posts will be moved to the archive."
                onConfirm={handleBulkArchive}
                okText="Archive"
              >
                <Button
                  icon={<InboxOutlined />}
                  loading={bulkArchive.isPending}
                >
                  Archive Selected ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            ) : (
              <Popconfirm
                title={`Restore ${selectedRowKeys.length} posts?`}
                description="Selected posts will be restored to active posts."
                onConfirm={handleBulkRestore}
                okText="Restore"
              >
                <Button
                  icon={<UndoOutlined />}
                  type="primary"
                  ghost
                  loading={bulkRestore.isPending}
                >
                  Restore Selected ({selectedRowKeys.length})
                </Button>
              </Popconfirm>
            )}
          </>
        )}
      </Space>

      <Table
        columns={columns}
        dataSource={data?.posts}
        rowKey="id"
        loading={isLoading}
        rowSelection={rowSelection}
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
