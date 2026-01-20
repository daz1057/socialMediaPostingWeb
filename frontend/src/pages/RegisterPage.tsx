import { useState } from 'react';
import { Link, useNavigate } from 'react-router-dom';
import { Form, Input, Button, Card, Typography, Alert, Space } from 'antd';
import { UserOutlined, LockOutlined, MailOutlined } from '@ant-design/icons';
import { useRegister, useLogin } from '@/hooks/useAuth';
import type { UserCreate } from '@/types';

const { Title, Text } = Typography;

export function RegisterPage() {
  const navigate = useNavigate();
  const [form] = Form.useForm();
  const register = useRegister();
  const login = useLogin();
  const [error, setError] = useState<string | null>(null);

  const onFinish = async (values: UserCreate & { confirmPassword: string }) => {
    setError(null);
    try {
      // Register user
      await register.mutateAsync({
        username: values.username,
        email: values.email,
        password: values.password,
      });

      // Auto-login after registration
      await login.mutateAsync({
        username: values.username,
        password: values.password,
      });

      navigate('/', { replace: true });
    } catch (err) {
      const message = err instanceof Error ? err.message : 'Registration failed. Please try again.';
      setError(message);
    }
  };

  return (
    <div className="tw-min-h-screen tw-flex tw-items-center tw-justify-center tw-bg-gray-50 tw-py-12 tw-px-4">
      <Card className="tw-w-full tw-max-w-md">
        <Space direction="vertical" size="large" className="tw-w-full">
          <div className="tw-text-center">
            <Title level={2}>Create Account</Title>
            <Text type="secondary">Sign up to get started.</Text>
          </div>

          {error && (
            <Alert
              message="Registration Error"
              description={error}
              type="error"
              showIcon
              closable
              onClose={() => setError(null)}
            />
          )}

          <Form
            form={form}
            name="register"
            onFinish={onFinish}
            layout="vertical"
            size="large"
          >
            <Form.Item
              name="username"
              rules={[
                { required: true, message: 'Please enter a username' },
                { min: 3, message: 'Username must be at least 3 characters' },
              ]}
            >
              <Input
                prefix={<UserOutlined />}
                placeholder="Username"
                autoComplete="username"
              />
            </Form.Item>

            <Form.Item
              name="email"
              rules={[
                { required: true, message: 'Please enter your email' },
                { type: 'email', message: 'Please enter a valid email' },
              ]}
            >
              <Input
                prefix={<MailOutlined />}
                placeholder="Email"
                autoComplete="email"
              />
            </Form.Item>

            <Form.Item
              name="password"
              rules={[
                { required: true, message: 'Please enter a password' },
                { min: 8, message: 'Password must be at least 8 characters' },
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Password"
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item
              name="confirmPassword"
              dependencies={['password']}
              rules={[
                { required: true, message: 'Please confirm your password' },
                ({ getFieldValue }) => ({
                  validator(_, value) {
                    if (!value || getFieldValue('password') === value) {
                      return Promise.resolve();
                    }
                    return Promise.reject(new Error('Passwords do not match'));
                  },
                }),
              ]}
            >
              <Input.Password
                prefix={<LockOutlined />}
                placeholder="Confirm Password"
                autoComplete="new-password"
              />
            </Form.Item>

            <Form.Item>
              <Button
                type="primary"
                htmlType="submit"
                loading={register.isPending || login.isPending}
                block
              >
                Create Account
              </Button>
            </Form.Item>
          </Form>

          <div className="tw-text-center">
            <Text type="secondary">
              Already have an account?{' '}
              <Link to="/login">Sign in</Link>
            </Text>
          </div>
        </Space>
      </Card>
    </div>
  );
}
