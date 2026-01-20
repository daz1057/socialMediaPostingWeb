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
      dataIndex: 'description',
      key: 'description',
      ellipsis: true,
      render: (desc) => desc || '-',
    },
    {
      title: 'Tags',
      dataIndex: 'tags',
      key: 'tags',
      render: (tags: Prompt['tags']) => (
        <>
          {tags.slice(0, 3).map((tag) => (
            <Tag key={tag.id}>{tag.name}</Tag>
          ))}
          {tags.length > 3 && <Tag>+{tags.length - 3}</Tag>}
        </>
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
        dataSource={data?.items}
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
