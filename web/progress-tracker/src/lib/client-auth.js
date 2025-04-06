'use client';

import { useState, useEffect } from 'react';
import { useRouter } from 'next/navigation';

// 创建认证上下文
export function useAuth() {
  const [user, setUser] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const router = useRouter();

  // 初始化时检查用户登录状态
  useEffect(() => {
    const checkAuth = async () => {
      try {
        setLoading(true);
        setError(null);
        
        // 从localStorage获取token
        const token = localStorage.getItem('auth_token');
        
        if (!token) {
          setUser(null);
          setLoading(false);
          return;
        }
        
        // 验证token
        const response = await fetch('/api/auth/verify', {
          headers: {
            'Authorization': `Bearer ${token}`
          }
        });
        
        const data = await response.json();
        
        if (data.success) {
          setUser(data.user);
        } else {
          // Token无效，清除本地存储
          localStorage.removeItem('auth_token');
          setUser(null);
        }
      } catch (err) {
        console.error('认证检查错误:', err);
        setError('认证检查失败');
        setUser(null);
      } finally {
        setLoading(false);
      }
    };
    
    checkAuth();
  }, []);

  // 登录函数
  const login = async (username, password) => {
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/auth/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });
      
      const data = await response.json();
      
      if (data.success) {
        // 保存token到localStorage
        localStorage.setItem('auth_token', data.token);
        setUser(data.user);
        return true;
      } else {
        setError(data.message || '登录失败');
        return false;
      }
    } catch (err) {
      console.error('登录错误:', err);
      setError('登录请求失败');
      return false;
    } finally {
      setLoading(false);
    }
  };

  // 登出函数
  const logout = () => {
    localStorage.removeItem('auth_token');
    setUser(null);
    router.push('/login');
  };

  // 获取认证头信息
  const getAuthHeaders = () => {
    const token = localStorage.getItem('auth_token');
    return token ? { 'Authorization': `Bearer ${token}` } : {};
  };

  return {
    user,
    loading,
    error,
    login,
    logout,
    getAuthHeaders,
    isAuthenticated: !!user
  };
}
