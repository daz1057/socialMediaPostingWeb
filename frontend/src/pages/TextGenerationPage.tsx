import { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import {
  Form,
  Select,
  InputNumber,
  Button,
  Card,
  Typography,
  Space,
  Alert,
  Spin,
  Slider,
  message,
  Divider,
} from 'antd';
import { CopyOutlined, PlusOutlined, SendOutlined } from '@ant-design/icons';
import { usePrompts } from '@/hooks/usePrompts';
import { useModelConfigs } from '@/hooks/useModels';
import { useGenerateText } from '@/hooks/useGenerate';
import { useCreatePost } from '@/hooks/usePosts';
import type { TextGenerationRequest, TextGenerationResponse } from '@/types';

const { Title, Paragraph, Text } = Typography;

export function TextGenerationPage() {
  const location = useLocation();
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [result, setResult] = useState<TextGenerationResponse | null>(null);

  // Get initial prompt ID from navigation state
  const initialPromptId = (location.state as { promptId?: number })?.promptId;

  const { data: promptsData, isLoading: promptsLoading } = usePrompts();
  const { data: modelsData, isLoading: modelsLoading } = useModelConfigs({
    modelType: 'text',
    enabledOnly: true,
  });

  const generateText = useGenerateText();
  const createPost = useCreatePost();

  const onGenerate = async (values: TextGenerationRequest) => {
    try {
      const response = await generateText.mutateAsync(values);
      setResult(response);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Generation failed';
      message.error(msg);
    }
  };

  const handleCopyToClipboard = () => {
    if (result?.content) {
      navigator.clipboard.writeText(result.content);
      message.success('Copied to clipboard');
    }
  };

  const handleCreatePost = async () => {
    if (result?.content) {
      try {
        const post = await createPost.mutateAsync({
          content: result.content,
          prompt_id: result.prompt_id,
        });
        message.success('Post created');
        navigate(`/posts/${post.id}`);
      } catch {
        message.error('Failed to create post');
      }
    }
  };

  return (
    <div>
      <Title level={2}>Text Generation</Title>
      <Text type="secondary">Generate content using AI models.</Text>

      <div className="tw-grid tw-grid-cols-1 lg:tw-grid-cols-2 tw-gap-6 tw-mt-6">
        <Card title="Generation Settings">
          <Form
            form={form}
            layout="vertical"
            onFinish={onGenerate}
            initialValues={{
              prompt_id: initialPromptId,
              temperature: 0.7,
              max_tokens: 1024,
            }}
          >
            <Form.Item
              name="prompt_id"
              label="Prompt"
              rules={[{ required: true, message: 'Please select a prompt' }]}
            >
              <Select
                placeholder="Select a prompt"
                loading={promptsLoading}
                showSearch
                optionFilterProp="label"
                options={promptsData?.items.map((p) => ({
                  value: p.id,
                  label: p.name,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="model_config_id"
              label="Model"
              rules={[{ required: true, message: 'Please select a model' }]}
            >
              <Select
                placeholder="Select a model"
                loading={modelsLoading}
                options={modelsData?.items.map((m) => ({
                  value: m.id,
                  label: m.display_name || `${m.provider} / ${m.model_id}`,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="temperature"
              label="Temperature"
              extra="Lower values are more focused, higher values more creative"
            >
              <Slider
                min={0}
                max={2}
                step={0.1}
                marks={{ 0: '0', 0.7: '0.7', 1: '1', 2: '2' }}
              />
            </Form.Item>

            <Form.Item
              name="max_tokens"
              label="Max Tokens"
            >
              <InputNumber min={1} max={4096} style={{ width: '100%' }} />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={generateText.isPending}
                block
              >
                Generate
              </Button>
            </Form.Item>
          </Form>

          {(promptsData?.items.length === 0 || modelsData?.items.length === 0) && (
            <Alert
              type="warning"
              message="Setup Required"
              description={
                <div>
                  {promptsData?.items.length === 0 && (
                    <p>
                      No prompts found.{' '}
                      <a onClick={() => navigate('/prompts/new')}>Create a prompt</a>
                    </p>
                  )}
                  {modelsData?.items.length === 0 && (
                    <p>
                      No text models configured.{' '}
                      <a onClick={() => navigate('/settings/models')}>Configure models</a>
                    </p>
                  )}
                </div>
              }
            />
          )}
        </Card>

        <Card title="Generated Content">
          {generateText.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-64">
              <Spin size="large" tip="Generating..." />
            </div>
          )}

          {result && !generateText.isPending && (
            <div>
              <div className="tw-flex tw-justify-end tw-mb-2">
                <Space>
                  <Button
                    icon={<CopyOutlined />}
                    onClick={handleCopyToClipboard}
                    size="small"
                  >
                    Copy
                  </Button>
                  <Button
                    icon={<PlusOutlined />}
                    onClick={handleCreatePost}
                    loading={createPost.isPending}
                    size="small"
                    type="primary"
                  >
                    Create Post
                  </Button>
                </Space>
              </div>

              <Paragraph>
                <pre style={{
                  whiteSpace: 'pre-wrap',
                  wordWrap: 'break-word',
                  background: '#f5f5f5',
                  padding: 16,
                  borderRadius: 8,
                  margin: 0,
                  maxHeight: 400,
                  overflow: 'auto',
                }}>
                  {result.content}
                </pre>
              </Paragraph>

              <Divider />

              <Text type="secondary">
                Model: {result.provider} / {result.model_used}
                {result.usage && (
                  <> | Tokens: {result.usage.total_tokens}</>
                )}
              </Text>
            </div>
          )}

          {!result && !generateText.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-64 tw-text-gray-400">
              <div className="tw-text-center">
                <SendOutlined style={{ fontSize: 48 }} />
                <p className="tw-mt-4">Generated content will appear here</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
