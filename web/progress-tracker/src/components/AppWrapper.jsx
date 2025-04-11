'use client';

import React from 'react';
import { DataProvider } from '@/lib/data-context';

// 应用根布局包装器，提供数据上下文
export function AppWrapper({ children }) {
  return (
    <DataProvider>
      {children}
    </DataProvider>
  );
}
