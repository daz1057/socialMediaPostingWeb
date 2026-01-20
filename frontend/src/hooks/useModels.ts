import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type {
  ModelConfig,
  ModelConfigCreate,
  ModelConfigUpdate,
  ModelConfigList,
  ModelType,
  ProvidersListResponse,
} from '@/types';

interface UseModelConfigsParams {
  skip?: number;
  limit?: number;
  provider?: string;
  modelType?: ModelType;
  enabledOnly?: boolean;
}

export function useModelConfigs(params: UseModelConfigsParams = {}) {
  const { skip = 0, limit = 100, provider, modelType, enabledOnly } = params;

  return useQuery({
    queryKey: ['modelConfigs', { skip, limit, provider, modelType, enabledOnly }],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', limit.toString());
      if (provider) queryParams.append('provider', provider);
      if (modelType) queryParams.append('model_type', modelType);
      if (enabledOnly !== undefined) queryParams.append('enabled_only', enabledOnly.toString());

      const response = await apiClient.get<ModelConfigList>(`/models?${queryParams}`);
      return response.data;
    },
  });
}

export function useModelConfig(id: number) {
  return useQuery({
    queryKey: ['modelConfig', id],
    queryFn: async () => {
      const response = await apiClient.get<ModelConfig>(`/models/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useProviders() {
  return useQuery({
    queryKey: ['providers'],
    queryFn: async () => {
      const response = await apiClient.get<ProvidersListResponse>('/models/providers/list');
      return response.data;
    },
  });
}

export function useCreateModelConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ModelConfigCreate) => {
      const response = await apiClient.post<ModelConfig>('/models', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modelConfigs'] });
    },
  });
}

export function useUpdateModelConfig(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: ModelConfigUpdate) => {
      const response = await apiClient.put<ModelConfig>(`/models/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modelConfigs'] });
      queryClient.invalidateQueries({ queryKey: ['modelConfig', id] });
    },
  });
}

export function useDeleteModelConfig() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/models/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['modelConfigs'] });
    },
  });
}
