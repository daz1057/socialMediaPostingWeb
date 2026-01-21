import { useMutation, useQuery } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type { OCRProcessResponse, OCRProvidersResponse } from '@/types';

export interface ProcessImageParams {
  file: File;
  model_config_id: number;
  custom_prompt?: string;
  template_name?: string;
  template_tags?: string[];
}

export function useProcessImage() {
  return useMutation({
    mutationFn: async (params: ProcessImageParams) => {
      const formData = new FormData();
      formData.append('file', params.file);
      formData.append('model_config_id', params.model_config_id.toString());

      if (params.custom_prompt) {
        formData.append('custom_prompt', params.custom_prompt);
      }
      if (params.template_name) {
        formData.append('template_name', params.template_name);
      }
      if (params.template_tags && params.template_tags.length > 0) {
        formData.append('template_tags', params.template_tags.join(','));
      }

      const response = await apiClient.post<OCRProcessResponse>('/ocr/process', formData, {
        headers: {
          'Content-Type': 'multipart/form-data',
        },
      });
      return response.data;
    },
  });
}

export function useOCRProviders() {
  return useQuery({
    queryKey: ['ocr-providers'],
    queryFn: async () => {
      const response = await apiClient.get<OCRProvidersResponse>('/ocr/providers');
      return response.data;
    },
  });
}
