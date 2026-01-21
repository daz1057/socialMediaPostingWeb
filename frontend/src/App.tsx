import { Routes, Route, Navigate } from 'react-router-dom';
import { ConfigProvider } from 'antd';

// Components
import { Layout } from './components/Layout';
import { ProtectedRoute } from './components/ProtectedRoute';

// Auth Pages
import { LoginPage } from './pages/LoginPage';
import { RegisterPage } from './pages/RegisterPage';

// Main Pages
import { DashboardPage } from './pages/DashboardPage';
import { TextGenerationPage } from './pages/TextGenerationPage';
import { ImageGenerationPage } from './pages/ImageGenerationPage';

// Prompt Pages
import {
  PromptsListPage,
  PromptCreatePage,
  PromptEditPage,
  PromptDetailPage,
} from './pages/prompts';

// Post Pages
import {
  PostsListPage,
  PostCreatePage,
  PostEditPage,
  PostDetailPage,
} from './pages/posts';

// Template Pages
import {
  TemplatesListPage,
  TemplateCreatePage,
  TemplateEditPage,
  TemplateDetailPage,
} from './pages/templates';

// OCR Pages
import { OCRPage } from './pages/ocr';

// Settings Pages
import { CredentialsPage, ModelsPage } from './pages/settings';

function App() {
  return (
    <ConfigProvider
      theme={{
        token: {
          colorPrimary: '#1890ff',
        },
      }}
    >
      <Routes>
        {/* Public routes */}
        <Route path="/login" element={<LoginPage />} />
        <Route path="/register" element={<RegisterPage />} />

        {/* Protected routes with layout */}
        <Route
          element={
            <ProtectedRoute>
              <Layout />
            </ProtectedRoute>
          }
        >
          {/* Dashboard */}
          <Route path="/" element={<DashboardPage />} />

          {/* Prompts */}
          <Route path="/prompts" element={<PromptsListPage />} />
          <Route path="/prompts/new" element={<PromptCreatePage />} />
          <Route path="/prompts/:id" element={<PromptDetailPage />} />
          <Route path="/prompts/:id/edit" element={<PromptEditPage />} />

          {/* Generation */}
          <Route path="/generate/text" element={<TextGenerationPage />} />
          <Route path="/generate/image" element={<ImageGenerationPage />} />

          {/* OCR */}
          <Route path="/ocr" element={<OCRPage />} />

          {/* Posts */}
          <Route path="/posts" element={<PostsListPage />} />
          <Route path="/posts/new" element={<PostCreatePage />} />
          <Route path="/posts/:id" element={<PostDetailPage />} />
          <Route path="/posts/:id/edit" element={<PostEditPage />} />

          {/* Templates */}
          <Route path="/templates" element={<TemplatesListPage />} />
          <Route path="/templates/new" element={<TemplateCreatePage />} />
          <Route path="/templates/:id" element={<TemplateDetailPage />} />
          <Route path="/templates/:id/edit" element={<TemplateEditPage />} />

          {/* Settings */}
          <Route path="/settings/credentials" element={<CredentialsPage />} />
          <Route path="/settings/models" element={<ModelsPage />} />
        </Route>

        {/* Catch all - redirect to dashboard */}
        <Route path="*" element={<Navigate to="/" replace />} />
      </Routes>
    </ConfigProvider>
  );
}

export default App;
