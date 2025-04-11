import { Card, CardHeader, CardTitle, CardContent, Progress, CardFooter, Badge } from "@/components/ui/ui-components";
import Link from "next/link";
import getStatusBadge from "./global";

const ProgressUpdate = () => {
  const projectProgress = {
    overall: 20,
    timeElapsed: 25,
    tasksCompleted: 70,
    milestonesReached: 20
  };

  const teamMembers = [
    { id: 1, name: 'Chen yuan', role: 'Leader', progress: 85, avatar: '/avatars/member1.png' },
    { id: 2, name: 'Xu Hanlin', role: 'Member', progress: 85, avatar: '/avatars/member2.png' },
    { id: 3, name: 'WANG Xueyao', role: 'Member', progress: 85, avatar: '/avatars/member3.png' },
    { id: 4, name: 'Yu Yitao', role: 'Member', progress: 85, avatar: '/avatars/member4.png' },
    { id: 5, name: 'Su Yingcheng', role: 'Member', progress: 85, avatar: '/avatars/member5.png' }
  ];

  // const milestones = [
  //   { id: 1, title: 'Planning and Analysis ', status: 'completed', date: '2025-03-10' },
  //   { id: 2, title: 'Prototype Design', status: 'in_progress', date: '2025-02-28' },
  //   { id: 3, title: 'Frontend Development', status: 'in_progress', date: '2025-03-15' },
  //   { id: 4, title: 'Backend Development', status: 'pending', date: '2025-03-30' }
  // ];

  const milestones = [
    { 
      id: 1, 
      title: 'Planning phase', 
      description: 'Define project objectives and outline development plan',
      startDate: '2025-01-20', 
      endDate: '2025-03-10', 
      status: 'completed', 
      progress: 100 
    },
    { 
      id: 2, 
      title: 'Prototype design', 
      description: 'Draft UI design and define technical architecture',
      startDate: '2025-03-10', 
      endDate: '2025-04-07', 
      status: 'in_progress', 
      progress: 95 
    },
    { 
      id: 3, 
      title: 'Development phase', 
      description: 'Implement frontend and backend core features',
      startDate: '2025-04-7', 
      endDate: '2025-07-7', 
      status: 'pending', 
      progress: 0 
    },
    { 
      id: 4, 
      title: 'Testing phase', 
      description: 'Perform functional testing, performance testing and user testing to fix issues',
      startDate: '2025-06-17', 
      endDate: '2025-7-7', 
      status: 'pending', 
      progress: 0 
    },
    { 
      id: 5, 
      title: 'Deployment', 
      description: 'Deploy the system to a production environment',
      startDate: '2025-06-17', 
      endDate: '2025-07-7', 
      status: 'pending', 
      progress: 0 
    }
  ];

  const formatDate = (dateString) => {
    return new Date(dateString).toLocaleDateString('en');
  };
    
  const getDaysBetween = (startDate, endDate) => {
    const start = new Date(startDate);
    const end = new Date(endDate);
    return Math.round((end - start) / (1000 * 60 * 60 * 24));
  };

  return (
    <>
  {/* Overall Project Progress */}
  <div className="mb-12">
    <h2 className="text-2xl font-semibold text-gray-900 mb-6">Overall Project Progress</h2>
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      <Card>
        <CardHeader>
          <CardTitle>Overall Completion</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="flex flex-col items-center">
            <div className="relative w-32 h-32">
              <svg className="w-full h-full" viewBox="0 0 100 100">
                <circle 
                  className="text-gray-200" 
                  strokeWidth="10" 
                  stroke="currentColor" 
                  fill="transparent" 
                  r="40" 
                  cx="50" 
                  cy="50" 
                />
                <circle 
                  className="text-blue-600" 
                  strokeWidth="10" 
                  strokeDasharray={`${projectProgress.overall * 2.51} 251`}
                  strokeLinecap="round" 
                  stroke="currentColor" 
                  fill="transparent" 
                  r="40" 
                  cx="50" 
                  cy="50" 
                />
              </svg>
              <div className="absolute inset-0 flex items-center justify-center">
                <span className="text-3xl font-semibold text-gray-900">{projectProgress.overall}%</span>
              </div>
            </div>
          </div>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>Timeline</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-2 flex justify-between text-sm">
            {/* <span>Time Elapsed</span> */}
            <span>{projectProgress.timeElapsed}%</span>
          </div>
          <Progress value={projectProgress.timeElapsed} className="mb-4" />
          <p className="text-sm text-gray-500">expected to be completed by July 7, 2025</p>
        </CardContent>
      </Card>

      {/* <Card>
        <CardHeader>
          <CardTitle>Tasks Completed</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-2 flex justify-between text-sm">
            <span>{projectProgress.tasksCompleted}%</span>
          </div>
          <Progress value={projectProgress.tasksCompleted} className="mb-4" />
          <p className="text-sm text-gray-500">28/40 tasks completed</p>
        </CardContent>
      </Card> */}

      <Card>
        <CardHeader>
          <CardTitle>Milestones Reached</CardTitle>
        </CardHeader>
        <CardContent>
          <div className="mb-2 flex justify-between text-sm">
            <span>{projectProgress.milestonesReached}%</span>
          </div>
          <Progress value={projectProgress.milestonesReached} className="mb-4" />
          <p className="text-sm text-gray-500">1/5 milestones achieved</p>
        </CardContent>
      </Card>
    </div>
  </div>

  {/* Team Member Progress*/}
  <div className="mb-12">
    <div className="flex justify-between items-center mb-6">
      <h2 className="text-2xl font-semibold text-gray-900">Team Member Progress</h2>
      <Link 
        href="https://github.com/Ryan-Chen-Yuan/HKU-Capstone-XY/tree/main/docs" 
        target="_blank" 
        className="text-blue-600 hover:text-blue-800">
        Details &rarr;
      </Link>
    </div>
    {/* <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
      {teamMembers.map(member => (
        <Card key={member.id}>
          <CardHeader className="flex flex-row items-center space-x-4">
            <div className="h-12 w-12 rounded-full bg-blue-100 flex items-center justify-center text-blue-600 font-semibold text-lg">
              {member.name.charAt(0)}
            </div>
            <div>
              <CardTitle>{member.name}</CardTitle>
              <p className="text-sm text-gray-500">{member.role}</p>
            </div>
          </CardHeader>
          <CardContent>
            <div className="mb-2 flex justify-between text-sm">
              <span>Task progress</span>
              <span>{member.progress}%</span>
            </div>
            <Progress value={member.progress} />
          </CardContent>
        </Card>
      ))}
    </div> */}
  </div>

  {/* Latest Milestones */}
  <div className="mb-12">
    <div className="flex justify-between items-center mb-6">
      <h2 className="text-2xl font-semibold text-gray-900">Latest Milestones</h2>
      {/* <Link href="/progress" className="text-blue-600 hover:text-blue-800">
        查看全部 &rarr;
      </Link> */}
    </div>
    {/* <Card> */}
      {/* <div className="divide-y divide-gray-200">
        {milestones.map(milestone => (
          <div key={milestone.id} className="p-6 flex justify-between items-center">
            <div>
              <h3 className="font-medium text-gray-900">{milestone.title}</h3>
              <p className="text-sm text-gray-500">Date: {formatDate(milestone.date)}</p>
            </div>
            <div>
              {getStatusBadge(milestone.status)}
            </div>
          </div>
        ))}
      </div> */}
       <div className="space-y-6">
            {milestones.map((milestone) => (
              <Card key={milestone.id}>
                <CardHeader>
                  <div className="flex justify-between items-start">
                    <div>
                      <CardTitle>{milestone.title}</CardTitle>
                      <p className="text-gray-500">{milestone.description}</p>
                    </div>
                    <div>
                      {getStatusBadge(milestone.status)}
                    </div>
                  </div>
                </CardHeader>
                <CardContent>
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Time period</p>
                      <p className="font-medium">
                        {formatDate(milestone.startDate)} - {formatDate(milestone.endDate)}
                      </p>
                      <p className="text-sm text-gray-500 mt-1">
                        last {getDaysBetween(milestone.startDate, milestone.endDate)} days
                      </p>
                    </div>
                    <div>
                      <p className="text-sm text-gray-500 mb-1">Progress</p>
                      <div className="flex justify-between text-sm mb-1">
                        {/* <span>progress</span> */}
                        <span>{milestone.progress}%</span>
                      </div>
                      <Progress value={milestone.progress} />
                    </div>
                  </div>
                </CardContent>
              </Card>
            ))}
          </div>
    {/* </Card> */}
  </div>

  {/* 快速链接 */}
  {/* <div>
    <h2 className="text-2xl font-semibold text-gray-900 mb-6">快速链接</h2>
    <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
      <Link href="/proposal" className="block">
        <Card className="transition-transform hover:scale-105">
          <CardHeader>
            <CardTitle>项目设计Proposal</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">查看项目设计方案和详细说明</p>
          </CardContent>
          <CardFooter className="justify-end">
            <span className="text-blue-600">查看详情 &rarr;</span>
          </CardFooter>
        </Card>
      </Link>
      
      <Link href="/progress" className="block">
        <Card className="transition-transform hover:scale-105">
          <CardHeader>
            <CardTitle>项目进度详情</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">查看项目里程碑和详细进度</p>
          </CardContent>
          <CardFooter className="justify-end">
            <span className="text-blue-600">查看详情 &rarr;</span>
          </CardFooter>
        </Card>
      </Link>
      
      <Link href="/about" className="block">
        <Card className="transition-transform hover:scale-105">
          <CardHeader>
            <CardTitle>关于项目</CardTitle>
          </CardHeader>
          <CardContent>
            <p className="text-gray-500">了解项目背景和团队信息</p>
          </CardContent>
          <CardFooter className="justify-end">
            <span className="text-blue-600">查看详情 &rarr;</span>
          </CardFooter>
        </Card>
      </Link>
    </div>
  </div> */}
  </>
  );
};

export default ProgressUpdate;