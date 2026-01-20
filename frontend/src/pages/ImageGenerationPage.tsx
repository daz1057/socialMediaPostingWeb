import { useState } from 'react';
import {
  Form,
  Select,
  Input,
  InputNumber,
  Button,
  Card,
  Typography,
  Space,
  Alert,
  Spin,
  Image,
  message,
  Divider,
  Slider,
} from 'antd';
import { DownloadOutlined, PictureOutlined } from '@ant-design/icons';
import { useNavigate } from 'react-router-dom';
import { useModelConfigs } from '@/hooks/useModels';
import { useGenerateImage } from '@/hooks/useGenerate';
import type { ImageGenerationRequest, ImageGenerationResponse, ModelConfig } from '@/types';

const { Title, Text, Paragraph } = Typography;
const { TextArea } = Input;

export function ImageGenerationPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const [result, setResult] = useState<ImageGenerationResponse | null>(null);
  const [selectedModel, setSelectedModel] = useState<ModelConfig | null>(null);

  const { data: modelsData, isLoading: modelsLoading } = useModelConfigs({
    modelType: 'image',
    enabledOnly: true,
  });

  const generateImage = useGenerateImage();

  const onModelChange = (modelId: number) => {
    const model = modelsData?.items.find((m) => m.id === modelId);
    setSelectedModel(model || null);
  };

  const onGenerate = async (values: ImageGenerationRequest) => {
    try {
      const response = await generateImage.mutateAsync(values);
      setResult(response);
    } catch (err) {
      const msg = err instanceof Error ? err.message : 'Generation failed';
      message.error(msg);
    }
  };

  const handleDownload = (base64Data: string, index: number) => {
    const link = document.createElement('a');
    link.href = `data:image/png;base64,${base64Data}`;
    link.download = `generated_image_${index + 1}.png`;
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const isDallE = selectedModel?.provider === 'openai_dalle';
  const isFlux = selectedModel?.provider === 'bfl_flux';

  return (
    <div>
      <Title level={2}>Image Generation</Title>
      <Text type="secondary">Generate images using DALL-E or Flux.</Text>

      <div className="tw-grid tw-grid-cols-1 lg:tw-grid-cols-2 tw-gap-6 tw-mt-6">
        <Card title="Generation Settings">
          <Form
            form={form}
            layout="vertical"
            onFinish={onGenerate}
            initialValues={{
              size: '1024x1024',
              quality: 'standard',
              style: 'vivid',
              n: 1,
              width: 1024,
              height: 1024,
              steps: 28,
              guidance: 3.5,
            }}
          >
            <Form.Item
              name="prompt"
              label="Image Description"
              rules={[{ required: true, message: 'Please describe the image' }]}
            >
              <TextArea
                rows={4}
                placeholder="A futuristic city at sunset with flying cars..."
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
                onChange={onModelChange}
                options={modelsData?.items.map((m) => ({
                  value: m.id,
                  label: m.display_name || `${m.provider} / ${m.model_id}`,
                }))}
              />
            </Form.Item>

            {isDallE && (
              <>
                <Form.Item name="size" label="Size">
                  <Select
                    options={[
                      { value: '1024x1024', label: '1024x1024 (Square)' },
                      { value: '1792x1024', label: '1792x1024 (Landscape)' },
                      { value: '1024x1792', label: '1024x1792 (Portrait)' },
                    ]}
                  />
                </Form.Item>

                <Form.Item name="quality" label="Quality">
                  <Select
                    options={[
                      { value: 'standard', label: 'Standard' },
                      { value: 'hd', label: 'HD' },
                    ]}
                  />
                </Form.Item>

                <Form.Item name="style" label="Style">
                  <Select
                    options={[
                      { value: 'vivid', label: 'Vivid' },
                      { value: 'natural', label: 'Natural' },
                    ]}
                  />
                </Form.Item>
              </>
            )}

            {isFlux && (
              <>
                <div className="tw-grid tw-grid-cols-2 tw-gap-4">
                  <Form.Item name="width" label="Width">
                    <InputNumber min={256} max={2048} step={64} style={{ width: '100%' }} />
                  </Form.Item>
                  <Form.Item name="height" label="Height">
                    <InputNumber min={256} max={2048} step={64} style={{ width: '100%' }} />
                  </Form.Item>
                </div>

                <Form.Item
                  name="steps"
                  label="Inference Steps"
                  extra="More steps = higher quality but slower"
                >
                  <Slider min={1} max={50} marks={{ 1: '1', 28: '28', 50: '50' }} />
                </Form.Item>

                <Form.Item
                  name="guidance"
                  label="Guidance Scale"
                  extra="Higher = more adherence to prompt"
                >
                  <Slider min={1} max={10} step={0.5} marks={{ 1: '1', 3.5: '3.5', 10: '10' }} />
                </Form.Item>
              </>
            )}

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={generateImage.isPending}
                block
                disabled={!selectedModel}
              >
                Generate Image
              </Button>
            </Form.Item>
          </Form>

          {modelsData?.items.length === 0 && (
            <Alert
              type="warning"
              message="Setup Required"
              description={
                <p>
                  No image models configured.{' '}
                  <a onClick={() => navigate('/settings/models')}>Configure models</a>
                </p>
              }
            />
          )}
        </Card>

        <Card title="Generated Image">
          {generateImage.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-96">
              <Spin size="large" tip="Generating image..." />
            </div>
          )}

          {result && !generateImage.isPending && (
            <div>
              {result.images.map((img, index) => (
                <div key={index} className="tw-mb-4">
                  <Image
                    src={`data:image/${img.format || 'png'};base64,${img.base64_data}`}
                    alt={`Generated image ${index + 1}`}
                    style={{ maxWidth: '100%', borderRadius: 8 }}
                  />
                  <div className="tw-mt-2 tw-flex tw-justify-between tw-items-center">
                    <Button
                      icon={<DownloadOutlined />}
                      onClick={() => handleDownload(img.base64_data, index)}
                    >
                      Download
                    </Button>
                  </div>
                  {img.revised_prompt && (
                    <Paragraph type="secondary" style={{ marginTop: 8 }}>
                      <strong>Revised prompt:</strong> {img.revised_prompt}
                    </Paragraph>
                  )}
                </div>
              ))}

              <Divider />

              <Text type="secondary">
                Model: {result.provider} / {result.model_used}
              </Text>
            </div>
          )}

          {!result && !generateImage.isPending && (
            <div className="tw-flex tw-justify-center tw-items-center tw-h-96 tw-text-gray-400">
              <div className="tw-text-center">
                <PictureOutlined style={{ fontSize: 48 }} />
                <p className="tw-mt-4">Generated image will appear here</p>
              </div>
            </div>
          )}
        </Card>
      </div>
    </div>
  );
}
