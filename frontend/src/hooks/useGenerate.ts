import { useMutation } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type {
  TextGenerationRequest,
  TextGenerationResponse,
  ImageGenerationRequest,
  ImageGenerationResponse,
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
