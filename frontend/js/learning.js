/**
 * AI Learning Assistant - Learning Workspace Logic
 * Handles the dual-pane UI: Markdown reading on left, Code Playground on right.
 */

const LearningApp = {
    courseId: null,
    currentCourse: null,
    currentLessonId: null,
    editor: null,
    cacheKey: 'ai_learning_current_course',
    usesCachedCourse: false,

    init() {
        // Parse courseId from URL query string
        const urlParams = new URLSearchParams(window.location.search);
        this.courseId = urlParams.get('course_id');

        if (!this.courseId) {
            alert('获取课程信息失败，请返回重试！');
            window.location.href = 'courses.html';
            return;
        }

        this.initEditor();
        this.bindEvents();
        this.loadCourseData();
    },

    initEditor() {
        const textarea = document.getElementById('code-editor');
        if (!textarea) return;

        this.editor = CodeMirror.fromTextArea(textarea, {
            mode: 'python',
            theme: 'dracula',
            lineNumbers: true,
            indentUnit: 4,
            tabSize: 4,
            indentWithTabs: false,
            lineWrapping: true,
            matchBrackets: true,
            autoCloseBrackets: true
        });
    },

    bindEvents() {
        const runBtn = document.getElementById('run-code-btn');
        if (runBtn) {
            runBtn.addEventListener('click', () => {
                this.executeCode();
            });
        }
    },

    cacheCurrentCourse() {
        if (!this.currentCourse) return;

        try {
            sessionStorage.setItem(this.cacheKey, JSON.stringify({
                courseId: this.currentCourse.id,
                cachedAt: Date.now(),
                course: this.currentCourse
            }));
        } catch (error) {
            console.warn('缓存课程信息失败:', error);
        }
    },

    getCachedCourse() {
        try {
            const raw = sessionStorage.getItem(this.cacheKey);
            if (!raw) return null;

            const payload = JSON.parse(raw);
            const cachedCourse = payload?.course;
            const cachedCourseId = payload?.courseId ?? cachedCourse?.id;

            if (!cachedCourse || String(cachedCourseId) !== String(this.courseId)) {
                return null;
            }

            return cachedCourse;
        } catch (error) {
            console.warn('读取课程缓存失败:', error);
            return null;
        }
    },

    renderLoadError(message) {
        document.getElementById('lesson-content').innerHTML = `
            <div class="loader" style="color: red;">
                <p>${message}</p>
                <p><a href="courses.html" style="color: inherit;">返回课程中心</a></p>
            </div>`;
    },

    openFirstLesson() {
        if (this.currentCourse?.chapters?.length > 0) {
            const firstChapter = this.currentCourse.chapters[0];
            if (firstChapter.lessons?.length > 0) {
                this.loadLesson(firstChapter.lessons[0].id);
                return true;
            }
        }

        document.getElementById('lesson-content').innerHTML = `
            <div class="loader">
                 <p>课程暂时没有上架课时内容。</p>
            </div>`;
        return false;
    },

    loadCachedCourseData(message) {
        const cachedCourse = this.getCachedCourse();
        if (!cachedCourse) {
            return false;
        }

        this.currentCourse = cachedCourse;
        this.usesCachedCourse = true;
        this.renderNavigation();
        this.openFirstLesson();
        console.warn(message);
        return true;
    },

    getLocalLessonPayload(lessonId, reason = '') {
        const targetLessonId = parseInt(lessonId, 10);

        if (!this.currentCourse?.chapters?.length) {
            return null;
        }

        for (const chapter of this.currentCourse.chapters) {
            const lesson = (chapter.lessons || []).find(item => parseInt(item.id, 10) === targetLessonId);
            if (lesson) {
                const notice = reason || (this.usesCachedCourse
                    ? '当前为本地预览模式，服务器课程内容暂未同步。'
                    : '服务器课时内容暂不可用，已切换到本地预览。');

                const content = [
                    `> ${notice}`,
                    '',
                    `## 课程：${this.currentCourse.name}`,
                    `## 章节：${chapter.name}`,
                    '',
                    `${lesson.description || chapter.description || this.currentCourse.description || '课程内容准备中。'}`,
                    '',
                    '### 当前学习建议',
                    '- 先阅读左侧章节目录，按顺序完成学习。',
                    '- 如右侧代码实验室已开启，可直接运行示例代码。',
                    '- 若需要完整教案内容，请补齐后端课程种子数据。'
                ].join('\n');

                return {
                    ...lesson,
                    content
                };
            }
        }

        return null;
    },

    renderCachedLesson(lessonId, reason = '') {
        const lesson = this.getLocalLessonPayload(lessonId, reason);
        if (!lesson) {
            return false;
        }

        this.renderLessonContent(lesson);
        return true;
    },

    hasRichMarkdownRenderer() {
        return typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined';
    },

    sanitizeRenderedHtml(html) {
        if (!this.hasRichMarkdownRenderer()) {
            return html;
        }

        return DOMPurify.sanitize(html, {
            USE_PROFILES: { html: true }
        });
    },

    renderMarkdown(text) {
        const source = String(text ?? '').replace(/\r\n?/g, '\n').trim();
        if (!source) {
            return '';
        }

        marked.setOptions({
            gfm: true,
            breaks: true,
            langPrefix: 'hljs language-',
            highlight(code, lang) {
                const language = hljs.getLanguage(lang) ? lang : 'plaintext';
                return hljs.highlight(code, { language }).value;
            }
        });

        return this.sanitizeRenderedHtml(marked.parse(source));
    },

    buildLessonHtml(lesson) {
        const rawMarkdown = String(lesson.content || '').trim();
        const hasMarkdownTitle = /^#\s+.+/m.test(rawMarkdown);

        if (rawMarkdown) {
            const markdownHtml = this.renderMarkdown(rawMarkdown);
            return hasMarkdownTitle
                ? `<article class="markdown-content">${markdownHtml}</article>`
                : `<article class="markdown-content"><h1>${lesson.name}</h1>${markdownHtml}</article>`;
        }

        if (lesson.content_html) {
            const html = this.sanitizeRenderedHtml(lesson.content_html);
            const hasHtmlTitle = /<h1[\s>]/i.test(html);
            return hasHtmlTitle
                ? `<article class="markdown-content">${html}</article>`
                : `<article class="markdown-content"><h1>${lesson.name}</h1>${html}</article>`;
        }

        return `<article class="markdown-content"><h1>${lesson.name}</h1><p>该课时暂无内容。</p></article>`;
    },

    async loadCourseData() {
        try {
            const response = await UserManager.fetchApi(`/api/course/${this.courseId}`);
            if (response.status === 404) {
                if (this.loadCachedCourseData('服务器中未找到该课程，已切换到本地预览模式。')) {
                    return;
                }

                this.renderLoadError('该课程当前未同步到服务器，请返回课程中心重试。');
                return;
            }

            const result = await response.json();
            if (result.success) {
                this.currentCourse = result.data;
                this.usesCachedCourse = false;
                this.cacheCurrentCourse();
                this.renderNavigation();
                this.openFirstLesson();
            } else {
                throw new Error(result.error);
            }
        } catch (error) {
            console.error('加载课程数据失败:', error);
            if (this.loadCachedCourseData('网络异常，已切换到本地预览模式。')) {
                return;
            }

            this.renderLoadError('网络错误，无法加载课程大纲。请检查服务运行状态。');
        }
    },

    renderNavigation() {
        document.getElementById('top-course-title').textContent = this.currentCourse.name;

        const dirHtml = this.currentCourse.chapters.map((chapter, index) => {
            const lessonsHtml = (chapter.lessons || []).map(lesson => `
                <div class="menu-lesson" data-lesson-id="${lesson.id}" onclick="LearningApp.loadLesson(${lesson.id})">
                    ${lesson.name}
                </div>
            `).join('');

            return `
                <div class="menu-chapter-group">
                    <div class="menu-chapter">第${index + 1}章: ${chapter.name}</div>
                    <div class="menu-lessons-list">${lessonsHtml}</div>
                </div>
            `;
        }).join('');

        document.getElementById('course-directory').innerHTML = dirHtml;
    },

    async loadLesson(lessonId) {
        this.currentLessonId = lessonId;

        // Highlight active menu item
        document.querySelectorAll('.menu-lesson').forEach(el => {
            el.classList.remove('active');
            if (parseInt(el.dataset.lessonId) === lessonId) {
                el.classList.add('active');
            }
        });

        const mainContent = document.getElementById('lesson-content');
        mainContent.innerHTML = `
            <div class="loader">
                <svg width="40" height="40" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-dasharray="15" stroke-dashoffset="15" class="animate-spin" style="margin-bottom: 15px; animation: spin 2s linear infinite;">
                    <circle cx="12" cy="12" r="10" />
                </svg>
                <p>读取教案中...</p>
            </div>`;

        try {
            const response = await UserManager.fetchApi(`/api/course/lesson/${lessonId}`);
            if (response.status === 404) {
                if (this.renderCachedLesson(lessonId, '当前课时内容尚未同步到服务器，已展示本地预览。')) {
                    return;
                }

                mainContent.innerHTML = '<p style="color:red; padding: 20px;">读取课时失败：课程内容不存在。</p>';
                return;
            }

            const result = await response.json();

            if (result.success) {
                this.renderLessonContent(result.data);
            } else if (this.renderCachedLesson(lessonId, `读取课时失败：${result.error || '服务器返回异常'}，已展示本地预览。`)) {
                return;
            } else {
                mainContent.innerHTML = `<p style="color:red; padding: 20px;">读取课时失败: ${result.error}</p>`;
            }
        } catch (error) {
            console.error('加载课时内容失败:', error);
            if (this.renderCachedLesson(lessonId, '网络异常，已展示本地预览内容。')) {
                return;
            }

            mainContent.innerHTML = '<p style="color:red; padding: 20px;">发生错误，请稍后重试。</p>';
        }
    },

    renderLessonContent(lesson) {
        const mainContent = document.getElementById('lesson-content');
        mainContent.innerHTML = this.buildLessonHtml(lesson);

        // Display code playground if course is a programming language course
        const subject = this.currentCourse.subject;
        const codePlayground = document.getElementById('code-playground');

        if (subject === 'programming' || this.currentCourse.name.includes('Python') || this.currentCourse.name.includes('C ')) {
            codePlayground.style.display = 'flex';

            // Set mode
            if (this.currentCourse.name.includes('C ')) {
                this.editor.setOption('mode', 'text/x-csrc');
                if (!this.editor.getValue()) {
                    this.editor.setValue('#include <stdio.h>\n\nint main() {\n    printf("Hello World!");\n    return 0;\n}');
                }
            } else {
                this.editor.setOption('mode', 'python');
                if (!this.editor.getValue()) {
                    this.editor.setValue('print("Hello Playground!")');
                }
            }
        } else {
            codePlayground.style.display = 'none';
        }
    },

    async executeCode() {
        if (!this.editor) return;

        const code = this.editor.getValue().trim();
        if (!code) return;

        const btn = document.getElementById('run-code-btn');
        const consoleOutput = document.getElementById('console-output');
        const statusEl = document.getElementById('run-status');

        btn.disabled = true;
        btn.textContent = '运行中...';
        consoleOutput.innerHTML = '';
        consoleOutput.classList.remove('error');

        statusEl.textContent = '正在执行代码...';
        statusEl.style.color = '#FFA500';
        statusEl.style.display = 'block';

        const runLanguage = this.currentCourse.name.includes('C ') ? 'c' : 'python';

        if (runLanguage === 'c') {
            // C execution is now allowed
        }

        try {
            const response = await UserManager.fetchApi('/api/programming/execute', {
                method: 'POST',
                body: JSON.stringify({ code: code, language: runLanguage })
            });

            const result = await response.json();

            if (result.success) {
                // Return Code Handling
                if (result.data.returnCode === 0) {
                    statusEl.textContent = '执行成功 (Return Code 0)';
                    statusEl.style.color = '#4CAF50';
                    consoleOutput.textContent = result.data.stdout || '(脚本未输出任何内容)';
                } else {
                    statusEl.textContent = '执行异常';
                    statusEl.style.color = '#f44336';
                    consoleOutput.classList.add('error');
                    consoleOutput.textContent = result.data.stderr || result.data.stdout || '执行中发生未知内部错误';
                }
            } else {
                statusEl.textContent = '运行被拒绝';
                statusEl.style.color = '#f44336';
                consoleOutput.classList.add('error');
                consoleOutput.textContent = result.error || 'Server Side Execution Exception';
            }
        } catch (error) {
            console.error('执行代码失败:', error);
            statusEl.textContent = '网络错误';
            statusEl.style.color = '#f44336';
            consoleOutput.classList.add('error');
            consoleOutput.textContent = '无法连接到代码执行沙盒引擎。请确保后端开启。';
        } finally {
            btn.disabled = false;
            btn.textContent = '▶ 运行代码';
        }
    }
};

document.addEventListener('DOMContentLoaded', () => {
    LearningApp.init();
});
