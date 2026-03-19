import React, { useState, useRef } from 'react';
import Button from '../ui/Button';

interface ProblemInputProps {
  onSubmit: (type: 'text' | 'image', content: string) => void;
  isLoading: boolean;
}

const ProblemInput: React.FC<ProblemInputProps> = ({ onSubmit, isLoading }) => {
  const [input, setInput] = useState('');
  const [image, setImage] = useState<string | null>(null);
  const [inputType, setInputType] = useState<'text' | 'image'>('text');
  const fileInputRef = useRef<HTMLInputElement>(null);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (inputType === 'text' && input.trim()) {
      onSubmit('text', input);
      setInput('');
    } else if (inputType === 'image' && image) {
      onSubmit('image', image);
      setImage(null);
    }
  };

  const handleImageUpload = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      const reader = new FileReader();
      reader.onloadend = () => {
        setImage(reader.result as string);
      };
      reader.readAsDataURL(file);
    }
  };

  const handleClear = () => {
    setInput('');
    setImage(null);
  };

  return (
    <div className="space-y-5">
      <div className="flex space-x-3">
        <Button
          variant={inputType === 'text' ? 'primary' : 'outline'}
          onClick={() => setInputType('text')}
        >
          文本输入
        </Button>
        <Button
          variant={inputType === 'image' ? 'primary' : 'outline'}
          onClick={() => setInputType('image')}
        >
          图片输入
        </Button>
      </div>

      <form onSubmit={handleSubmit} className="space-y-5">
        {inputType === 'text' ? (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              输入问题
            </label>
            <textarea
              value={input}
              onChange={(e) => setInput(e.target.value)}
              className="w-full px-4 py-3 border border-gray-200 rounded-lg focus:outline-none focus:ring-2 focus:ring-primary/50 focus:border-primary transition-all duration-300 resize-none"
              rows={4}
              placeholder="请输入你的问题..."
            />
          </div>
        ) : (
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              上传图片
            </label>
            <div className="border-2 border-dashed border-gray-200 rounded-lg p-8 text-center hover:border-primary/50 transition-colors duration-300">
              {image ? (
                <div className="space-y-4">
                  <img src={image} alt="预览" className="max-h-60 mx-auto rounded-lg shadow-sm" />
                  <Button variant="outline" size="sm" onClick={() => setImage(null)}>
                    更换图片
                  </Button>
                </div>
              ) : (
                <div className="space-y-4">
                  <svg xmlns="http://www.w3.org/2000/svg" className="h-16 w-16 text-gray-400 mx-auto" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M7 16a4 4 0 01-.88-7.903A5 5 0 1115.9 6L16 6a5 5 0 011 9.9M15 13l-3-3m0 0l-3 3m3-3v12" />
                  </svg>
                  <p className="text-sm text-gray-600">
                    点击或拖拽图片到此处上传
                  </p>
                  <input
                    ref={fileInputRef}
                    type="file"
                    accept="image/*"
                    onChange={handleImageUpload}
                    className="hidden"
                  />
                  <Button variant="outline" onClick={() => fileInputRef.current?.click()}>
                    选择图片
                  </Button>
                </div>
              )}
            </div>
          </div>
        )}

        <div className="flex space-x-3">
          <Button type="submit" loading={isLoading}>
            提交
          </Button>
          <Button variant="outline" onClick={handleClear}>
            清空
          </Button>
        </div>
      </form>
    </div>
  );
};

export default ProblemInput;