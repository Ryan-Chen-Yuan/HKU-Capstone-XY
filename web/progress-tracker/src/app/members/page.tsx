'use client';

import React, { useState } from 'react';
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
  Badge,
  Button,
  Separator
} from '@/components/ui/ui-components';
import { formatDate } from '../global';

export default function MembersPage() {
  // Team member detailed data
  const teamMembers = [
    { 
      id: 1, 
      name: 'CHEN Yuan', 
      role: 'Leader', 
      progress: 85, 
      avatar: '/avatars/member1.png',
      email: 'zhangsan@example.com',
      tasks: [
        { id: 1, title: 'Develop Medal Feedback feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-20' },
        { id: 2, title: 'Project Management', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-28' },
        // { id: 3, title: 'Data Visualization Component', status: 'in_progress', progress: 70, priority: 'medium', dueDate: '2025-03-15' },
        // { id: 4, title: 'Responsive Layout Optimization', status: 'pending', progress: 0, priority: 'low', dueDate: '2025-03-25' }
      ]
    },
    { 
      id: 2, 
      name: 'Xu Hanlin', 
      role: 'Member', 
      progress: 85, 
      avatar: '/avatars/member2.png',
      email: 'lisi@example.com',
      tasks: [
        { id: 5, title: 'Develop Response Suggestions/Tips feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-15' },
        { id: 6, title: 'Develop AI Conversation feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-25' },
        // { id: 7, title: 'User Permission Management', status: 'in_progress', progress: 60, priority: 'medium', dueDate: '2025-03-10' },
        // { id: 8, title: 'Performance Optimization', status: 'pending', progress: 0, priority: 'medium', dueDate: '2025-03-20' }
      ]
    },
    { 
      id: 3, 
      name: 'WANG Xueyao', 
      role: 'Member', 
      progress: 85, 
      avatar: '/avatars/member3.png',
      email: 'wangwu@example.com',
      tasks: [
        { id: 9, title: 'Develop Mood Score feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-10' },
        { id: 10, title: 'Develop Project Webpage', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-20' },
        // { id: 11, title: 'Component Library Design', status: 'completed', progress: 100, priority: 'medium', dueDate: '2025-03-01' },
        // { id: 12, title: 'Motion Design', status: 'in_progress', progress: 70, priority: 'low', dueDate: '2025-03-15' }
      ]
    },
    { 
      id: 4, 
      name: 'YU Yitao', 
      role: 'Member', 
      progress: 85, 
      avatar: '/avatars/member4.png',
      email: 'zhaoliu@example.com',
      tasks: [
        { id: 13, title: 'Develop AI Conversation feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-05' },
        // { id: 14, title: 'Data Model Design', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-15' },
        // { id: 15, title: 'Data Visualization Plan', status: 'in_progress', progress: 50, priority: 'medium', dueDate: '2025-03-10' },
        // { id: 16, title: 'User Behavior Analysis', status: 'pending', progress: 0, priority: 'medium', dueDate: '2025-03-25' }
      ]
    },
    { 
      id: 5, 
      name: 'SU Yingcheng', 
      role: 'Member', 
      progress: 85, 
      avatar: '/avatars/member5.png',
      email: 'qianqi@example.com',
      tasks: [
        { id: 17, title: 'Develop Event Analysis feature', status: 'completed', progress: 100, priority: 'high', dueDate: '2025-02-01' },
        // { id: 18, title: 'Team Coordination', status: 'in_progress', progress: 80, priority: 'high', dueDate: '2025-04-30' },
        // { id: 19, title: 'Progress Tracking', status: 'in_progress', progress: 75, priority: 'high', dueDate: '2025-04-30' },
        // { id: 20, title: 'Risk Management', status: 'in_progress', progress: 60, priority: 'medium', dueDate: '2025-04-30' }
      ]
    }
  ];

  // Currently selected member
  const [selectedMember, setSelectedMember] = useState(teamMembers[0]);

  // Get status badge style
  const getStatusBadge = (status) => {
    switch (status) {
      case 'completed':
        return <Badge variant="success">Completed</Badge>;
      case 'in_progress':
        return <Badge variant="primary">In Progress</Badge>;
      case 'pending':
        return <Badge variant="warning">Pending</Badge>;
      case 'delayed':
        return <Badge variant="danger">Delayed</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  // Get priority badge style
  const getPriorityBadge = (priority) => {
    switch (priority) {
      case 'high':
        return <Badge variant="danger">High</Badge>;
      case 'medium':
        return <Badge variant="warning">Medium</Badge>;
      case 'low':
        return <Badge variant="success">Low</Badge>;
      default:
        return <Badge>Unknown</Badge>;
    }
  };

  // Calculate completed task count
  const getCompletedTasksCount = (tasks) => {
    return tasks.filter(task => task.status === 'completed').length;
  };

  return (
    <main className="min-h-screen bg-gray-50 py-12">
      <Container>
        {/* Page Title */}
        <div className="mb-12">
          <PageTitle className="mb-3">Member Progress</PageTitle>
          <PageDescription>View the work progress and task allocation of team members</PageDescription>
        </div>

        {/* Member Selector */}
        <div className="mb-8 flex flex-wrap gap-2">
          {teamMembers.map(member => (
            <Button
              key={member.id}
              variant={selectedMember.id === member.id ? "primary" : "outline"}
              onClick={() => setSelectedMember(member)}
            >
              {member.name}
            </Button>
          ))}
        </div>

        {/* Member Details */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Member Info Card */}
          <Card>
            <CardHeader>
              <div className="flex flex-col items-center">
                <div className="h-24 w-24 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-3xl mb-4">
                  {selectedMember.name.charAt(0)}
                </div>
                <CardTitle className="text-xl">{selectedMember.name}</CardTitle>
                <p className="text-gray-500">{selectedMember.role}</p>
              </div>
            </CardHeader>
            <CardContent>
              <div className="space-y-4">
                {/* <div>
                  <p className="text-sm text-gray-500 mb-1">Email</p>
                  <p className="font-medium">{selectedMember.email}</p>
                </div> */}
                <div>
                  <p className="text-sm text-gray-500 mb-1">Overall Progress</p>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Completion</span>
                    <span>{selectedMember.progress}%</span>
                  </div>
                  <Progress value={selectedMember.progress} />
                </div>
                <div>
                  <p className="text-sm text-gray-500 mb-1">Task Completion</p>
                  <p className="font-medium">{getCompletedTasksCount(selectedMember.tasks)}/{selectedMember.tasks.length} tasks</p>
                </div>
              </div>
            </CardContent>
          </Card>

          {/* Task List */}
          <div className="lg:col-span-2">
            <Card>
              <CardHeader>
                <CardTitle>Task List</CardTitle>
              </CardHeader>
              <div className="divide-y divide-gray-200">
                {selectedMember.tasks.map(task => (
                  <div key={task.id} className="p-6">
                    <div className="flex justify-between items-start mb-2">
                      <h3 className="font-medium text-gray-900">{task.title}</h3>
                      <div className="flex space-x-2">
                        {getPriorityBadge(task.priority)}
                        {getStatusBadge(task.status)}
                      </div>
                    </div>
                    <div className="mb-2">
                      <div className="flex justify-between text-sm mb-1">
                        <span className="text-gray-500">Progress</span>
                        <span className="text-gray-500">{task.progress}%</span>
                      </div>
                      <Progress value={task.progress} />
                    </div>
                    <div className="text-sm text-gray-500">
                      Due Date: {formatDate(task.dueDate)}
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>

        {/* Team Overall Progress */}
        <div className="mt-12">
          <h2 className="text-2xl font-semibold text-gray-900 mb-6">Team Overall Progress</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-5 gap-6">
            {teamMembers.map(member => (
              <Card key={member.id}>
                <CardHeader>
                  <div className="flex flex-col items-center">
                    <div className="h-16 w-16 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-xl mb-2">
                      {member.name.charAt(0)}
                    </div>
                    <CardTitle>{member.name}</CardTitle>
                    <p className="text-sm text-gray-500">{member.role}</p>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="flex justify-between text-sm mb-1">
                    <span>Progress</span>
                    <span>{member.progress}%</span>
                  </div>
                  <Progress value={member.progress} className="mb-2" />
                  <p className="text-sm text-gray-500 text-center">
                    {getCompletedTasksCount(member.tasks)}/{member.tasks.length} tasks completed
                  </p>
                </CardContent>
              </Card>
            ))}
          </div>
        </div>
      </Container>
    </main>
  );
}
