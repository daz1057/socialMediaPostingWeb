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
  Popconfirm,
  message,
  Tag,
} from 'antd';
import { PlusOutlined, DeleteOutlined, CheckCircleOutlined, KeyOutlined } from '@ant-design/icons';
import type { ColumnsType } from 'antd/es/table';
import {
  useCredentials,
  useCreateCredential,
  useDeleteCredential,
  useValidateCredential,
} from '@/hooks/useCredentials';
import { useProviders } from '@/hooks/useModels';
import type { Credential, CredentialCreate } from '@/types';

const { Title, Text } = Typography;

export function CredentialsPage() {
  const [isModalOpen, setIsModalOpen] = useState(false);
  const [form] = Form.useForm();
  const [validatingKey, setValidatingKey] = useState<string | null>(null);

  const { data, isLoading } = useCredentials();
  const { data: providersData } = useProviders();
  const createCredential = useCreateCredential();
  const deleteCredential = useDeleteCredential();
  const validateCredential = useValidateCredential();

  // Collect all unique credential keys from providers
  const credentialKeyOptions = providersData?.providers
    .flatMap((p) => p.credential_keys)
    .filter((key, index, self) => self.indexOf(key) === index)
    .map((key) => ({ value: key, label: key })) ?? [];

  const handleCreate = async (values: CredentialCreate) => {
    try {
      await createCredential.mutateAsync(values);
      message.success('Credential added successfully');
      setIsModalOpen(false);
      form.resetFields();
    } catch {
      message.error('Failed to add credential');
    }
  };

  const handleDelete = async (key: string) => {
    try {
      await deleteCredential.mutateAsync(key);
      message.success('Credential deleted successfully');
    } catch {
      message.error('Failed to delete credential');
    }
  };

  const handleValidate = async (key: string) => {
    setValidatingKey(key);
    try {
      const result = await validateCredential.mutateAsync({ key });
      if (result.is_valid) {
        message.success(result.message || 'Credential is valid');
      } else {
        message.error(result.message || 'Credential is invalid');
      }
    } catch {
      message.error('Validation failed');
    } finally {
      setValidatingKey(null);
    }
  };

  const columns: ColumnsType<Credential> = [
    {
      title: 'Key',
      dataIndex: 'key',
      key: 'key',
      render: (key) => (
        <Space>
          <KeyOutlined />
          <Text code>{key}</Text>
        </Space>
      ),
    },
    {
      title: 'Description',
      dataIndex: 'description',
      key: 'description',
      render: (desc) => desc || '-',
    },
    {
      title: 'Value',
      key: 'value',
      render: () => <Text type="secondary">••••••••••••••••</Text>,
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
      width: 200,
      render: (_, record) => (
        <Space>
          <Button
            icon={<CheckCircleOutlined />}
            size="small"
            onClick={() => handleValidate(record.key)}
            loading={validatingKey === record.key}
          >
            Validate
          </Button>
          <Popconfirm
            title="Delete this credential?"
            description="This action cannot be undone."
            onConfirm={() => handleDelete(record.key)}
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
          <Title level={2} style={{ margin: 0 }}>API Credentials</Title>
          <Text type="secondary">Manage your AI provider API keys</Text>
        </div>
        <Button
          type="primary"
          icon={<PlusOutlined />}
          onClick={() => setIsModalOpen(true)}
        >
          Add Credential
        </Button>
      </div>

      <Table
        columns={columns}
        dataSource={data?.items}
        rowKey="key"
        loading={isLoading}
        pagination={false}
      />

      <Modal
        title="Add API Credential"
        open={isModalOpen}
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
        >
          <Form.Item
            name="key"
            label="Credential Type"
            rules={[{ required: true, message: 'Please select a credential type' }]}
          >
            <Select
              placeholder="Select credential type"
              options={credentialKeyOptions}
              showSearch
            />
          </Form.Item>

          <Form.Item
            name="value"
            label="API Key"
            rules={[{ required: true, message: 'Please enter the API key' }]}
          >
            <Input.Password placeholder="sk-..." />
          </Form.Item>

          <Form.Item
            name="description"
            label="Description (optional)"
          >
            <Input placeholder="e.g., Production OpenAI key" />
          </Form.Item>

          <Form.Item>
            <Space>
              <Button
                type="primary"
                htmlType="submit"
                loading={createCredential.isPending}
              >
                Add Credential
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
    </div>
  );
}
