import React, { useRef, useState } from 'react';
import axios from 'axios';
import Card from '../../components/ui/Card';
import Button from '../../components/ui/Button';
import Input from '../../components/ui/Input';
import { api } from '../../services/api';

type SupportedLanguage = 'python' | 'c' | 'javascript' | 'java' | 'cpp';
type ResultMode = 'plain' | 'markdown';

interface ExecutionResult {
  success: boolean;
  error?: string;
  data?: {
    stdout: string;
    stderr: string;
    returnCode: number;
    language: string;
  };
}

const starterCode: Record<SupportedLanguage, string> = {
  python: "print('Hello, World!')",
  c: '#include <stdio.h>\n\nint main() {\n  printf("Hello, World!\\n");\n  return 0;\n}',
  javascript: "console.log('Hello, World!');",
  java: 'public class Main {\n    public static void main(String[] args) {\n        System.out.println("Hello, World!");\n    }\n}',
  cpp: '#include <iostream>\n\nint main() {\n    std::cout << "Hello, World!" << std::endl;\n    return 0;\n}',
};

const languages: Array<{ id: SupportedLanguage; name: string; icon: string }> = [
  { id: 'python', name: 'Python', icon: '🐍' },
  { id: 'c', name: 'C', icon: '⚙️' },
  { id: 'javascript', name: 'JavaScript', icon: '📜' },
  { id: 'java', name: 'Java', icon: '☕' },
  { id: 'cpp', name: 'C++', icon: '🧩' },
];

const INDENT_UNIT = '    ';

