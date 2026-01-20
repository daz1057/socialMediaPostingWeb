import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type {
  Credential,
  CredentialCreate,
  CredentialUpdate,
  CredentialList,
  CredentialValidateRequest,
  CredentialValidateResponse,
} from '@/types';

interface UseCredentialsParams {
  skip?: number;
  limit?: number;
}

export function useCredentials(params: UseCredentialsParams = {}) {
  const { skip = 0, limit = 100 } = params;

  return useQuery({
    queryKey: ['credentials', { skip, limit }],
    queryFn: async () => {
      const response = await apiClient.get<CredentialList>(
        `/credentials?skip=${skip}&limit=${limit}`
      );
      return response.data;
    },
  });
}

export function useCredential(key: string) {
  return useQuery({
    queryKey: ['credential', key],
    queryFn: async () => {
      const response = await apiClient.get<Credential>(`/credentials/${key}`);
      return response.data;
    },
    enabled: !!key,
  });
}

export function useCreateCredential() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CredentialCreate) => {
      const response = await apiClient.post<Credential>('/credentials', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials'] });
    },
  });
}

export function useUpdateCredential(key: string) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: CredentialUpdate) => {
      const response = await apiClient.put<Credential>(`/credentials/${key}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials'] });
      queryClient.invalidateQueries({ queryKey: ['credential', key] });
    },
  });
}

export function useDeleteCredential() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (key: string) => {
      await apiClient.delete(`/credentials/${key}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['credentials'] });
    },
  });
}

export function useValidateCredential() {
  return useMutation({
    mutationFn: async (data: CredentialValidateRequest) => {
      const response = await apiClient.post<CredentialValidateResponse>(
        '/credentials/validate',
        data
      );
      return response.data;
    },
  });
}
