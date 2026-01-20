import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { Post, PostCreate, PostUpdate, PostList, PostStatus, MediaUploadResponse } from '@/types';

interface UsePostsParams {
  skip?: number;
  limit?: number;
  status?: PostStatus;
  dateFrom?: string;
  dateTo?: string;
  search?: string;
}

export function usePosts(params: UsePostsParams = {}) {
  const { skip = 0, limit = 100, status, dateFrom, dateTo, search } = params;

  return useQuery({
    queryKey: ['posts', { skip, limit, status, dateFrom, dateTo, search }],
    queryFn: async () => {
      const queryParams = new URLSearchParams();
      queryParams.append('skip', skip.toString());
      queryParams.append('limit', limit.toString());
      if (status) queryParams.append('status', status);
      if (dateFrom) queryParams.append('date_from', dateFrom);
      if (dateTo) queryParams.append('date_to', dateTo);
      if (search) queryParams.append('search', search);

      const response = await apiClient.get<PostList>(`/posts?${queryParams}`);
      return response.data;
    },
  });
}

export function usePost(id: number) {
  return useQuery({
    queryKey: ['post', id],
    queryFn: async () => {
      const response = await apiClient.get<Post>(`/posts/${id}`);
      return response.data;
    },
    enabled: !!id,
  });
}

export function useCreatePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PostCreate) => {
      const response = await apiClient.post<Post>('/posts', data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}

export function useUpdatePost(id: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (data: PostUpdate) => {
      const response = await apiClient.put<Post>(`/posts/${id}`, data);
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      queryClient.invalidateQueries({ queryKey: ['post', id] });
    },
  });
}

export function useDeletePost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      await apiClient.delete(`/posts/${id}`);
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
    },
  });
}

export function usePublishPost() {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (id: number) => {
      const response = await apiClient.post<Post>(`/posts/${id}/publish`);
      return response.data;
    },
    onSuccess: (_, id) => {
      queryClient.invalidateQueries({ queryKey: ['posts'] });
      queryClient.invalidateQueries({ queryKey: ['post', id] });
    },
  });
}

export function useUploadMedia(postId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);

      const response = await apiClient.post<MediaUploadResponse>(
        `/posts/${postId}/media`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['post', postId] });
    },
  });
}

export function useRemoveMedia(postId: number) {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: async (mediaUrl: string) => {
      await apiClient.delete(`/posts/${postId}/media`, {
        params: { media_url: mediaUrl },
      });
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ['post', postId] });
    },
  });
}

export function useExportPostsCSV() {
  return useMutation({
    mutationFn: async (params: { status?: PostStatus; dateFrom?: string; dateTo?: string }) => {
      const queryParams = new URLSearchParams();
      if (params.status) queryParams.append('status', params.status);
      if (params.dateFrom) queryParams.append('date_from', params.dateFrom);
      if (params.dateTo) queryParams.append('date_to', params.dateTo);

      const response = await apiClient.get(`/posts/export/csv?${queryParams}`, {
        responseType: 'blob',
      });

      // Create download link
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `posts_export_${new Date().toISOString().split('T')[0]}.csv`);
      document.body.appendChild(link);
      link.click();
      link.remove();
      window.URL.revokeObjectURL(url);
    },
  });
}
