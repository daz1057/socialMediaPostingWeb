import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Prompt, PromptCreate, PromptUpdate, PromptList } from '@/types';

interface UsePromptsParams {
  skip?: number;
  limit?: number;
  tagId?: number;
  search?: string;
}

export function usePrompts(params: UsePromptsParams = {}) {
  const { skip = 0, limit = 100, tagId, search } = params;

  return useQuery({
    queryKey: ['prompts', { skip, limit, tagId, search }],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', limit.toString());
      if (tagId) queryParams.append('tag_id', tagId.toString());
      if (search) queryParams.append('search', search);

      const response = await apiClient.get<PromptList>(`/prompts?${queryParams}`);
      return response.data;
    },
  });
}

export function usePrompt(id: number) {
  return useQuery({
    queryKey: ['prompt', id],
    queryFn: async () => {
      const response = await apiClient.get<Prompt>(`/prompts/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreatePrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PromptCreate) => {
      const response = await apiClient.post<Prompt>('/prompts', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
    },
  });
}

export function useUpdatePrompt(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PromptUpdate) => {
      const response = await apiClient.put<Prompt>(`/prompts/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
      queryClient.invalidateQueries({ queryKey: ['prompt', id] });
    },
  });
}

export function useDeletePrompt() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/prompts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['prompts'] });
    },
  });
}
