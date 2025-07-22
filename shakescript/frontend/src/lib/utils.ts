import { clsx, type ClassValue } from "clsx"
import { twMerge } from "tailwind-merge"
import { useAuth } from '../contexts/AuthContext';
import { useNavigate } from 'react-router-dom';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs))
}

export function useAuthFetch() {
  const { session } = useAuth();
  const navigate = useNavigate();

  const authFetch = async (url: string, options: RequestInit = {}) => {
    if (!session) {
      navigate('/login');
      throw new Error('Not authenticated');
    }
    const token = session.access_token;
    const headers = {
      ...(options.headers ? options.headers : {}),
      Authorization: `Bearer ${token}`,
    };
    return fetch(url, { ...options, headers });
  };

  return authFetch;
}
