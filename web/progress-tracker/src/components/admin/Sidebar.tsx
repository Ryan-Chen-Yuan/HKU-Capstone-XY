'use client';

import { useState } from 'react';
import Link from 'next/link';
import { signOut } from 'next-auth/react';
import { 
  HomeIcon, 
  UserGroupIcon, 
  ClipboardDocumentListIcon, 
  DocumentTextIcon,
  ChartBarIcon,
  Cog6ToothIcon
} from '@heroicons/react/24/outline';

interface SidebarProps {
  isOpen: boolean;
  setIsOpen: (isOpen: boolean) => void;
}

export default function Sidebar({ isOpen, setIsOpen }: SidebarProps) {
  const [activeItem, setActiveItem] = useState('dashboard');

  const menuItems = [
    { id: 'dashboard', name: '仪表盘', href: '/admin', icon: HomeIcon },
    { id: 'users', name: '用户管理', href: '/admin/users', icon: UserGroupIcon },
    { id: 'projects', name: '项目管理', href: '/admin/projects', icon: ChartBarIcon },
    { id: 'tasks', name: '任务管理', href: '/admin/tasks', icon: ClipboardDocumentListIcon },
    { id: 'proposals', name: '提案管理', href: '/admin/proposals', icon: DocumentTextIcon },
    { id: 'settings', name: '系统设置', href: '/admin/settings', icon: Cog6ToothIcon },
  ];

  return (
    <div 
      className={`fixed inset-y-0 left-0 z-50 bg-white shadow-lg transition-all duration-300 ${
        isOpen ? 'w-64' : 'w-20'
      }`}
    >
      <div className="flex flex-col h-full">
        {/* Logo */}
        <div className="flex items-center justify-center h-16 border-b">
          <h1 className={`font-semibold text-blue-600 transition-opacity duration-300 ${
            isOpen ? 'opacity-100' : 'opacity-0'
          }`}>
            毕设项目管理系统
          </h1>
          {!isOpen && (
            <span className="text-blue-600 font-bold text-xl">P</span>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 pt-4 pb-4">
          <ul className="space-y-1">
            {menuItems.map((item) => (
              <li key={item.id}>
                <Link
                  href={item.href}
                  className={`flex items-center px-4 py-3 text-gray-700 hover:bg-blue-50 hover:text-blue-600 transition-colors ${
                    activeItem === item.id ? 'bg-blue-50 text-blue-600' : ''
                  }`}
                  onClick={() => setActiveItem(item.id)}
                >
                  <item.icon className="h-6 w-6" />
                  <span className={`ml-3 transition-opacity duration-300 ${
                    isOpen ? 'opacity-100' : 'opacity-0'
                  }`}>
                    {item.name}
                  </span>
                </Link>
              </li>
            ))}
          </ul>
        </nav>

        {/* Logout */}
        <div className="border-t p-4">
          <button
            onClick={() => signOut({ callbackUrl: '/login' })}
            className="flex items-center w-full px-4 py-2 text-gray-700 hover:bg-red-50 hover:text-red-600 rounded-md transition-colors"
          >
            <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
            </svg>
            <span className={`ml-3 transition-opacity duration-300 ${
              isOpen ? 'opacity-100' : 'opacity-0'
            }`}>
              退出登录
            </span>
          </button>
        </div>
      </div>
    </div>
  );
}
