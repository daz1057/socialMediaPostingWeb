import { useMutation, useQuery, useQueryClient } from '@tanstack/react-query';
import { apiClient } from '@/api/client';
import { useAuthStore } from '@/store/authStore';
import type { User, UserCreate, LoginRequest, TokenResponse } from '@/types';

export function useCurrentUser() {
  const { accessToken, setUser } = useAuthStore();
  const storedToken = accessToken ?? localStorage.getItem('access_token');

  return useQuery({
    queryKey: ['currentUser'],
    queryFn: async () => {
      const response = await apiClient.get<User>('/auth/me');
      return response.data;
    },
    enabled: !!storedToken,
    retry: false,
    onSuccess: (user) => {
      setUser(user);
    },
  });
}

export function useLogin() {
  const queryClient = useQueryClient();
  const { setTokens, setUser } = useAuthStore();

  return useMutation({
    mutationFn: async (credentials: LoginRequest) => {
      // OAuth2 form data format
      const formData = new URLSearchParams();
      formData.append('username', credentials.username);
      formData.append('password', credentials.password);

      const response = await apiClient.post<TokenResponse>('/auth/login', formData, {
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
        },
      });
      return response.data;
    },
    onSuccess: async (data) => {
      setTokens(data.access_token, data.refresh_token);

      // Fetch user info after login
      const userResponse = await apiClient.get<User>('/auth/me');
      setUser(userResponse.data);

      queryClient.invalidateQueries({ queryKey: ['currentUser'] });
    },
  });
}

export function useRegister() {
  return useMutation({
    mutationFn: async (userData: UserCreate) => {
      const response = await apiClient.post<User>('/auth/register', userData);
      return response.data;
    },
  });
}

export function useLogout() {
  const queryClient = useQueryClient();
  const { logout } = useAuthStore();

  return useMutation({
    mutationFn: async () => {
      try {
        await apiClient.post('/auth/logout');
      } catch {
        // Ignore logout errors
      }
    },
    onSettled: () => {
      logout();
      queryClient.clear();
    },
  });
}
