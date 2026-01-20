import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Template, TemplateCreate, TemplateUpdate, TemplateList, TemplateCategory } from '@/types';

interface UseTemplatesParams {
  skip?: number;
  limit?: number;
  category?: TemplateCategory;
  tag?: string;
  search?: string;
}

export function useTemplates(params: UseTemplatesParams = {}) {
  const { skip = 0, limit = 100, category, tag, search } = params;

  return useQuery({
    queryKey: ['templates', { skip, limit, category, tag, search }],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', limit.toString());
      if (category) queryParams.append('category', category);
      if (tag) queryParams.append('tag', tag);
      if (search) queryParams.append('search', search);

      const response = await apiClient.get<TemplateList>(`/templates?${queryParams}`);
      return response.data;
    },
  });
}

export function useTemplate(id: number) {
  return useQuery({
    queryKey: ['template', id],
    queryFn: async () => {
      const response = await apiClient.get<Template>(`/templates/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useTemplateTags() {
  return useQuery({
    queryKey: ['template-tags'],
    queryFn: async () => {
      const response = await apiClient.get<string[]>('/templates/tags');
      return response.data;
    },
  });
}

export function useCreateTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TemplateCreate) => {
      const response = await apiClient.post<Template>('/templates', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template-tags'] });
    },
  });
}

export function useUpdateTemplate(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: TemplateUpdate) => {
      const response = await apiClient.put<Template>(`/templates/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template', id] });
      queryClient.invalidateQueries({ queryKey: ['template-tags'] });
    },
  });
}

export function useDeleteTemplate() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/templates/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['templates'] });
      queryClient.invalidateQueries({ queryKey: ['template-tags'] });
    },
  });
}
