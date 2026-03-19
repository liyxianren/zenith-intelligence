import React, { useState } from 'react';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';

interface Module {
  id: string;
  title: string;
  content: string;
}

interface Course {
  id: string;
  title: string;
  description: string;
  modules: Module[];
  progress?: number;
  thumbnail?: string;
}

const CoursesPage: React.FC = () => {
  // 模拟课程数据
  const courses: Course[] = [
    {
      id: '1',
      title: '数学基础',
      description: '包含代数、几何、微积分等基础数学知识',
      progress: 65,
      thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=mathematics%20education%20concept%20with%20formulas%20and%20geometry&image_size=landscape_16_9',
      modules: [
        { id: '1-1', title: '代数基础', content: '变量、方程、不等式等基本概念' },
        { id: '1-2', title: '几何入门', content: '平面几何和立体几何基础' },
        { id: '1-3', title: '微积分初步', content: '导数和积分的基本概念' },
      ],
    },
    {
      id: '2',
      title: '物理入门',
      description: '力学、热学、电磁学等物理学基础',
      progress: 30,
      thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=physics%20education%20concept%20with%20science%20equipment&image_size=landscape_16_9',
      modules: [
        { id: '2-1', title: '牛顿运动定律', content: '牛顿三大定律及其应用' },
        { id: '2-2', title: '能量守恒', content: '动能、势能和能量守恒定律' },
        { id: '2-3', title: '电磁学基础', content: '电场、磁场和电磁感应' },
      ],
    },
    {
      id: '3',
      title: '编程基础',
      description: 'Python、JavaScript等编程语言入门',
      progress: 80,
      thumbnail: 'https://trae-api-cn.mchost.guru/api/ide/v1/text_to_image?prompt=programming%20education%20concept%20with%20code%20and%20laptop&image_size=landscape_16_9',
      modules: [
        { id: '3-1', title: 'Python基础', content: '变量、数据类型、控制流' },
        { id: '3-2', title: 'JavaScript入门', content: '前端开发基础' },
        { id: '3-3', title: '算法基础', content: '常见算法和数据结构' },
      ],
    },
  ];

  const [searchTerm, setSearchTerm] = useState('');
  const [selectedCourse, setSelectedCourse] = useState<Course | null>(null);

  const filteredCourses = courses.filter((course) =>
    course.title.toLowerCase().includes(searchTerm.toLowerCase()) ||
    course.description.toLowerCase().includes(searchTerm.toLowerCase())
  );

  const handleCourseClick = (course: Course) => {
    setSelectedCourse(selectedCourse?.id === course.id ? null : course);
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">我的课程</h1>
        <p className="text-gray-600">浏览和管理你的学习课程</p>
      </div>
      
      {/* 搜索和添加按钮 */}
      <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4">
        <div className="relative w-full sm:w-80">
          <Input
            placeholder="搜索课程..."
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            prefix={
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
              </svg>
            }
          />
        </div>
        <Button variant="primary" size="md">
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6v6m0 0v6m0-6h6m-6 0H6" />
          </svg>
          添加课程
        </Button>
      </div>
      
      {/* 课程列表 */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
        {filteredCourses.map((course) => (
          <Card key={course.id} shadow="lg" hover={true} className="overflow-hidden transition-all duration-300">
            <div className="cursor-pointer" onClick={() => handleCourseClick(course)}>
              {/* 课程封面 */}
              {course.thumbnail && (
                <div className="h-48 overflow-hidden relative">
                  <img 
                    src={course.thumbnail} 
                    alt={course.title} 
                    className="w-full h-full object-cover transition-transform duration-500 hover:scale-105"
                  />
                  <div className="absolute top-3 right-3 bg-white/90 backdrop-blur-sm rounded-full px-3 py-1 text-xs font-medium text-gray-800 shadow-sm">
                    {course.progress}% 完成
                  </div>
                </div>
              )}
              
              {/* 课程信息 */}
              <div className="p-6">
                <div className="flex justify-between items-start mb-4">
                  <h3 className="text-xl font-semibold text-gray-900">{course.title}</h3>
                  <button className="text-gray-500 hover:text-primary transition-colors p-2 rounded-full hover:bg-gray-50">
                    {selectedCourse?.id === course.id ? (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                      </svg>
                    ) : (
                      <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 5l7 7-7 7" />
                      </svg>
                    )}
                  </button>
                </div>
                
                <p className="text-gray-600 mb-4 line-clamp-2">{course.description}</p>
                
                {/* 进度条 */}
                <div className="mb-4">
                  <div className="flex justify-between text-sm text-gray-500 mb-1.5">
                    <span>学习进度</span>
                    <span>{course.progress}%</span>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2.5 overflow-hidden">
                    <div 
                      className="bg-primary h-full rounded-full transition-all duration-700 ease-out"
                      style={{ width: `${course.progress}%` }}
                    ></div>
                  </div>
                </div>
                
                <div className="flex justify-between items-center">
                  <span className="text-sm text-gray-500">{course.modules.length} 个模块</span>
                  <Button variant="primary" size="sm">
                    继续学习
                  </Button>
                </div>
              </div>
            </div>
            
            {/* 课程模块详情 */}
            {selectedCourse?.id === course.id && (
              <div className="px-6 pb-6 pt-4 border-t border-gray-200 animate-slide-in">
                <h4 className="font-semibold text-gray-800 mb-4">课程模块</h4>
                <div className="space-y-3">
                  {course.modules.map((module, index) => (
                    <div key={module.id} className="p-4 bg-gray-50 rounded-lg hover:bg-gray-100 transition-colors">
                      <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-full bg-primary/10 text-primary flex items-center justify-center font-medium">
                          {index + 1}
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-900">{module.title}</h5>
                          <p className="text-sm text-gray-600 mt-1">{module.content}</p>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            )}
          </Card>
        ))}
      </div>
    </div>
  );
};

export default CoursesPage;