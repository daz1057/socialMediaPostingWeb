import { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import {
  Table,
  Button,
  Input,
  Space,
  Typography,
  Tag,
  Popconfirm,
  message,
} from 'antd';
import { PlusOutlined, SearchOutlined, EditOutlined, DeleteOutlined, EyeOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { usePrompts, useDeletePrompt } from '@/hooks/usePrompts';
import type { Prompt } from '@/types';

const { Title } = Typography;

export function PromptsListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading } = usePrompts({
    skip: (page - 1) * pageSize,
    limit: pageSize,
    search: search || undefined,
  });

  const deletePrompt = useDeletePrompt();

  const handleDelete = async (id: number) => {
    try {
      await deletePrompt.mutateAsync(id);
      message.success('Prompt deleted successfully');
    } catch {
      message.error('Failed to delete prompt');
    }
  };

  const columns: ColumnsType<Prompt> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <a onClick={() => navigate(`/prompts/${record.id}`)}>{name}</a>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'details',
      key: 'details',
      ellipsis: true,
      render: (details) => details ? details.substring(0, 100) + (details.length > 100 ? '...' : '') : '-',
    },
    {
      title: 'Tags',
      dataIndex: 'tag',
      key: 'tag',
      render: (tag: Prompt['tag']) => (
        tag ? <Tag>{tag.name}</Tag> : '-'
      ),
    },
    {
      title: 'Created',
      dataIndex: 'created_at',
      key: 'created_at',
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
            onClick={() => navigate(`/prompts/${record.id}`)}
          />
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/prompts/${record.id}/edit`)}
          />
          <Popconfirm
            title="Delete this prompt?"
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
        <Title level={2} style={{ margin: 0 }}>Prompts</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/prompts/new')}
        >
          New Prompt
        </Button>
      </div>

      <div className="tw-mb-4">
        <Input
          placeholder="Search prompts..."
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 300 }}
          allowClear
        />
      </div>

      <Table
        columns={columns}
        dataSource={data?.prompts}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: setPage,
          showSizeChanger: false,
          showTotal: (total) => `Total ${total} prompts`,
        }}
      />
    </div>
  );
}