function escapeHtml(text: string) {
  return text
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/"/g, '&quot;')
    .replace(/'/g, '&#39;');
}

function renderInlineMarkdown(text: string) {
  let html = escapeHtml(text);
  html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');
  html = html.replace(
    /\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>',
  );
  html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
  html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
  html = html.replace(/~~([^~\n]+)~~/g, '<del>$1</del>');
  return html;
}

function renderMarkdownBlock(
  block: string,
  codeBlocks: Array<{ lang: string; code: string }>,
) {
  const codeTokenMatch = block.match(/^@@CODE_BLOCK_(\d+)@@$/);
  if (codeTokenMatch) {
    const codeBlock = codeBlocks[Number(codeTokenMatch[1])];
    const languageClass = codeBlock.lang ? ` class="language-${escapeHtml(codeBlock.lang)}"` : '';
    return `<pre><code${languageClass}>${codeBlock.code}</code></pre>`;
  }

  const lines = block.split('\n').map((line) => line.replace(/\s+$/, ''));

  if (lines.every((line) => /^[-*+]\s+/.test(line.trim()))) {
    const items = lines
      .map((line) => line.trim().replace(/^[-*+]\s+/, ''))
      .map((item) => `<li>${renderInlineMarkdown(item)}</li>`)
      .join('');
    return `<ul>${items}</ul>`;
  }

  if (lines.every((line) => /^\d+\.\s+/.test(line.trim()))) {
    const items = lines
      .map((line) => line.trim().replace(/^\d+\.\s+/, ''))
      .map((item) => `<li>${renderInlineMarkdown(item)}</li>`)
      .join('');
    return `<ol>${items}</ol>`;
  }

  const headingMatch = block.match(/^(#{1,6})\s+(.+)$/);
  if (headingMatch) {
    const level = headingMatch[1].length;
    return `<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`;
  }

  if (lines.every((line) => /^>\s?/.test(line.trim()))) {
    const quote = lines
      .map((line) => line.trim().replace(/^>\s?/, ''))
      .map((line) => renderInlineMarkdown(line))
      .join('<br>');
    return `<blockquote>${quote}</blockquote>`;
  }

  return `<p>${lines.map((line) => renderInlineMarkdown(line)).join('<br>')}</p>`;
}

function renderMarkdown(text: string) {
  const source = String(text ?? '').replace(/\r\n?/g, '\n').trim();
  if (!source) {
    return '';
  }

  const codeBlocks: Array<{ lang: string; code: string }> = [];
  const withCodeTokens = source.replace(
    /```([a-zA-Z0-9_-]+)?\n?([\s\S]*?)```/g,
    (_, lang = '', code = '') => {
      const token = `@@CODE_BLOCK_${codeBlocks.length}@@`;
      codeBlocks.push({
        lang: String(lang).trim(),
        code: escapeHtml(String(code).replace(/\n$/, '')),
      });
      return token;
    },
  );

  return withCodeTokens
    .split(/\n{2,}/)
    .map((block) => renderMarkdownBlock(block, codeBlocks))
    .join('');
}

function applyEditorIndentation(
  value: string,
  selectionStart: number,
  selectionEnd: number,
  isOutdent: boolean,
) {
  const lineStart = value.lastIndexOf('\n', Math.max(selectionStart - 1, 0)) + 1;
  const hasSelection = selectionStart !== selectionEnd;

  if (!isOutdent && !hasSelection) {
    return {
      value: value.slice(0, selectionStart) + INDENT_UNIT + value.slice(selectionEnd),
      selectionStart: selectionStart + INDENT_UNIT.length,
      selectionEnd: selectionStart + INDENT_UNIT.length,
    };
  }

  const block = value.slice(lineStart, selectionEnd);
  const lines = block.split('\n');

  if (!isOutdent) {
    const updatedBlock = lines.map((line) => INDENT_UNIT + line).join('\n');
    return {
      value: value.slice(0, lineStart) + updatedBlock + value.slice(selectionEnd),
      selectionStart: selectionStart + INDENT_UNIT.length,
      selectionEnd: selectionEnd + INDENT_UNIT.length * lines.length,
    };
  }

  let removedFromFirstLine = 0;
  let totalRemoved = 0;
  const updatedLines = lines.map((line, index) => {
    let removed = 0;
    let updatedLine = line;

    if (updatedLine.startsWith(INDENT_UNIT)) {
      updatedLine = updatedLine.slice(INDENT_UNIT.length);
      removed = INDENT_UNIT.length;
    } else if (updatedLine.startsWith('\t')) {
      updatedLine = updatedLine.slice(1);
      removed = 1;
    } else {
      const leadingSpaces = updatedLine.match(/^ {1,4}/);
      if (leadingSpaces) {
        removed = leadingSpaces[0].length;
        updatedLine = updatedLine.slice(removed);
      }
    }

    if (index === 0) {
      removedFromFirstLine = removed;
    }
    totalRemoved += removed;
    return updatedLine;
  });

  if (!totalRemoved) {
    return {
      value,
      selectionStart,
      selectionEnd,
    };
  }

  const nextSelectionStart = Math.max(lineStart, selectionStart - removedFromFirstLine);

  return {
    value: value.slice(0, lineStart) + updatedLines.join('\n') + value.slice(selectionEnd),
    selectionStart: nextSelectionStart,
    selectionEnd: Math.max(nextSelectionStart, selectionEnd - totalRemoved),
  };
}

const ProgrammingPage: React.FC = () => {
  const [code, setCode] = useState(starterCode.python);
  const [isLoading, setIsLoading] = useState(false);
  const [result, setResult] = useState('');
  const [resultMode, setResultMode] = useState<ResultMode>('plain');
  const [generatePrompt, setGeneratePrompt] = useState('');
  const [activeTab, setActiveTab] = useState<'editor' | 'generator'>('editor');
  const [selectedLanguage, setSelectedLanguage] = useState<SupportedLanguage>('python');
  const editorRef = useRef<HTMLTextAreaElement | null>(null);

  const selectLanguage = (language: SupportedLanguage) => {
    setSelectedLanguage(language);
    setCode(starterCode[language]);
  };

  const handleEditorKeyDown = (event: React.KeyboardEvent<HTMLTextAreaElement>) => {
    if (event.key !== 'Tab') {
      return;
    }

    event.preventDefault();

    const target = event.currentTarget;
    const nextState = applyEditorIndentation(
      code,
      target.selectionStart,
      target.selectionEnd,
      event.shiftKey,
    );

    setCode(nextState.value);

    requestAnimationFrame(() => {
      editorRef.current?.setSelectionRange(nextState.selectionStart, nextState.selectionEnd);
    });
  };

  const handleExecute = async () => {
    if (!code.trim()) {
      setResultMode('plain');
      setResult('请输入代码后再运行');
      return;
    }

    setIsLoading(true);
    setResult('');
    setResultMode('plain');

    try {
      const response = await api.post<ExecutionResult>('/api/programming/execute', {
        code,
        language: selectedLanguage,
      });
      const payload = response.data;

      if (!payload.success || !payload.data) {
        setResult(payload.error || '执行失败');
        return;
      }

      const parts: string[] = [];
      if (payload.data.stdout.trim()) {
        parts.push(payload.data.stdout.trimEnd());
      }
      if (payload.data.stderr.trim()) {
        parts.push(`[错误输出]\n${payload.data.stderr.trimEnd()}`);
      }
      if (payload.data.returnCode !== 0) {
        parts.push(`[进程退出码: ${payload.data.returnCode}]`);
      }

      setResult(parts.join('\n\n') || '程序执行完成，无输出');
    } catch (error) {
      if (axios.isAxiosError<{ error?: string }>(error)) {
        setResult(error.response?.data?.error || error.message || '执行失败');
      } else {
        setResult('执行失败');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleExplain = async () => {
    setIsLoading(true);
    setResult('');
    setResultMode('plain');

    try {
      const response = await api.post<{
        success: boolean;
        error?: string;
        data?: {
          explanation: string;
          language: string;
        };
      }>('/api/programming/explain', {
        code,
        language: selectedLanguage,
      });

      if (!response.data.success || !response.data.data) {
        setResult(response.data.error || '解释失败');
        return;
      }

      setResultMode('markdown');
      setResult(response.data.data.explanation || '未返回解释内容');
    } catch (error) {
      if (axios.isAxiosError<{ error?: string }>(error)) {
        setResult(error.response?.data?.error || error.message || '解释失败');
      } else {
        setResult('解释失败');
      }
    } finally {
      setIsLoading(false);
    }
  };

  const handleGenerate = async () => {
    if (!generatePrompt.trim()) return;
    
    setIsLoading(true);
    setResult('');
    setResultMode('plain');

    try {
      const response = await api.post<{
        success: boolean;
        error?: string;
        data?: {
          code: string;
          language: string;
        };
      }>('/api/programming/generate', {
        description: generatePrompt,
        language: selectedLanguage,
      });

      if (!response.data.success || !response.data.data) {
        setResult(response.data.error || '代码生成失败');
        return;
      }

      const generatedCode = response.data.data.code || starterCode[selectedLanguage];
      setCode(generatedCode);
      setResult('代码生成成功！');
    } catch (error) {
      if (axios.isAxiosError<{ error?: string }>(error)) {
        setResult(error.response?.data?.error || error.message || '代码生成失败');
      } else {
        setResult('代码生成失败');
      }
    } finally {
      setIsLoading(false);
    }
  };

  return (
    <div className="space-y-8 animate-fade-in">
      {/* 页面标题 */}
      <div>
        <h1 className="text-3xl font-bold text-gray-900 mb-2">编程助手</h1>
        <p className="text-gray-600">编写、执行和生成代码，提升你的编程技能</p>
      </div>
      
      {/* 标签切换 */}
      <div className="bg-white rounded-xl shadow-sm p-1 border border-gray-100 inline-block">
        <Button
          variant={activeTab === 'editor' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('editor')}
          className="rounded-lg"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
          </svg>
          代码编辑器
        </Button>
        <Button
          variant={activeTab === 'generator' ? 'primary' : 'outline'}
          onClick={() => setActiveTab('generator')}
          className="rounded-lg"
        >
          <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
          </svg>
          代码生成器
        </Button>
      </div>

      {/* 编辑器内容 */}
      {activeTab === 'editor' ? (
        <Card shadow="lg" padding="lg">
          <div className="space-y-6">
            {/* 语言选择 */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-3 sm:space-y-0">
              <label className="text-sm font-semibold text-gray-700">编程语言：</label>
              <div className="flex flex-wrap gap-2">
                {languages.map((lang) => (
                  <button
                    key={lang.id}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedLanguage === lang.id ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    onClick={() => selectLanguage(lang.id)}
                  >
                    <span>{lang.icon}</span>
                    {lang.name}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 代码编辑器 */}
            <div>
              <div className="flex justify-between items-center mb-3">
                <h3 className="text-lg font-semibold text-gray-800">代码编辑器</h3>
                <Button variant="outline" size="sm" onClick={() => setCode(starterCode[selectedLanguage])}>
                  清空
                </Button>
              </div>
              <textarea
                ref={editorRef}
                value={code}
                onChange={(e) => setCode(e.target.value)}
                onKeyDown={handleEditorKeyDown}
                className="w-full px-4 py-4 border border-gray-300 rounded-xl focus:outline-none focus:ring-2 focus:ring-primary focus:border-primary font-mono text-sm bg-gray-50 resize-none transition-all duration-300"
                rows={10}
              />
            </div>
            
            {/* 操作按钮 */}
            <div className="flex flex-wrap gap-3">
              <Button onClick={handleExecute} loading={isLoading} size="md">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14.752 11.168l-3.197-2.132A1 1 0 0010 9.87v4.263a1 1 0 001.555.832l3.197-2.132a1 1 0 000-1.664z" />
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                执行代码
              </Button>
              <Button variant="secondary" onClick={handleExplain} loading={isLoading} size="md">
                <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
                解释代码
              </Button>
            </div>
          </div>
        </Card>
      ) : (
        <Card shadow="lg" padding="lg">
          <div className="space-y-6">
            {/* 语言选择 */}
            <div className="flex flex-col sm:flex-row sm:items-center sm:space-x-4 space-y-3 sm:space-y-0">
              <label className="text-sm font-semibold text-gray-700">目标语言：</label>
              <div className="flex flex-wrap gap-2">
                {languages.map((lang) => (
                  <button
                    key={lang.id}
                    className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${selectedLanguage === lang.id ? 'bg-primary text-white' : 'bg-gray-100 text-gray-700 hover:bg-gray-200'}`}
                    onClick={() => selectLanguage(lang.id)}
                  >
                    <span>{lang.icon}</span>
                    {lang.name}
                  </button>
                ))}
              </div>
            </div>
            
            {/* 生成提示输入 */}
            <div>
              <h3 className="text-lg font-semibold text-gray-800 mb-3">输入代码生成需求</h3>
              <Input
                placeholder="例如：创建一个计算斐波那契数列的函数"
                value={generatePrompt}
                onChange={(e) => setGeneratePrompt(e.target.value)}
                fullWidth

              />
              <p className="text-sm text-gray-500 mt-2">
                详细描述你的需求，AI将为你生成相应的代码
              </p>
            </div>
            
            {/* 生成按钮 */}
            <Button onClick={handleGenerate} loading={isLoading} size="lg" fullWidth>
              <svg xmlns="http://www.w3.org/2000/svg" className="h-5 w-5 mr-2" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 6V4m0 2a2 2 0 100 4m0-4a2 2 0 110 4m-6 8a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4m6 6v10m6-2a2 2 0 100-4m0 4a2 2 0 110-4m0 4v2m0-6V4" />
              </svg>
              生成代码
            </Button>
          </div>
        </Card>
      )}

      {/* 结果显示 */}
      {result && (
        <Card shadow="lg" padding="lg" className="animate-slide-in">
          <h3 className="text-lg font-semibold text-gray-800 mb-4">执行结果</h3>
          {resultMode === 'markdown' ? (
            <div
              className="text-sm leading-7 text-gray-800 [&_h1]:mb-3 [&_h1]:text-xl [&_h1]:font-bold [&_h2]:mb-3 [&_h2]:text-lg [&_h2]:font-semibold [&_h3]:mb-2 [&_h3]:text-base [&_h3]:font-semibold [&_p]:mb-3 [&_ul]:mb-3 [&_ul]:list-disc [&_ul]:pl-5 [&_ol]:mb-3 [&_ol]:list-decimal [&_ol]:pl-5 [&_blockquote]:mb-3 [&_blockquote]:border-l-4 [&_blockquote]:border-emerald-500 [&_blockquote]:pl-3 [&_blockquote]:text-slate-600 [&_pre]:mb-3 [&_pre]:overflow-x-auto [&_pre]:rounded-xl [&_pre]:bg-slate-950 [&_pre]:p-4 [&_pre]:text-slate-100 [&_code]:rounded [&_code]:bg-indigo-50 [&_code]:px-1.5 [&_code]:py-0.5 [&_code]:font-mono [&_code]:text-xs [&_code]:text-indigo-900 [&_pre_code]:bg-transparent [&_pre_code]:p-0 [&_pre_code]:text-slate-100 [&_a]:text-blue-600 [&_a]:underline"
              dangerouslySetInnerHTML={{ __html: renderMarkdown(result) }}
            />
          ) : (
            <pre className="whitespace-pre-wrap font-mono text-sm bg-gray-50 p-4 rounded-xl border border-gray-200">{result}</pre>
          )}
        </Card>
      )}
    </div>
  );
};

export default ProgrammingPage;
