/**
 * TypeScript type definitions for the application.
 */

// API Response wrapper
export interface ApiResponse<T> {
  data?: T;
  error?: string;
  success: boolean;
}

// Pagination
export interface PaginatedResponse<T> {
  items: T[];
  total: number;
  skip: number;
  limit: number;
}

// ============ User Types ============
export interface User {
  id: number;
  username: string;
  email: string;
  is_active: boolean;
  created_at: string;
  updated_at?: string;
}

export interface UserCreate {
  username: string;
  email: string;
  password: string;
}

// ============ Auth Types ============
export interface LoginRequest {
  username: string;
  password: string;
}

export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
}

// ============ Tag Types ============
export interface Tag {
  id: number;
  name: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface TagCreate {
  name: string;
}

export interface TagUpdate {
  name?: string;
}

// ============ Customer Info Types ============
export interface CustomerInfo {
  id: number;
  name: string;
  industry?: string;
  target_audience?: string;
  brand_voice?: string;
  key_products?: string;
  unique_selling_points?: string;
  additional_context?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CustomerInfoCreate {
  name: string;
  industry?: string;
  target_audience?: string;
  brand_voice?: string;
  key_products?: string;
  unique_selling_points?: string;
  additional_context?: string;
}

export interface CustomerInfoUpdate {
  name?: string;
  industry?: string;
  target_audience?: string;
  brand_voice?: string;
  key_products?: string;
  unique_selling_points?: string;
  additional_context?: string;
}

// ============ Prompt Types ============
export interface Prompt {
  id: number;
  name: string;
  details: string;
  selected_customers: Record<string, boolean>;
  url?: string;
  media_file_path?: string;
  aws_folder_url?: string;
  artwork_description?: string;
  example_image?: string;
  tag_id?: number;
  tag?: Tag;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PromptCreate {
  name: string;
  details: string;
  selected_customers?: Record<string, boolean>;
  url?: string;
  media_file_path?: string;
  aws_folder_url?: string;
  artwork_description?: string;
  example_image?: string;
  tag_id?: number;
}

export interface PromptUpdate {
  name?: string;
  details?: string;
  selected_customers?: Record<string, boolean>;
  url?: string;
  media_file_path?: string;
  aws_folder_url?: string;
  artwork_description?: string;
  example_image?: string;
  tag_id?: number;
}

export interface PromptList {
  prompts: Prompt[];
  total: number;
  skip: number;
  limit: number;
}

// ============ Credential Types ============
export interface Credential {
  id: number;
  key: string;
  description?: string;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface CredentialCreate {
  key: string;
  value: string;
  description?: string;
}

export interface CredentialUpdate {
  value?: string;
  description?: string;
}

export interface CredentialList {
  items: Credential[];
  total: number;
  skip: number;
  limit: number;
}

export interface CredentialValidateRequest {
  key: string;
}

export interface CredentialValidateResponse {
  key: string;
  is_valid: boolean;
  message: string;
}

// ============ Model Config Types ============
export type ModelType = 'text' | 'image';

export interface ModelConfig {
  id: number;
  provider: string;
  model_id: string;
  model_type: ModelType;
  display_name?: string;
  is_enabled: boolean;
  is_default: boolean;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface ModelConfigCreate {
  provider: string;
  model_id: string;
  model_type: ModelType;
  display_name?: string;
  is_enabled?: boolean;
  is_default?: boolean;
}

export interface ModelConfigUpdate {
  display_name?: string;
  is_enabled?: boolean;
  is_default?: boolean;
}

export interface ModelConfigList {
  items: ModelConfig[];
  total: number;
  skip: number;
  limit: number;
}

export interface ModelInfo {
  model_id: string;
  display_name: string;
  model_type: ModelType;
}

export interface ProviderInfo {
  provider_name: string;
  display_name: string;
  models: ModelInfo[];
  credential_keys: string[];
}

export interface ProvidersListResponse {
  providers: ProviderInfo[];
}

// ============ Post Types ============
export type PostStatus = 'draft' | 'scheduled' | 'published';

// Common graphic types
export const GRAPHIC_TYPES = [
  'Infographic',
  'Short Video',
  'Illustration',
  'Photo',
  'Carousel',
  'Quote',
  'Meme',
  'Story',
  'Reel',
  'Other',
] as const;

export type GraphicType = typeof GRAPHIC_TYPES[number];

export interface Post {
  id: number;
  content: string;
  caption?: string;
  alt_text?: string;
  status: PostStatus;
  graphic_type?: string;
  source_url?: string;
  original_prompt_name?: string;
  keep: boolean;
  for_deletion: boolean;
  scheduled_at?: string;
  published_at?: string;
  media_urls: string[];
  prompt_id?: number;
  user_id: number;
  created_at: string;
  updated_at?: string;
}

export interface PostCreate {
  content: string;
  caption?: string;
  alt_text?: string;
  status?: PostStatus;
  graphic_type?: string;
  source_url?: string;
  original_prompt_name?: string;
  keep?: boolean;
  for_deletion?: boolean;
  scheduled_at?: string;
  media_urls?: string[];
  prompt_id?: number;
}

export interface PostUpdate {
  content?: string;
  caption?: string;
  alt_text?: string;
  status?: PostStatus;
  graphic_type?: string;
  source_url?: string;
  original_prompt_name?: string;
  keep?: boolean;
  for_deletion?: boolean;
  scheduled_at?: string;
  media_urls?: string[];
  prompt_id?: number;
}

export interface PostList {
  items: Post[];
  total: number;
  skip: number;
  limit: number;
}

export interface MediaUploadResponse {
  url: string;
  filename: string;
  content_type: string;
  size: number;
}

export interface CSVExportRequest {
  status?: PostStatus;
  date_from?: string;
  date_to?: string;
}

// ============ Text Generation Types ============
export interface TextGenerationRequest {
  prompt_id: number;
  model_config_id: number;
  temperature?: number;
  max_tokens?: number;
}

export interface TextGenerationResponse {
  content: string;
  model_used: string;
  provider: string;
  prompt_id: number;
  usage?: {
    prompt_tokens?: number;
    completion_tokens?: number;
    total_tokens?: number;
  };
  success: boolean;
  error?: string;
  request_id: string;
}

// ============ Image Generation Types ============
export interface ImageGenerationRequest {
  prompt: string;
  model_config_id: number;
  size?: string;
  quality?: string;
  style?: string;
  n?: number;
  width?: number;
  height?: number;
  steps?: number;
  guidance?: number;
  reference_image_url?: string;
  reference_image_strength?: number;
}

export interface ImageData {
  base64_data: string;
  format: string;
  revised_prompt?: string;
}

export interface ImageGenerationResponse {
  images: ImageData[];
  model_used: string;
  provider: string;
  request_id: string;
  raw_response?: Record<string, unknown>;
}

export interface ImageGenerationError {
  error: string;
  model_used: string;
  provider: string;
  request_id: string;
}

export interface ReferenceImageUploadResponse {
  s3_url: string;
  s3_key: string;
  filename: string;
  content_type: string;
}

// ============ Template Types ============
export type TemplateCategory = 'ocr' | 'manual' | 'custom';

export const TEMPLATE_CATEGORIES: { value: TemplateCategory; label: string }[] = [
  { value: 'ocr', label: 'OCR' },
  { value: 'manual', label: 'Manual' },
  { value: 'custom', label: 'Custom' },
];

export interface Template {
  id: number;
  name: string;
  category: TemplateCategory;
  tags: string[];
  content: string;
  user_id: number;
  created_at: string;
  updated_at: string;
}

export interface TemplateCreate {
  name: string;
  category?: TemplateCategory;
  tags?: string[];
  content: string;
}

export interface TemplateUpdate {
  name?: string;
  category?: TemplateCategory;
  tags?: string[];
  content?: string;
}

export interface TemplateList {
  templates: Template[];
  total: number;
  skip: number;
  limit: number;
}
