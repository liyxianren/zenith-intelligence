import React, { useState } from 'react';
import { useSelector, useDispatch } from 'react-redux';
import type { RootState } from '../../store';
import { logout } from '../../store/slices/userSlice';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

const ProfilePage: React.FC = () => {
  const dispatch = useDispatch();
  const userState = useSelector((state: RootState) => state.user);
  
  // 模拟用户数据
  const [user, setUser] = useState({
    name: userState.name || '张三',
    email: userState.email || 'zhangsan@example.com',
    avatar: null,
    bio: '热爱学习，喜欢探索新知识',
  });

  // 模拟学习统计数据
  const stats = {
    totalProblems: 120,
    solvedProblems: 95,
    learningTime: 45,
    accuracy: 85,
    weeklyProgress: [
      { day: '周一', problems: 12 },
      { day: '周二', problems: 8 },
      { day: '周三', problems: 15 },
      { day: '周四', problems: 10 },
      { day: '周五', problems: 14 },
      { day: '周六', problems: 6 },
      { day: '周日', problems: 5 },
    ],
  };

  // 模拟成就数据
  const achievements = [
    { id: '1', name: '初学者', description: '完成第一个问题', date: '2026-01-15', icon: '🎯' },
    { id: '2', name: '解题能手', description: '解决50个问题', date: '2026-01-28', icon: '🏆' },
    { id: '3', name: '学习达人', description: '学习时间超过24小时', date: '2026-02-10', icon: '⏰' },
  ];

  const [isEditing, setIsEditing] = useState(false);
  const [editForm, setEditForm] = useState(user);

  const handleEditSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setUser(editForm);
    setIsEditing(false);
  };

  const handleLogout = () => {
    dispatch(logout());
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">个人资料</h1>
        <p className="text-gray-600">管理你的个人信息和学习数据</p>
      </div>
      
      {/* 用户信息卡片 */}
      <Card shadow="lg" padding="lg">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex items-center gap-6">
            <div className="w-24 h-24 rounded-full bg-gradient-to-br from-primary to-secondary text-white flex items-center justify-center text-3xl font-bold shadow-lg">
              {user.name.charAt(0).toUpperCase()}
            </div>
            <div>
              <h2 className="text-2xl font-semibold text-gray-900">{user.name}</h2>
              <p className="text-gray-600 mt-1">{user.email}</p>
              {user.bio && (
                <p className="text-gray-500 text-sm mt-2">{user.bio}</p>
              )}
            </div>
          </div>
          <div className="flex flex-col sm:flex-row gap-3 w-full md:w-auto">
            <Button
              variant={isEditing ? 'secondary' : 'primary'}
              onClick={() => setIsEditing(!isEditing)}
              size="md"
            >
              {isEditing ? '取消' : '编辑资料'}
            </Button>
            <Button variant="outline" onClick={handleLogout} size="md">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M17 16l4-4m0 0l-4-4m4 4H7m6 4v1a3 3 0 01-3 3H6a3 3 0 01-3-3V7a3 3 0 013-3h4a3 3 0 013 3v1" />
              </svg>
              退出登录
            </Button>
          </div>
        </div>

        {isEditing && (
          <div className="mt-8 pt-8 border-t border-gray-200 animate-slide-in">
            <h3 className="text-lg font-semibold text-gray-800 mb-6">编辑个人资料</h3>
            <form onSubmit={handleEditSubmit} className="space-y-6">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">姓名</label>
                  <Input
                    value={editForm.name}
                    onChange={(e) => setEditForm({ ...editForm, name: e.target.value })}
                    fullWidth
                  />
                </div>
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">邮箱</label>
                  <Input
                    value={editForm.email}
                    onChange={(e) => setEditForm({ ...editForm, email: e.target.value })}
                    fullWidth
                  />
                </div>
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-2">个人简介</label>
                <textarea
                  value={editForm.bio || ''}
                  onChange={(e) => setEditForm({ ...editForm, bio: e.target.value })}
                  className="w-full px-4 py-3 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary text-sm transition-all duration-300"
                  rows={4}
                />
              </div>
              <div className="flex justify-end">
                <Button type="submit" size="md">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4" />
                  </svg>
                  保存更改
                </Button>
              </div>
            </form>
          </div>
        )}
      </Card>

      {/* 学习统计卡片 */}
      <Card shadow="lg" padding="lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-6">学习统计</h3>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-4">
          <div className="bg-primary/5 rounded-xl p-4 text-center card-hover">
            <div className="text-2xl font-bold text-primary mb-1">{stats.totalProblems}</div>
            <div className="text-sm text-gray-600">总问题数</div>
          </div>
          <div className="bg-success/5 rounded-xl p-4 text-center card-hover">
            <div className="text-2xl font-bold text-success mb-1">{stats.solvedProblems}</div>
            <div className="text-sm text-gray-600">已解决</div>
          </div>
          <div className="bg-accent/5 rounded-xl p-4 text-center card-hover">
            <div className="text-2xl font-bold text-accent mb-1">{stats.learningTime}h</div>
            <div className="text-sm text-gray-600">学习时间</div>
          </div>
          <div className="bg-error/5 rounded-xl p-4 text-center card-hover">
            <div className="text-2xl font-bold text-error mb-1">{stats.accuracy}%</div>
            <div className="text-sm text-gray-600">准确率</div>
          </div>
        </div>

        <div className="mt-8">
          <h4 className="font-semibold text-gray-800 mb-4">周学习进度</h4>
          <div className="space-y-4">
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
        </div>
      </Card>

      {/* 成就卡片 */}
      <Card shadow="lg" padding="lg">
        <h3 className="text-lg font-semibold text-gray-800 mb-6">我的成就</h3>
        <div className="space-y-4">
          {achievements.map((achievement, index) => (
            <div 
              key={achievement.id} 
              className="flex items-center gap-4 p-4 bg-gray-50 rounded-xl hover:bg-gray-100 transition-all duration-300 card-hover"
              style={{ animationDelay: `${index * 100}ms` }}
            >
              <div className="w-12 h-12 rounded-full bg-gradient-to-br from-accent to-warning flex items-center justify-center text-xl shadow-md">
                {achievement.icon}
              </div>
              <div className="flex-1">
                <div className="flex flex-col sm:flex-row sm:justify-between sm:items-start gap-2">
                  <h4 className="font-semibold text-gray-900">{achievement.name}</h4>
                  <span className="text-sm text-gray-500">{achievement.date}</span>
                </div>
                <p className="text-sm text-gray-600 mt-1">{achievement.description}</p>
              </div>
            </div>
          ))}
        </div>
      </Card>
    </div>
  );
};

export default ProfilePage;