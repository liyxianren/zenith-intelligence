import React, { useState } from 'react';
import { NavLink } from 'react-router-dom';

const Sidebar: React.FC = () => {
  const [isOpen, setIsOpen] = useState(true);
  const navItems = [
    { path: '/', label: 'AI助手', icon: '💡', color: 'text-primary' },
    { path: '/courses', label: '课程', icon: '📚', color: 'text-success' },
    { path: '/programming', label: '编程', icon: '💻', color: 'text-warning' },
    { path: '/stats', label: '统计', icon: '📊', color: 'text-error' },
    { path: '/profile', label: '个人中心', icon: '👤', color: 'text-secondary' },
  ];

  return (
    <>
      {/* 移动端菜单按钮 */}
      <div className="md:hidden fixed top-4 left-4 z-50">
        <button
          onClick={() => setIsOpen(!isOpen)}
          className="bg-primary text-white p-2 rounded-lg shadow-lg hover:bg-primary/90 transition-colors duration-300"
        >
          {isOpen ? (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
            </svg>
          ) : (
            <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 12h16M4 18h16" />
            </svg>
          )}
        </button>
      </div>

      {/* 侧边栏 */}
      <aside
        className={`
          ${isOpen ? 'w-64' : 'w-20'}
          md:w-64
          bg-white border-r border-gray-200 flex flex-col
          fixed md:sticky top-0 left-0 h-screen z-40
          transition-all duration-300 ease-in-out
          overflow-hidden
          shadow-sm hover:shadow-md
        `}
      >
        {/* 侧边栏顶部 */}
        <div className="p-4 border-b border-gray-200 bg-gradient-to-r from-primary/5 to-secondary/5">
          <div className="flex items-center gap-3">
            <div className="w-10 h-10 rounded-lg bg-gradient-to-br from-primary to-secondary text-white flex items-center justify-center shadow-sm">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-6 w-6" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
              </svg>
            </div>
            {isOpen && (
              <div className="animate-fade-in">
                <h1 className="text-lg font-bold text-gray-900">AI学习助手</h1>
                <p className="text-xs text-gray-500">智能学习平台</p>
              </div>
            )}
          </div>
        </div>
        
        {/* 导航菜单 */}
        <nav className="flex-1 p-4 space-y-2">
          {navItems.map((item) => (
            <NavLink
              key={item.path}
              to={item.path}
              className={({ isActive }) =>
                `flex items-center space-x-3 px-3 py-2.5 rounded-xl transition-all duration-300 ${isActive
                  ? `bg-gradient-to-r from-primary/10 to-primary/5 ${item.color} font-medium shadow-sm border-l-4 border-primary`
                  : 'text-gray-700 hover:bg-gray-50 hover:shadow-sm hover:border-l-4 hover:border-gray-200'
                } ${!isOpen && 'justify-center'}`
              }
              onClick={() => setIsOpen(false)}
            >
              <span className={`text-xl ${item.color}`}>{item.icon}</span>
              {isOpen && <span className="text-sm font-medium">{item.label}</span>}
            </NavLink>
          ))}
        </nav>
        
        {/* 侧边栏底部 */}
        <div className={`p-4 border-t border-gray-200 bg-gray-50 transition-all duration-300 ${!isOpen && 'hidden'}`}>
          <div className="flex items-center gap-3 p-3 rounded-lg hover:bg-gray-100 transition-colors">
            <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center">
              <svg xmlns="http://www.w3.org/2000/svg" className="h-4 w-4" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
              </svg>
            </div>
            <div>
              <p className="text-sm font-medium text-gray-900">帮助中心</p>
              <p className="text-xs text-gray-500">获取支持</p>
            </div>
          </div>
          <div className="mt-4 text-xs text-gray-500 text-center">
            <p>AI Learning Assistant</p>
            <p className="mt-1">版本 1.0.0</p>
          </div>
        </div>
      </aside>

      {/* 遮罩层 */}
      {isOpen && (
        <div
          className="md:hidden fixed inset-0 bg-black/50 z-30 backdrop-blur-sm animate-fade-in"
          onClick={() => setIsOpen(false)}
        ></div>
      )}
    </>
  );
};

export default Sidebar;
