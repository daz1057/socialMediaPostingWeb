import { Outlet, useNavigate } from 'react-router-dom';
import { Layout as AntLayout, Button, Dropdown, Typography, Space, Avatar } from 'antd';
import type { MenuProps } from 'antd';
import { UserOutlined, LogoutOutlined } from '@ant-design/icons';
import { Sidebar } from './Sidebar';
import { useAuthStore } from '@/store/authStore';
import { useLogout } from '@/hooks/useAuth';

const { Header, Sider, Content } = AntLayout;
const { Text } = Typography;

export function Layout() {
  const navigate = useNavigate();
  const { user } = useAuthStore();
  const logout = useLogout();

  const handleLogout = async () => {
    await logout.mutateAsync();
    navigate('/login');
  };

  const userMenuItems: MenuProps['items'] = [
    {
      key: 'user',
      label: (
        <Space direction="vertical" size={0}>
          <Text strong>{user?.username}</Text>
          <Text type="secondary" style={{ fontSize: 12 }}>{user?.email}</Text>
        </Space>
      ),
      disabled: true,
    },
    {
      type: 'divider',
    },
    {
      key: 'logout',
      icon: <LogoutOutlined />,
      label: 'Logout',
      onClick: handleLogout,
    },
  ];

  return (
    <AntLayout style={{ minHeight: '100vh' }}>
      <Header
        style={{
          display: 'flex',
          alignItems: 'center',
          justifyContent: 'space-between',
          background: '#001529',
          padding: '0 24px',
        }}
      >
        <div
          style={{
            color: 'white',
            fontSize: 20,
            fontWeight: 'bold',
            cursor: 'pointer',
          }}
          onClick={() => navigate('/')}
        >
          Social Media Poster
        </div>

        <Dropdown menu={{ items: userMenuItems }} placement="bottomRight">
          <Button type="text" style={{ color: 'white' }}>
            <Space>
              <Avatar size="small" icon={<UserOutlined />} />
              {user?.username}
            </Space>
          </Button>
        </Dropdown>
      </Header>

      <AntLayout>
        <Sider
          width={220}
          style={{
            background: '#fff',
            overflow: 'auto',
            height: 'calc(100vh - 64px)',
          }}
        >
          <Sidebar />
        </Sider>

        <AntLayout style={{ padding: '24px' }}>
          <Content
            style={{
              padding: 24,
              margin: 0,
              minHeight: 280,
              background: '#fff',
              borderRadius: 8,
            }}
          >
            <Outlet />
          </Content>
        </AntLayout>
      </AntLayout>
    </AntLayout>
  );
}
