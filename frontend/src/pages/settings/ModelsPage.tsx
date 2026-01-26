import { useState } from 'react';
import {
  Table,
  Button,
  Modal,
  Form,
  Input,
  Select,
  Typography,
  Space,
  Switch,
  Popconfirm,
  message,
  Tag,
  Cascader,
} from 'antd';
import { PlusOutlined, DeleteOutlined, EditOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useModelConfigs,
  useProviders,
  useCreateModelConfig,
  useUpdateModelConfig,
  useDeleteModelConfig,
} from '@/hooks/useModels';
import type { ModelConfig, ModelConfigCreate, ModelType } from '@/types';

const { Title, Text } = Typography;

export function ModelsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [editingModel, setEditingModel] = useState<ModelConfig | null>(null);
  const [form] = Form.useForm();

  const { data, isLoading } = useModelConfigs();
  const { data: providersData, isLoading: providersLoading } = useProviders();
  const createModelConfig = useCreateModelConfig();
  const updateModelConfig = useUpdateModelConfig(editingModel?.id ?? 0);
  const deleteModelConfig = useDeleteModelConfig();

  // Build cascader options for provider/model selection
  const cascaderOptions = providersData?.providers.map((provider) => ({
    value: provider.provider_name,
    label: provider.display_name,
    children: provider.models.map((model) => ({
      value: model.model_id,
      label: model.display_name,
      model_type: model.model_type,
    })),
  })) ?? [];

  const handleCreate = async (values: { provider_model: string[]; display_name?: string; is_enabled: boolean; is_default: boolean }) => {
    const [provider, model_id] = values.provider_model;
    const providerData = providersData?.providers.find((p) => p.provider_name === provider);
    const modelData = providerData?.models.find((m) => m.model_id === model_id);

    try {
      await createModelConfig.mutateAsync({
        provider,
        model_id,
        model_type: modelData?.model_type ?? 'text',
        display_name: values.display_name,
        is_enabled: values.is_enabled,
        is_default: values.is_default,
      });
      message.success('Model configuration added');
      setIsModalOpen(false);
      form.resetFields();
    } catch {
      message.error('Failed to add model configuration');
    }
  };

  const handleUpdate = async (values: { display_name?: string; is_enabled: boolean; is_default: boolean }) => {
    if (!editingModel) return;

    try {
      await updateModelConfig.mutateAsync({
        display_name: values.display_name,
        is_enabled: values.is_enabled,
        is_default: values.is_default,
      });
      message.success('Model configuration updated');
      setEditingModel(null);
      form.resetFields();
    } catch {
      message.error('Failed to update model configuration');
    }
  };

  const handleDelete = async (id: number) => {
    try {
      await deleteModelConfig.mutateAsync(id);
      message.success('Model configuration deleted');
    } catch {
      message.error('Failed to delete model configuration');
    }
  };

  const openEditModal = (model: ModelConfig) => {
    setEditingModel(model);
    form.setFieldsValue({
      display_name: model.display_name,
      is_enabled: model.is_enabled,
      is_default: model.is_default,
    });
  };

  const columns: ColumnsType<ModelConfig> = [
    {
      title: 'Provider',
      dataIndex: 'provider',
      key: 'provider',
    },
    {
      title: 'Model',
      dataIndex: 'model_id',
      key: 'model_id',
    },
    {
      title: 'Display Name',
      dataIndex: 'display_name',
      key: 'display_name',
      render: (name, record) => name || `${record.provider} / ${record.model_id}`,
    },
    {
      title: 'Type',
      dataIndex: 'model_type',
      key: 'model_type',
      render: (type: ModelType) => (
        <Tag color={type === 'text' ? 'blue' : 'purple'}>
          {type.toUpperCase()}
        </Tag>
      ),
    },
    {
      title: 'Enabled',
      dataIndex: 'is_enabled',
      key: 'is_enabled',
      render: (enabled) => (
        <Tag color={enabled ? 'success' : 'default'}>
          {enabled ? 'Yes' : 'No'}
        </Tag>
      ),
    },
    {
      title: 'Default',
      dataIndex: 'is_default',
      key: 'is_default',
      render: (isDefault) => isDefault ? <Tag color="gold">Default</Tag> : '-',
    },
    {
      title: 'Actions',
      key: 'actions',
      width: 120,
      render: (_, record) => (
        <Space>
          <Button
            icon={<EditOutlined />}
            size="small"
            onClick={() => openEditModal(record)}
          />
          <Popconfirm
            title="Delete this model configuration?"
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
        <div>
          <Title level={2} style={{ margin: 0 }}>Model Configuration</Title>
          <Text type="secondary">Configure AI models for text and image generation</Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => {
            setEditingModel(null);
            form.resetFields();
            setIsModalOpen(true);
          }}
        >
          Add Model
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data?.models}
        rowKey="id"
        loading={isLoading}
        pagination={false}
      />

      {/* Create Modal */}
      <Modal
        title="Add Model Configuration"
        open={isModalOpen && !editingModel}
        onCancel={() => {
          setIsModalOpen(false);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleCreate}
          initialValues={{ is_enabled: true, is_default: false }}
        >
          <Form.Item
            name="provider_model"
            label="Provider / Model"
            rules={[{ required: true, message: 'Please select a model' }]}
          >
            <Cascader
              options={cascaderOptions}
              placeholder="Select provider and model"
              loading={providersLoading}
              expandTrigger="hover"
            />
          </Form.Item>

          <Form.Item
            name="display_name"
            label="Display Name (optional)"
          >
            <Input placeholder="e.g., GPT-4 Turbo" />
          </Form.Item>

          <Form.Item
            name="is_enabled"
            label="Enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="is_default"
            label="Set as Default"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createModelConfig.isPending}
              >
                Add Model
              </Button>
              <Button onClick={() => {
                setIsModalOpen(false);
                form.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>

      {/* Edit Modal */}
      <Modal
        title="Edit Model Configuration"
        open={!!editingModel}
        onCancel={() => {
          setEditingModel(null);
          form.resetFields();
        }}
        footer={null}
      >
        <Form
          form={form}
          layout="vertical"
          onFinish={handleUpdate}
        >
          <Form.Item label="Provider / Model">
            <Text>{editingModel?.provider} / {editingModel?.model_id}</Text>
          </Form.Item>

          <Form.Item
            name="display_name"
            label="Display Name"
          >
            <Input placeholder="e.g., GPT-4 Turbo" />
          </Form.Item>

          <Form.Item
            name="is_enabled"
            label="Enabled"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item
            name="is_default"
            label="Set as Default"
            valuePropName="checked"
          >
            <Switch />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={updateModelConfig.isPending}
              >
                Save Changes
              </Button>
              <Button onClick={() => {
                setEditingModel(null);
                form.resetFields();
              }}>
                Cancel
              </Button>
            </Space>
          </Form.Item>
        </Form>
      </Modal>
    </div>
  );
}
