import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';

const StatsPage: React.FC = () => {
  // 模拟学习数据
  const stats = {
    totalProblems: 120,
    solvedProblems: 95,
    learningTime: 45,
    accuracy: 85,
    weeklyProgress: [
      { day: '周一', problems: 12, time: 2.5 },
      { day: '周二', problems: 8, time: 1.8 },
      { day: '周三', problems: 15, time: 3.2 },
      { day: '周四', problems: 10, time: 2.0 },
      { day: '周五', problems: 14, time: 2.8 },
      { day: '周六', problems: 6, time: 1.5 },
      { day: '周日', problems: 5, time: 1.2 },
    ],
    subjectBreakdown: [
      { subject: '数学', problems: 45, accuracy: 90, color: 'bg-primary' },
      { subject: '物理', problems: 30, accuracy: 85, color: 'bg-success' },
      { subject: '编程', problems: 25, accuracy: 80, color: 'bg-accent' },
      { subject: '化学', problems: 20, accuracy: 75, color: 'bg-error' },
    ],
  };

  const [timeRange, setTimeRange] = useState('week');

  const handleExport = () => {
    // 模拟数据导出
    alert('数据导出功能已触发');
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 页面标题 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div>
          <h1 className="text-3xl font-bold text-gray-900 mb-2">学习统计</h1>
          <p className="text-gray-600">追踪你的学习进度和表现</p>
        </div>
        <Button variant="secondary" onClick={handleExport} size="md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 16v1a3 3 0 003 3h10a3 3 0 003-3v-1m-4-4l-4 4m0 0l-4-4m4 4V4" />
          </svg>
          导出数据
        </Button>
      </div>
      
      {/* 时间范围选择 */}
      <div className="bg-white rounded-xl shadow-sm p-1 border border-gray-100 inline-block">
        <Button
          variant={timeRange === 'week' ? 'primary' : 'outline'}
          onClick={() => setTimeRange('week')}
          className="rounded-lg"
        >
          周
        </Button>
        <Button
          variant={timeRange === 'month' ? 'primary' : 'outline'}
          onClick={() => setTimeRange('month')}
          className="rounded-lg"
        >
          月
        </Button>
        <Button
          variant={timeRange === 'year' ? 'primary' : 'outline'}
          onClick={() => setTimeRange('year')}
          className="rounded-lg"
        >
          年
        </Button>
      </div>
      
      {/* 统计卡片 */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        <Card shadow="lg" hover={true} className="animate-fade-in" style={{ animationDelay: '0ms' }}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">总问题数</h3>
              <div className="w-10 h-10 rounded-full bg-primary/10 text-primary flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2" />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.totalProblems}</p>
            <p className="text-sm text-success mt-2 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
              较上周 +12%
            </p>
          </div>
        </Card>
        
        <Card shadow="lg" hover={true} className="animate-fade-in" style={{ animationDelay: '100ms' }}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">已解决</h3>
              <div className="w-10 h-10 rounded-full bg-success/10 text-success flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.solvedProblems}</p>
            <p className="text-sm text-success mt-2 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
              解决率 {Math.round((stats.solvedProblems / stats.totalProblems) * 100)}%
            </p>
          </div>
        </Card>
        
        <Card shadow="lg" hover={true} className="animate-fade-in" style={{ animationDelay: '200ms' }}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">学习时间</h3>
              <div className="w-10 h-10 rounded-full bg-accent/10 text-accent flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.learningTime}h</p>
            <p className="text-sm text-success mt-2 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
              较上周 +8%
            </p>
          </div>
        </Card>
        
        <Card shadow="lg" hover={true} className="animate-fade-in" style={{ animationDelay: '300ms' }}>
          <div className="p-6">
            <div className="flex items-center justify-between mb-4">
              <h3 className="text-sm font-medium text-gray-600">准确率</h3>
              <div className="w-10 h-10 rounded-full bg-error/10 text-error flex items-center justify-center">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
                </svg>
              </div>
            </div>
            <p className="text-3xl font-bold text-gray-900">{stats.accuracy}%</p>
            <p className="text-sm text-success mt-2 flex items-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4 mr-1" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 10l7-7m0 0l7 7m-7-7v18" />
              </svg>
              较上周 +2%
            </p>
          </div>
        </Card>
      </div>
      
      {/* 详细统计 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card shadow="lg" padding="lg" className="animate-slide-in">
          <h3 className="text-lg font-semibold text-gray-800 mb-6">学科分布</h3>
          <div className="space-y-5">
            {stats.subjectBreakdown.map((item) => (
              <div key={item.subject}>
                <div className="flex justify-between items-center mb-2">
                  <div className="flex items-center gap-3">
                    <div className={`w-3 h-3 rounded-full ${item.color}`}></div>
                    <span className="font-medium text-gray-700">{item.subject}</span>
                  </div>
                  <span className="text-sm font-medium text-gray-600">{item.problems} 题 ({item.accuracy}%)</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                  <div 
                    className={`h-2.5 rounded-full transition-all duration-700 ease-out ${item.color}`}
                    style={{ width: `${(item.problems / stats.totalProblems) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card shadow="lg" padding="lg" className="animate-slide-in" style={{ animationDelay: '100ms' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-6">周学习进度</h3>
          <div className="space-y-5">
            {stats.weeklyProgress.map((item) => (
              <div key={item.day}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">{item.day}</span>
                  <span className="text-sm font-medium text-gray-600">{item.problems} 题</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                  <div 
                    className="bg-primary h-2.5 rounded-full transition-all duration-700 ease-out"
                    style={{ width: `${(item.problems / 15) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        <Card shadow="lg" padding="lg" className="animate-slide-in" style={{ animationDelay: '200ms' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-6">每日学习时间</h3>
          <div className="space-y-5">
            {stats.weeklyProgress.map((item) => (
              <div key={item.day}>
                <div className="flex justify-between items-center mb-2">
                  <span className="font-medium text-gray-700">{item.day}</span>
                  <span className="text-sm font-medium text-gray-600">{item.time} 小时</span>
                </div>
                <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                  <div 
                    className="bg-success h-2.5 rounded-full transition-all duration-700 ease-out"
                    style={{ width: `${(item.time / 4) * 100}%` }}
                  ></div>
                </div>
              </div>
            ))}
          </div>
        </Card>

        <Card shadow="lg" padding="lg" className="animate-slide-in" style={{ animationDelay: '300ms' }}>
          <h3 className="text-lg font-semibold text-gray-800 mb-6">学习趋势</h3>
          <div className="h-64 bg-gray-50 rounded-xl flex items-center justify-center border border-gray-200">
            <div className="text-center">
              <div className="w-16 h-16 bg-primary/10 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-8 w-8 text-primary" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z" />
                </svg>
              </div>
              <p className="text-gray-600">学习趋势图表</p>
              <p className="text-sm text-gray-500 mt-2">数据可视化功能即将上线</p>
            </div>
          </div>
        </Card>
      </div>
    </div>
  );
};

export default StatsPage;