import { useState } from 'react';
import {
  Form,
  Select,
  Input,
  Button,
  Card,
  Typography,
  Space,
  Alert,
  Spin,
  Upload,
  message,
  Divider,
  Tag,
} from 'antd';
import type { UploadFile, UploadProps } from 'antd';
import {
  InboxOutlined,
  CopyOutlined,
  FileTextOutlined,
  LinkOutlined,
} from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useModelConfigs } from '@/hooks/useModels';
import { useProcessImage, useOCRProviders } from '@/hooks/useOCR';
import type { OCRProcessResponse, ModelConfig } from '@/types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;
const { Dragger } = Upload;

export function OCRPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [result, setResult] = useState<OCRProcessResponse | null>(null);
  const [selectedModel, setSelectedModel] = useState<ModelConfig | null>(null);
  const [fileList, setFileList] = useState<UploadFile[]>([]);

  const { data: modelsData, isLoading: modelsLoading } = useModelConfigs({
    modelType: 'vision',
    enabledOnly: true,
  });

  const { data: providersData } = useOCRProviders();

  const processImage = useProcessImage();

  const onModelChange = (modelId: number) => {
    const model = modelsData?.items.find((m) => m.id === modelId);
    setSelectedModel(model || null);
  };

  const onProcess = async (values: { model_config_id: number; custom_prompt?: string; template_name?: string; template_tags?: string }) => {
    if (fileList.length === 0 || !fileList[0].originFileObj) {
      message.error('Please select an image file');
      return;
    }

    try {
      const tags = values.template_tags
        ? values.template_tags.split(',').map((t) => t.trim()).filter((t) => t)
        : undefined;

      const response = await processImage.mutateAsync({
        file: fileList[0].originFileObj,
        model_config_id: values.model_config_id,
        custom_prompt: values.custom_prompt || undefined,
        template_name: values.template_name || undefined,
        template_tags: tags,
      });

      setResult(response);

      if (response.success) {
        message.success('Text extracted successfully!');
      } else {
        message.error(response.error || 'OCR processing failed');
      }
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'OCR processing failed';
      message.error(msg);
    }
  };

  const handleCopyText = () => {
    if (result?.extracted_text) {
      navigator.clipboard.writeText(result.extracted_text);
      message.success('Text copied to clipboard');
    }
  };

  const uploadProps: UploadProps = {
    name: 'file',
    multiple: false,
    fileList,
    beforeUpload: (file) => {
      const isImage = file.type.startsWith('image/');
      if (!isImage) {
        message.error('You can only upload image files!');
        return Upload.LIST_IGNORE;
      }
      const isLt20M = file.size / 1024 / 1024 < 20;
      if (!isLt20M) {
        message.error('Image must be smaller than 20MB!');
        return Upload.LIST_IGNORE;
      }
      setFileList([file as UploadFile]);
      return false;
    },
    onRemove: () => {
      setFileList([]);
    },
  };

  const getProviderInfo = (providerName: string) => {
    return providersData?.providers.find((p) => p.name === providerName);
  };

  return (
    <div>
      <Title level={2}>OCR - Text Extraction</Title>
      <Text type="secondary">
        Extract text from images using vision AI models. The extracted text will be saved as an OCR template.
      </Text>

      <div className="tw-grid tw-grid-cols-1 lg:tw-grid-cols-2 tw-gap-6 tw-mt-6">
        <Card title="Upload & Settings">
          <Form
            form={form}
            layout="vertical"
            onFinish={onProcess}
            initialValues={{
              template_tags: 'ocr, extracted',
            }}
          >
            <Form.Item
              label="Image"
              required
            >
              <Dragger {...uploadProps}>
                <p className="ant-upload-drag-icon">
                  <InboxOutlined />
                </p>
                <p className="ant-upload-text">Click or drag image to upload</p>
                <p className="ant-upload-hint">
                  Supports PNG, JPG, GIF, WEBP. Max 20MB.
                </p>
              </Dragger>
            </Form.Item>

            <Form.Item
              name="model_config_id"
              label="Vision Model"
              rules={[{ required: true, message: 'Please select a vision model' }]}
              extra={
                selectedModel && getProviderInfo(selectedModel.provider)?.is_local
                  ? <Tag color="green">Local - No API key required</Tag>
                  : null
              }
            >
              <Select
                placeholder="Select a vision model"
                loading={modelsLoading}
                onChange={onModelChange}
                options={modelsData?.items.map((m) => ({
                  value: m.id,
                  label: m.display_name || `${m.provider} / ${m.model_id}`,
                }))}
              />
            </Form.Item>

            <Form.Item
              name="custom_prompt"
              label="Custom Prompt (Optional)"
              extra="Leave empty to use default text extraction prompt"
            >
              <TextArea
                rows={3}
                placeholder="Extract all text from this image..."
              />
            </Form.Item>

            <Divider>Template Settings</Divider>

            <Form.Item
              name="template_name"
              label="Template Name (Optional)"
              extra="Will auto-generate from filename if not provided"
            >
              <Input placeholder="My OCR Template" />
            </Form.Item>

            <Form.Item
              name="template_tags"
              label="Tags (Optional)"
              extra="Comma-separated tags for organizing templates"
            >
              <Input placeholder="ocr, extracted, document" />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={processImage.isPending}
                block
                disabled={!selectedModel || fileList.length === 0}
              >
                Extract Text
              </Button>
            </Form.Item>
          </Form>

          {modelsData?.items.length === 0 && (
            <Alert
              type="warning"
              message="Setup Required"
              description={
                <p>
                  No vision models configured.{' '}
                  <a onClick={() => navigate('/settings/models')}>Configure models</a>
                </p>
              }
            />
          )}
        </Card>

        <Card title="Extracted Text">
          {processImage.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-96">
              <Spin size="large" tip="Extracting text..." />
            </div>
          )}

          {result && !processImage.isPending && (
            <div>
              {result.success ? (
                <>
                  <div className="tw-mb-4">
                    <Space>
                      <Button
                        icon={<CopyOutlined />}
                        onClick={handleCopyText}
                      >
                        Copy Text
                      </Button>
                      {result.template_id && (
                        <Button
                          icon={<LinkOutlined />}
                          onClick={() => navigate(`/templates/${result.template_id}`)}
                        >
                          View Template
                        </Button>
                      )}
                    </Space>
                  </div>

                  <div
                    style={{
                      background: '#f5f5f5',
                      padding: 16,
                      borderRadius: 8,
                      maxHeight: 400,
                      overflow: 'auto',
                    }}
                  >
                    <Paragraph
                      style={{
                        whiteSpace: 'pre-wrap',
                        margin: 0,
                        fontFamily: 'monospace',
                      }}
                    >
                      {result.extracted_text}
                    </Paragraph>
                  </div>

                  <Divider />

                  <Space direction="vertical" size="small">
                    {result.template_name && (
                      <Text type="secondary">
                        Template: {result.template_name}
                      </Text>
                    )}
                    <Text type="secondary">
                      Model: {result.provider} / {result.model_used}
                    </Text>
                    {result.usage && (
                      <Text type="secondary">
                        Tokens: {result.usage.total_tokens}
                      </Text>
                    )}
                  </Space>
                </>
              ) : (
                <Alert
                  type="error"
                  message="Extraction Failed"
                  description={result.error || 'Unknown error occurred'}
                />
              )}
            </div>
          )}

          {!result && !processImage.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-96 tw-text-gray-400">
              <div className="tw-text-center">
                <FileTextOutlined style={{ fontSize: 48 }} />
                <p className="tw-mt-4">Extracted text will appear here</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
