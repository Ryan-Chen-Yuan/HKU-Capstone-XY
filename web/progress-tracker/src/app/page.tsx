'use client';

import React, { useState } from 'react';
import Link from 'next/link';
import { 
  Container, 
  PageTitle, 
  PageDescription, 
  Card, 
  CardHeader, 
  CardTitle, 
  CardContent, 
  CardFooter,
  Progress,
  Badge
} from '@/components/ui/ui-components';
import ProgressUpdate from './ProgressUpdate';
import AboutPage from './about';
import Schedule from './Schedule';

export default function HomePage() {
  const [activeTab, setActiveTab] = useState('overall'); // State to track the active tab

  const renderTabContent = () => {
    switch (activeTab) {
      case 'overall':
        return <ProgressUpdate/>;
      case 'about':
        return <AboutPage/>;
      case 'progressUpdate':
        return (<ProgressUpdate/>
        );
      case 'schedule':
        return <Schedule/>;
      default:
        return null;
    }
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* 页面标题 */}
        <div className="mb-12 text-center">
        <PageTitle className="text-3xl md:text-4xl mb-3 whitespace-nowrap">AI-Powered Counseling Ecosystem for Adolescent Mental Health Support</PageTitle>
          {/* <PageDescription className="text-xl">实时跟踪项目进展和团队成员工作状态</PageDescription> */}
        </div>

        {/* Tabs */}
        <div className="mb-6 flex justify-center space-x-4">
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'about' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('about')}
          >
            About 
          </button>
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'progressUpdate' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('progressUpdate')}
          >
            Progress Update
          </button>
          {/*
          <button 
            className={`px-4 py-2 rounded ${activeTab === 'schedule' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('schedule')}
          >
            Schedule
          </button> */}
          {/* <button 
            className={`px-4 py-2 rounded ${activeTab === 'overall' ? 'bg-blue-600 text-white' : 'bg-gray-200'}`}
            onClick={() => setActiveTab('overall')}
          >
            总体完成度
          </button> */}
        </div>

        {/* Tab Content */}
        <div>
          {renderTabContent()}
        </div>
      </Container>
    </main>
  );
}
