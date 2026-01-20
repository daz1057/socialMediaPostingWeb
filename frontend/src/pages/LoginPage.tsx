import { useState } from 'react';
import { Link, useNavigate, useLocation } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined } from '@ant-design/icons';
import { useLogin } from '@/hooks/useAuth';
import type { LoginRequest } from '@/types';

const { Title, Text } = Typography;

export function LoginPage() {
  const navigate = useNavigate();
  const location = useLocation();
  const [form] = Form.useForm();
  const login = useLogin();
  const [error, setError] = useState<string | null>(null);

  const from = (location.state as { from?: { pathname: string } })?.from?.pathname || '/';

  const onFinish = async (values: LoginRequest) => {
    setError(null);
    try {
      await login.mutateAsync(values);
      navigate(from, { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Login failed. Please try again.';
      setError(message);
    }
  };

  return (
    <div className="tw-min-h-screen tw-flex tw-items-center tw-justify-center tw-bg-gray-50 tw-py-12 tw-px-4">
      <Card className="tw-w-full tw-max-w-md">
        <Space direction="vertical" size="large" className="tw-w-full">
          <div className="tw-text-center">
            <Title level={2}>Sign In</Title>
            <Text type="secondary">Welcome back! Please sign in to continue.</Text>
          </div>

          {error && (
            <Alert
              message="Login Error"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
            />
          )}

          <Form
            form={form}
            name="login"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[{ required: true, message: 'Please enter your username' }]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[{ required: true, message: 'Please enter your password' }]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                autoComplete="current-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={login.isPending}
                block
              >
                Sign In
              </Button>
            </Form.Item>
          </Form>

          <div className="tw-text-center">
            <Text type="secondary">
              Don't have an account?{' '}
              <Link to="/register">Register now</Link>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
}
