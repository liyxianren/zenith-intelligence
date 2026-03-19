import React from 'react';
import Card from '../ui/Card';

interface Problem {
  id: string;
  content: string;
  type: 'text' | 'image';
  solution: string;
  timestamp: number;
}

interface HistoryListProps {
  history: Problem[];
  onSelectHistory: (problem: Problem) => void;
}

const HistoryList: React.FC<HistoryListProps> = ({ history, onSelectHistory }) => {
  const formatDate = (timestamp: number) => {
    return new Date(timestamp).toLocaleString();
  };

  return (
    <Card header={<h3 className="text-lg font-semibold text-dark">历史记录</h3>}>
      {history.length === 0 ? (
        <p className="text-gray-600 py-8 text-center">暂无历史记录</p>
      ) : (
        <div className="space-y-4 max-h-80 overflow-y-auto pr-2">
          {history.map((item) => (
            <div
              key={item.id}
              className="p-4 border border-gray-200 rounded-lg hover:bg-gray-50 cursor-pointer transition-all duration-300 hover:shadow-sm"
              onClick={() => onSelectHistory(item)}
            >
              <div className="flex justify-between items-start">
                <div className="flex-1">
                  <div className="text-sm font-medium text-dark truncate">
                    {item.type === 'text' ? item.content.substring(0, 50) + (item.content.length > 50 ? '...' : '') : '图片问题'}
                  </div>
                  <div className="text-xs text-gray-500 mt-2">
                    {formatDate(item.timestamp)}
                  </div>
                </div>
                <div className="ml-3 text-xs px-3 py-1 bg-primary/10 text-primary rounded-full font-medium">
                  {item.type === 'text' ? '文本' : '图片'}
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </Card>
  );
};

export default HistoryList;