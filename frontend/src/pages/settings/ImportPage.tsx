import { useState } from 'react';
import {
  Typography,
  Card,
  Upload,
  Button,
  Space,
  Alert,
  Divider,
  List,
  Tag,
  message,
  Spin,
} from 'antd';
import {
  UploadOutlined,
  FileTextOutlined,
  CheckCircleOutlined,
  CloseCircleOutlined,
  ImportOutlined,
} from '@ant-design/icons';
import type { UploadFile } from 'antd/es/upload/interface';
import { apiClient } from '@/api/client';

const { Title, Text, Paragraph } = Typography;

interface ImportResult {
  success: boolean;
  tags_imported: number;
  customer_info_imported: number;
  prompts_imported: number;
  errors: string[];
}

export function ImportPage() {
  const [tagsFile, setTagsFile] = useState<UploadFile | null>(null);
  const [customerInfoFile, setCustomerInfoFile] = useState<UploadFile | null>(null);
  const [promptsFile, setPromptsFile] = useState<UploadFile | null>(null);
  const [importing, setImporting] = useState(false);
  const [result, setResult] = useState<ImportResult | null>(null);

  const handleImport = async () => {
    if (!tagsFile && !customerInfoFile && !promptsFile) {
      message.warning('Please select at least one file to import');
      return;
    }

    setImporting(true);
    setResult(null);

    try {
      const formData = new FormData();

      if (tagsFile?.originFileObj) {
        formData.append('tags_file', tagsFile.originFileObj);
      }
      if (customerInfoFile?.originFileObj) {
        formData.append('customer_info_file', customerInfoFile.originFileObj);
      }
      if (promptsFile?.originFileObj) {
        formData.append('prompts_file', promptsFile.originFileObj);
      }

      const response = await apiClient.post('/import/files', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });

      setResult(response.data);

      if (response.data.success) {
        message.success('Import completed successfully');
      } else {
        message.warning('Import completed with some errors');
      }
    } catch (error) {
      message.error('Import failed');
      console.error('Import error:', error);
    } finally {
      setImporting(false);
    }
  };

  const clearFiles = () => {
    setTagsFile(null);
    setCustomerInfoFile(null);
    setPromptsFile(null);
    setResult(null);
  };

  return (
    <div>
      <Title level={2}>Import from Desktop App</Title>
      <Paragraph type="secondary">
        Import your data from the desktop Social Media Posting application.
        Select the JSON files exported from the desktop app.
      </Paragraph>

      <Card style={{ maxWidth: 800 }}>
        <Space direction="vertical" size="large" style={{ width: '100%' }}>
          <div>
            <Text strong>Tags File (tags.json)</Text>
            <Paragraph type="secondary" style={{ marginBottom: 8 }}>
              Optional. Contains tag categories for organizing prompts.
            </Paragraph>
            <Upload
              beforeUpload={() => false}
              maxCount={1}
              accept=".json"
              fileList={tagsFile ? [tagsFile] : []}
              onChange={({ fileList }) => setTagsFile(fileList[0] || null)}
            >
              <Button icon={<UploadOutlined />}>Select tags.json</Button>
            </Upload>
          </div>

          <div>
            <Text strong>Customer Info File (customer_info.json)</Text>
            <Paragraph type="secondary" style={{ marginBottom: 8 }}>
              Contains customer personas, pain points, desires, and other marketing data.
            </Paragraph>
            <Upload
              beforeUpload={() => false}
              maxCount={1}
              accept=".json"
              fileList={customerInfoFile ? [customerInfoFile] : []}
              onChange={({ fileList }) => setCustomerInfoFile(fileList[0] || null)}
            >
              <Button icon={<UploadOutlined />}>Select customer_info.json</Button>
            </Upload>
          </div>

          <div>
            <Text strong>Prompts File (prompts.json)</Text>
            <Paragraph type="secondary" style={{ marginBottom: 8 }}>
              Contains all your prompt templates with their customer info selections.
            </Paragraph>
            <Upload
              beforeUpload={() => false}
              maxCount={1}
              accept=".json"
              fileList={promptsFile ? [promptsFile] : []}
              onChange={({ fileList }) => setPromptsFile(fileList[0] || null)}
            >
              <Button icon={<UploadOutlined />}>Select prompts.json</Button>
            </Upload>
          </div>

          <Divider />

          <Space>
            <Button
              type="primary"
              icon={<ImportOutlined />}
              onClick={handleImport}
              loading={importing}
              disabled={!tagsFile && !customerInfoFile && !promptsFile}
            >
              Import Data
            </Button>
            <Button onClick={clearFiles}>Clear All</Button>
          </Space>
        </Space>
      </Card>

      {importing && (
        <Card style={{ marginTop: 16, textAlign: 'center' }}>
          <Spin size="large" />
          <Paragraph style={{ marginTop: 16 }}>Importing data...</Paragraph>
        </Card>
      )}

      {result && (
        <Card style={{ marginTop: 16 }}>
          <Alert
            type={result.success ? 'success' : 'warning'}
            message={result.success ? 'Import Successful' : 'Import Completed with Errors'}
            description={
              <Space direction="vertical">
                <Text>
                  <Tag color="blue">{result.tags_imported}</Tag> tags imported
                </Text>
                <Text>
                  <Tag color="green">{result.customer_info_imported}</Tag> customer info categories imported
                </Text>
                <Text>
                  <Tag color="purple">{result.prompts_imported}</Tag> prompts imported
                </Text>
              </Space>
            }
            showIcon
            icon={result.success ? <CheckCircleOutlined /> : <CloseCircleOutlined />}
          />

          {result.errors.length > 0 && (
            <div style={{ marginTop: 16 }}>
              <Text strong>Errors ({result.errors.length}):</Text>
              <List
                size="small"
                dataSource={result.errors}
                renderItem={(error) => (
                  <List.Item>
                    <Text type="danger">{error}</Text>
                  </List.Item>
                )}
                style={{ maxHeight: 200, overflow: 'auto' }}
              />
            </div>
          )}
        </Card>
      )}

      <Card style={{ marginTop: 16 }}>
        <Title level={5}>
          <FileTextOutlined /> File Locations
        </Title>
        <Paragraph>
          The JSON files are typically located in your desktop app folder:
        </Paragraph>
        <Paragraph code>
          C:\Users\[YourUsername]\PycharmProjects\SocialMediaPosting-4o-4o-Mini-WithAutomation\
        </Paragraph>
        <List size="small">
          <List.Item>
            <Text code>tags.json</Text> - Tag categories
          </List.Item>
          <List.Item>
            <Text code>customer_info.json</Text> - Customer personas and marketing data
          </List.Item>
          <List.Item>
            <Text code>prompts.json</Text> - Prompt templates
          </List.Item>
        </List>
      </Card>
    </div>
  );
}
