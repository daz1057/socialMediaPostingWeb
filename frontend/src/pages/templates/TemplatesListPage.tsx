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
} from 'antd';
import {
  PlusOutlined,
  SearchOutlined,
  EditOutlined,
  DeleteOutlined,
  EyeOutlined,
  CopyOutlined,
} from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import { useTemplates, useDeleteTemplate, useTemplateTags } from '@/hooks/useTemplates';
import type { Template, TemplateCategory } from '@/types';
import { TEMPLATE_CATEGORIES } from '@/types';

const { Title } = Typography;

const categoryColors: Record<TemplateCategory, string> = {
  ocr: 'blue',
  manual: 'green',
  custom: 'purple',
};

export function TemplatesListPage() {
  const navigate = useNavigate();
  const [search, setSearch] = useState('');
  const [category, setCategory] = useState<TemplateCategory | undefined>();
  const [selectedTag, setSelectedTag] = useState<string | undefined>();
  const [page, setPage] = useState(1);
  const pageSize = 10;

  const { data, isLoading } = useTemplates({
    skip: (page - 1) * pageSize,
    limit: pageSize,
    search: search || undefined,
    category,
    tag: selectedTag,
  });

  const { data: availableTags } = useTemplateTags();
  const deleteTemplate = useDeleteTemplate();

  const handleDelete = async (id: number) => {
    try {
      await deleteTemplate.mutateAsync(id);
      message.success('Template deleted successfully');
    } catch {
      message.error('Failed to delete template');
    }
  };

  const handleCopyContent = (content: string) => {
    navigator.clipboard.writeText(content);
    message.success('Content copied to clipboard');
  };

  const columns: ColumnsType<Template> = [
    {
      title: 'Name',
      dataIndex: 'name',
      key: 'name',
      render: (name, record) => (
        <a onClick={() => navigate(`/templates/${record.id}`)}>
          {name}
        </a>
      ),
    },
    {
      title: 'Category',
      dataIndex: 'category',
      key: 'category',
      width: 100,
      render: (cat: TemplateCategory) => (
        <Tag color={categoryColors[cat]}>{cat.toUpperCase()}</Tag>
      ),
    },
    {
      title: 'Tags',
      dataIndex: 'tags',
      key: 'tags',
      width: 200,
      render: (tags: string[]) => (
        <Space size={[0, 4]} wrap>
          {tags.slice(0, 3).map((tag) => (
            <Tag key={tag}>{tag}</Tag>
          ))}
          {tags.length > 3 && <Tag>+{tags.length - 3}</Tag>}
        </Space>
      ),
    },
    {
      title: 'Content Preview',
      dataIndex: 'content',
      key: 'content',
      ellipsis: true,
      render: (content) => (
        <span>{content.substring(0, 80)}{content.length > 80 ? '...' : ''}</span>
      ),
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
            onClick={() => navigate(`/templates/${record.id}`)}
          />
          <Button
            icon={<CopyOutlined />}
            size="small"
            onClick={() => handleCopyContent(record.content)}
            title="Copy content"
          />
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => navigate(`/templates/${record.id}/edit`)}
          />
          <Popconfirm
            title="Delete this template?"
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
        <Title level={2} style={{ margin: 0 }}>Templates</Title>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => navigate('/templates/new')}
        >
          New Template
        </Button>
      </div>

      <Space className="tw-mb-4" wrap>
        <Input
          placeholder="Search templates..."
          prefix={<SearchOutlined />}
          value={search}
          onChange={(e) => setSearch(e.target.value)}
          style={{ width: 250 }}
          allowClear
        />
        <Select
          placeholder="Filter by category"
          value={category}
          onChange={setCategory}
          style={{ width: 150 }}
          allowClear
          options={TEMPLATE_CATEGORIES}
        />
        <Select
          placeholder="Filter by tag"
          value={selectedTag}
          onChange={setSelectedTag}
          style={{ width: 150 }}
          allowClear
          options={availableTags?.map((tag) => ({ value: tag, label: tag })) || []}
        />
      </Space>

      <Table
        columns={columns}
        dataSource={data?.templates}
        rowKey="id"
        loading={isLoading}
        pagination={{
          current: page,
          pageSize,
          total: data?.total,
          onChange: setPage,
          showSizeChanger: false,
          showTotal: (total) => `Total ${total} templates`,
        }}
      />
    </div>
  );
}
