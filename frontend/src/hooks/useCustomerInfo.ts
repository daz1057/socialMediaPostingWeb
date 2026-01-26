import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import type {
  CustomerInfo,
  CustomerInfoList,
  CustomerInfoUpdate,
  CustomerCategoriesResponse,
  CustomerCategory,
} from '@/types';

const CUSTOMER_INFO_KEY = 'customerInfo';

/**
 * Get all category metadata with injection rules
 */
export function useCustomerInfoCategories() {
  return useQuery<CustomerCategoriesResponse>({
    queryKey: [CUSTOMER_INFO_KEY, 'categories'],
    queryFn: async () => {
      const response = await apiClient.get('/customer-info/categories');
      return response.data;
    },
  });
}

/**
 * List all customer info for the current user
 */
export function useCustomerInfoList() {
  return useQuery<CustomerInfoList>({
    queryKey: [CUSTOMER_INFO_KEY, 'list'],
    queryFn: async () => {
      const response = await apiClient.get('/customer-info/');
      return response.data;
    },
  });
}

/**
 * Get customer info for a specific category
 */
export function useCustomerInfo(category: CustomerCategory) {
  return useQuery<CustomerInfo>({
    queryKey: [CUSTOMER_INFO_KEY, category],
    queryFn: async () => {
      const response = await apiClient.get(`/customer-info/${encodeURIComponent(category)}`);
      return response.data;
    },
    enabled: !!category,
  });
}

/**
 * Update customer info for a category (upsert behavior)
 */
export function useUpdateCustomerInfo(category: CustomerCategory) {
  const queryClient = useQueryClient();

  return useMutation<CustomerInfo, Error, CustomerInfoUpdate>({
    mutationFn: async (data) => {
      const response = await apiClient.put(
        `/customer-info/${encodeURIComponent(category)}`,
        data
      );
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CUSTOMER_INFO_KEY] });
    },
  });
}

/**
 * Initialize all categories for a new user
 */
export function useInitializeCustomerInfo() {
  const queryClient = useQueryClient();

  return useMutation<CustomerInfoList, Error>({
    mutationFn: async () => {
      const response = await apiClient.post('/customer-info/initialize');
      return response.data;
    },
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: [CUSTOMER_INFO_KEY] });
    },
  });
}
