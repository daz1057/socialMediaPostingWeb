import { useLocation, useNavigate } from 'react-router-dom';
import { Menu } from 'antd';
import type { MenuProps } from 'antd';
import {
  DashboardOutlined,
  FileTextOutlined,
  EditOutlined,
  PictureOutlined,
  SendOutlined,
  KeyOutlined,
  SettingOutlined,
  SnippetsOutlined,
} from '@ant-design/icons';

type MenuItem = Required<MenuProps>['items'][number];

const menuItems: MenuItem[] = [
  {
    key: '/',
    icon: <DashboardOutlined />,
    label: 'Dashboard',
  },
  {
    key: '/prompts',
    icon: <FileTextOutlined />,
    label: 'Prompts',
  },
  {
    key: '/templates',
    icon: <SnippetsOutlined />,
    label: 'Templates',
  },
  {
    type: 'divider',
  },
  {
    key: 'generate',
    icon: <EditOutlined />,
    label: 'Generate',
    children: [
      {
        key: '/generate/text',
        label: 'Text',
      },
      {
        key: '/generate/image',
        label: 'Image',
      },
    ],
  },
  {
    key: '/posts',
    icon: <SendOutlined />,
    label: 'Posts',
  },
  {
    type: 'divider',
  },
  {
    key: 'settings',
    icon: <SettingOutlined />,
    label: 'Settings',
    children: [
      {
        key: '/settings/credentials',
        icon: <KeyOutlined />,
        label: 'API Credentials',
      },
      {
        key: '/settings/models',
        icon: <PictureOutlined />,
        label: 'Model Config',
      },
    ],
  },
];

export function Sidebar() {
  const location = useLocation();
  const navigate = useNavigate();

  const onClick: MenuProps['onClick'] = (e) => {
    navigate(e.key);
  };

  // Determine which keys should be open based on current path
  const getDefaultOpenKeys = () => {
    if (location.pathname.startsWith('/generate')) return ['generate'];
    if (location.pathname.startsWith('/settings')) return ['settings'];
    return [];
  };

  return (
    <Menu
      mode="inline"
      selectedKeys={[location.pathname]}
      defaultOpenKeys={getDefaultOpenKeys()}
      items={menuItems}
      onClick={onClick}
      style={{ height: '100%', borderRight: 0 }}
    />
  );
}
