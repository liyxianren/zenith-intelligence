import { BrowserRouter as Router, Routes, Route, Outlet } from 'react-router-dom';
import { lazy, Suspense } from 'react';
import Header from './components/layout/Header';
import Sidebar from './components/layout/Sidebar';
import Footer from './components/layout/Footer';
import ProtectedRoute from './components/layout/ProtectedRoute';
import Login from './pages/Login/Login';
import Register from './pages/Register/Register';

// 懒加载页面组件
const AppPage = lazy(() => import('./pages/App/App'));
const CoursesPage = lazy(() => import('./pages/Courses/Courses'));
const ProfilePage = lazy(() => import('./pages/Profile/Profile'));
const ProgrammingPage = lazy(() => import('./pages/Programming/Programming'));
const StatsPage = lazy(() => import('./pages/Stats/Stats'));

function App() {
  return (
    <Router>
      <Routes>
        {/* 登录和注册页面，不需要布局 */}
        <Route path="/login" element={<Login />} />
        <Route path="/register" element={<Register />} />
        
        {/* 受保护的路由，需要布局 */}
        <Route element={<ProtectedRoute />}>
          <Route element={
            <div className="flex h-screen bg-light">
              <Sidebar />
              <div className="flex-1 flex flex-col overflow-hidden md:ml-64">
                <Header />
                <main className="flex-1 overflow-y-auto p-6 md:p-8">
                  <div className="max-w-7xl mx-auto">
                    <Suspense fallback={<div className="flex items-center justify-center h-32">加载中...</div>}>
                      <Outlet />
                    </Suspense>
                  </div>
                </main>
                <Footer />
              </div>
            </div>
          }>
            <Route path="/" element={<AppPage />} />
            <Route path="/app" element={<AppPage />} />
            <Route path="/courses" element={<CoursesPage />} />
            <Route path="/profile" element={<ProfilePage />} />
            <Route path="/programming" element={<ProgrammingPage />} />
            <Route path="/stats" element={<StatsPage />} />
          </Route>
        </Route>
      </Routes>
    </Router>
  );
}

export default App;
