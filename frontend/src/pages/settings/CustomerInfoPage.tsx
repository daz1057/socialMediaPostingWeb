import { useState, useCallback } from 'react';
import {
  Typography,
  Collapse,
  Button,
  Tag,
  Space,
  Input,
  Empty,
  Spin,
  message,
  Popconfirm,
  Card,
} from 'antd';
import {
  PlusOutlined,
  DeleteOutlined,
  SaveOutlined,
  ReloadOutlined,
} from '@ant-design/icons';
import { useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import {
  useCustomerInfoList,
  useInitializeCustomerInfo,
} from '@/hooks';
import type {
  CustomerCategory,
  CustomerInfo,
  PromptResponsePair,
  InjectionType,
} from '@/types';
import {
  CUSTOMER_CATEGORIES,
  getInjectionType,
} from '@/types';

const { Title, Text } = Typography;
const { Panel } = Collapse;
const { TextArea } = Input;

// Injection type tag colors
const INJECTION_TYPE_COLORS: Record<InjectionType, string> = {
  random: 'blue',
  all: 'green',
  ignored: 'default',
};

const INJECTION_TYPE_LABELS: Record<InjectionType, string> = {
  random: 'Random (1 pair)',
  all: 'All pairs',
  ignored: 'Ignored',
};

interface CategoryEditorProps {
  category: CustomerCategory;
  customerInfo?: CustomerInfo;
  onSave: (details: PromptResponsePair[]) => Promise<void>;
  isSaving: boolean;
}

function CategoryEditor({ category, customerInfo, onSave, isSaving }: CategoryEditorProps) {
  const [pairs, setPairs] = useState<PromptResponsePair[]>(
    customerInfo?.details || []
  );
  const [hasChanges, setHasChanges] = useState(false);

  const injectionType = getInjectionType(category);

  const handleAddPair = () => {
    setPairs([...pairs, { prompt: '', response: '' }]);
    setHasChanges(true);
  };

  const handleRemovePair = (index: number) => {
    const newPairs = pairs.filter((_, i) => i !== index);
    setPairs(newPairs);
    setHasChanges(true);
  };

  const handleUpdatePair = (index: number, field: 'prompt' | 'response', value: string) => {
    const newPairs = [...pairs];
    newPairs[index] = { ...newPairs[index], [field]: value };
    setPairs(newPairs);
    setHasChanges(true);
  };

  const handleSave = async () => {
    // Filter out empty pairs
    const validPairs = pairs.filter(p => p.prompt.trim() || p.response.trim());
    await onSave(validPairs);
    setPairs(validPairs);
    setHasChanges(false);
  };

  const handleReset = () => {
    setPairs(customerInfo?.details || []);
    setHasChanges(false);
  };

  return (
    <div>
      <Space className="tw-mb-4" align="center">
        <Tag color={INJECTION_TYPE_COLORS[injectionType]}>
          {INJECTION_TYPE_LABELS[injectionType]}
        </Tag>
        <Text type="secondary">
          {pairs.length} pair{pairs.length !== 1 ? 's' : ''}
        </Text>
      </Space>

      {pairs.length === 0 ? (
        <Empty
          description="No prompt-response pairs"
          image={Empty.PRESENTED_IMAGE_SIMPLE}
        >
          <Button type="dashed" icon={<PlusOutlined />} onClick={handleAddPair}>
            Add First Pair
          </Button>
        </Empty>
      ) : (
        <div className="tw-space-y-4">
          {pairs.map((pair, index) => (
            <Card
              key={index}
              size="small"
              extra={
                <Popconfirm
                  title="Delete this pair?"
                  onConfirm={() => handleRemovePair(index)}
                  okText="Delete"
                  cancelText="Cancel"
                >
                  <Button
                    type="text"
                    danger
                    icon={<DeleteOutlined />}
                    size="small"
                  />
                </Popconfirm>
              }
            >
              <div className="tw-space-y-2">
                <div>
                  <Text strong>Prompt:</Text>
                  <TextArea
                    value={pair.prompt}
                    onChange={(e) => handleUpdatePair(index, 'prompt', e.target.value)}
                    placeholder="Enter the question/prompt..."
                    autoSize={{ minRows: 1, maxRows: 3 }}
                    className="tw-mt-1"
                  />
                </div>
                <div>
                  <Text strong>Response:</Text>
                  <TextArea
                    value={pair.response}
                    onChange={(e) => handleUpdatePair(index, 'response', e.target.value)}
                    placeholder="Enter the answer/response..."
                    autoSize={{ minRows: 2, maxRows: 6 }}
                    className="tw-mt-1"
                  />
                </div>
              </div>
            </Card>
          ))}
        </div>
      )}

      <Space className="tw-mt-4">
        <Button
          type="dashed"
          icon={<PlusOutlined />}
          onClick={handleAddPair}
        >
          Add Pair
        </Button>
        {hasChanges && (
          <>
            <Button
              type="primary"
              icon={<SaveOutlined />}
              onClick={handleSave}
              loading={isSaving}
            >
              Save
            </Button>
            <Button
              icon={<ReloadOutlined />}
              onClick={handleReset}
            >
              Reset
            </Button>
          </>
        )}
      </Space>
    </div>
  );
}

export function CustomerInfoPage() {
  const queryClient = useQueryClient();
  const { data: customerInfoList, isLoading } = useCustomerInfoList();
  const initializeMutation = useInitializeCustomerInfo();
  const [savingCategory, setSavingCategory] = useState<CustomerCategory | null>(null);

  // Create a map of category -> customer info
  const categoryMap = new Map<CustomerCategory, CustomerInfo>();
  customerInfoList?.customer_info.forEach((info) => {
    categoryMap.set(info.category, info);
  });

  const updateMutation = useMutation({
    mutationFn: async ({ category, details }: { category: CustomerCategory; details: PromptResponsePair[] }) => {
      const response = await apiClient.put(`/customer-info/${encodeURIComponent(category)}`, { details });
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['customerInfo'] });
    },
  });

  const handleInitialize = async () => {
    try {
      await initializeMutation.mutateAsync();
      message.success('Categories initialized successfully');
    } catch {
      message.error('Failed to initialize categories');
    }
  };

  const handleSaveCategory = useCallback(async (category: CustomerCategory, details: PromptResponsePair[]) => {
    setSavingCategory(category);
    try {
      await updateMutation.mutateAsync({ category, details });
      message.success(`${category} saved successfully`);
    } catch {
      message.error(`Failed to save ${category}`);
    } finally {
      setSavingCategory(null);
    }
  }, [updateMutation]);

  if (isLoading) {
    return (
      <div className="tw-flex tw-justify-center tw-items-center tw-h-64">
        <Spin size="large" />
      </div>
    );
  }

  const hasNoCategories = !customerInfoList || customerInfoList.customer_info.length === 0;

  return (
    <div>
      <div className="tw-flex tw-justify-between tw-items-center tw-mb-6">
        <div>
          <Title level={2}>Customer Info</Title>
          <Text type="secondary">
            Configure customer personas and marketing information for AI-powered content generation
          </Text>
        </div>
        {hasNoCategories && (
          <Button
            type="primary"
            onClick={handleInitialize}
            loading={initializeMutation.isPending}
          >
            Initialize Categories
          </Button>
        )}
      </div>

      {hasNoCategories ? (
        <Card>
          <Empty
            description={
              <span>
                No customer info categories found.
                <br />
                Click "Initialize Categories" to create all 11 predefined categories.
              </span>
            }
          />
        </Card>
      ) : (
        <Collapse accordion>
          {CUSTOMER_CATEGORIES.map((category) => {
            const info = categoryMap.get(category);
            const injectionType = getInjectionType(category);
            const pairCount = info?.details?.length || 0;

            return (
              <Panel
                key={category}
                header={
                  <Space>
                    <span>{category}</span>
                    <Tag color={INJECTION_TYPE_COLORS[injectionType]} style={{ marginLeft: 8 }}>
                      {INJECTION_TYPE_LABELS[injectionType]}
                    </Tag>
                    {pairCount > 0 && (
                      <Tag>{pairCount} pair{pairCount !== 1 ? 's' : ''}</Tag>
                    )}
                  </Space>
                }
              >
                <CategoryEditor
                  category={category}
                  customerInfo={info}
                  onSave={(details) => handleSaveCategory(category, details)}
                  isSaving={savingCategory === category}
                />
              </Panel>
            );
          })}
        </Collapse>
      )}
    </div>
  );
}
