import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type {
  TextGenerationRequest,
  TextGenerationResponse,
  ImageGenerationRequest,
  ImageGenerationResponse,
  ReferenceImageUploadResponse,
} from '@/types';

export function useGenerateText() {
  return useMutation({
    mutationFn: async (data: TextGenerationRequest) => {
      const response = await apiClient.post<TextGenerationResponse>('/generate/text', data);
      return response.data;
    },
  });
}

export function useGenerateImage() {
  return useMutation({
    mutationFn: async (data: ImageGenerationRequest) => {
      const response = await apiClient.post<ImageGenerationResponse>('/generate/image', data);
      return response.data;
    },
  });
}

export function useUploadReferenceImage() {
  return useMutation({
    mutationFn: async (file: File) => {
      const formData = new FormData();
      formData.append('file', file);
      const response = await apiClient.post<ReferenceImageUploadResponse>(
        '/generate/image/reference',
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data',
          },
        }
      );
      return response.data;
    },
  });
}
