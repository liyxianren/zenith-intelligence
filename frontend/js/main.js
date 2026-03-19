/**
 * Zenith Intelligence (极智学习) - 主入口文件
 * 负责界面交互、事件绑定和整体流程控制
 */

// ========================================
// 全局状态管理
// ========================================

const DEFAULT_MODEL_PROVIDER = {
    name: 'minimax',
    display_name: 'MiniMax-M2.7-highspeed'
};

const AppState = {
    isProcessing: false,
    currentStep: 0, // 0: 未开始, 1: 识别中, 2: 解析中, 3: 解答中
    recognizedText: '',
    parseResult: null,
    solution: null,
    history: [],
    currentUser: null,
    modelProvider: DEFAULT_MODEL_PROVIDER.name, // 当前选择的模型
    availableProviders: [DEFAULT_MODEL_PROVIDER] // 可用的模型列表
};

// ========================================
// DOM 元素引用
// ========================================

const DOM = {
    // 用户状态
    authButtons: document.getElementById('auth-buttons'),
    userInfo: document.getElementById('user-info-card'),
    userAvatar: document.getElementById('user-avatar-display'),
    userName: document.getElementById('user-name-display'),
    logoutBtn: document.getElementById('logout-icon'),

    // 模型选择
    modelProvider: document.getElementById('model-provider'),
    modelSelectorBtn: document.getElementById('model-selector-btn'),
    selectedModelName: document.getElementById('selected-model-name'),
    modelDropdownMenu: document.getElementById('model-dropdown-menu'),

    // 文字输入
    textInput: document.getElementById('text-input'),
    charCount: document.getElementById('char-count'),
    clearTextBtn: document.getElementById('clear-text'),

    // 图片输入
    imageInput: document.getElementById('image-input'),
    insertImageBtn: document.getElementById('insert-image-btn'),
    imagePreviews: document.getElementById('image-previews'),

    // 提交按钮
    submitBtn: document.getElementById('submit-btn'),
    btnText: document.querySelector('.btn-text'),
    btnLoading: document.querySelector('.btn-loading'),

    // 隐藏的模型选择（用于数据绑定）
    hiddenModelInput: document.getElementById('hidden-model-input'),

    // 步骤指示器
    progressSection: document.getElementById('progress-section'),
    steps: document.querySelectorAll('.step'),

    // 结果展示
    resultSection: document.getElementById('result-section'),
    recognitionCard: document.getElementById('recognition-card'),
    recognizedText: document.getElementById('recognized-text'),
    editRecognitionBtn: document.getElementById('edit-recognition'),

    parseCard: document.getElementById('parse-card'),
    parseType: document.getElementById('parse-type'),
    parseSubject: document.getElementById('parse-subject'),
    parseKnowledge: document.getElementById('parse-knowledge'),
    parseDifficulty: document.getElementById('parse-difficulty'),

    solutionCard: document.getElementById('solution-card'),
    solutionThinking: document.getElementById('solution-thinking'),
    solutionSteps: document.getElementById('solution-steps'),
    solutionAnswer: document.getElementById('solution-answer'),
    solutionSummary: document.getElementById('solution-summary'),

    // 历史记录
    historyBtn: document.getElementById('history-btn'),
    historySidebar: document.getElementById('history-sidebar'),
    closeHistoryBtn: document.getElementById('close-history'),
    historyList: document.getElementById('history-list'),
    overlay: document.getElementById('overlay'),

    // 折叠按钮
    toggleBtns: document.querySelectorAll('.toggle-btn')
};

// ========================================
// 初始化
// ========================================

document.addEventListener('DOMContentLoaded', () => {
    initEventListeners();
    updateUserDisplay();
    updateSubmitButton();
    void initializeApp();

    // 定期检查系统状态
    setInterval(() => {
        void initSystemStatus();
    }, 30000); // 每30秒检查一次
});

async function initializeApp() {
    await initUserState();
    loadHistory();

    await Promise.allSettled([
        checkBackendStatus(),
        initModelSelector()
    ]);

    updateSubmitButton();
}

// ========================================
// 事件监听器
// ========================================

function initEventListeners() {
    // 用户登出
    if (DOM.logoutBtn) {
        DOM.logoutBtn.addEventListener('click', () => {
            UserManager.logout();
            AppState.currentUser = null;
            updateUserDisplay();
        });
    }

    // 模型选择
    if (DOM.modelProvider) {
        DOM.modelProvider.addEventListener('change', handleModelChange);
    }
    if (DOM.modelSelectorBtn && DOM.modelDropdownMenu) {
        DOM.modelSelectorBtn.addEventListener('click', (e) => {
            e.stopPropagation();
            DOM.modelDropdownMenu.classList.toggle('hidden');
        });

        // 点击外部关闭下拉菜单
        document.addEventListener('click', (e) => {
            if (!DOM.modelSelectorBtn.contains(e.target) && !DOM.modelDropdownMenu.contains(e.target)) {
                DOM.modelDropdownMenu.classList.add('hidden');
            }
        });
    }

    // 文字输入
    DOM.textInput.addEventListener('input', handleTextInput);
    DOM.clearTextBtn.addEventListener('click', clearText);

    // 图片插入
    if (DOM.insertImageBtn) {
        DOM.insertImageBtn.addEventListener('click', () => DOM.imageInput.click());
    }

    // 图片选择
    DOM.imageInput.addEventListener('change', handleImageSelect);

    // 粘贴图片
    DOM.textInput.addEventListener('paste', handlePaste);

    // 拖拽图片
    document.addEventListener('dragover', (e) => {
        e.preventDefault();
    });

    document.addEventListener('drop', (e) => {
        e.preventDefault();
        const files = e.dataTransfer.files;
        if (files.length > 0 && files[0].type.startsWith('image/')) {
            processImage(files[0]);
        }
    });

    // 提交按钮
    DOM.submitBtn.addEventListener('click', handleSubmit);

    // 历史记录
    DOM.historyBtn.addEventListener('click', openHistory);
    DOM.closeHistoryBtn.addEventListener('click', closeHistory);
    DOM.overlay.addEventListener('click', closeHistory);

    // 折叠按钮
    DOM.toggleBtns.forEach(btn => {
        btn.addEventListener('click', () => toggleCard(btn));
    });

    // 编辑识别结果
    DOM.editRecognitionBtn.addEventListener('click', editRecognition);

    // 键盘快捷键
    document.addEventListener('keydown', handleKeyboard);
}



// ========================================
// 系统状态检查
// ========================================

async function initSystemStatus() {
    await Promise.allSettled([
        checkBackendStatus(),
        checkModelHealth()
    ]);
}

async function checkBackendStatus() {
    try {
        const startTime = performance.now();
        const response = await UserManager.fetchApi('/api/health');
        const endTime = performance.now();
        const delay = Math.round(endTime - startTime);

        const result = await response.json();

        if (result.success) {
            updateBackendStatus(true, '在线', delay);
        } else {
            updateBackendStatus(false, '离线');
            showWarning('后端服务离线，部分功能可能无法使用');
        }
    } catch (error) {
        console.error('检查后端状态失败:', error);
        updateBackendStatus(false, '离线');
        showWarning('无法连接到后端服务，请检查网络连接');
    }
}

function updateBackendStatus(healthy, statusText, delay) {
    const dotPing = document.getElementById('backend-dot-ping');
    const dot = document.getElementById('backend-dot');
    const text = document.getElementById('backend-status-text');
    const delayElement = document.getElementById('backend-delay');

    if (dotPing && dot) {
        if (healthy) {
            dotPing.className = "animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75";
            dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500";
        } else {
            dotPing.className = "animate-ping absolute inline-flex h-full w-full rounded-full bg-red-400 opacity-75";
            dot.className = "relative inline-flex rounded-full h-2.5 w-2.5 bg-red-500";
        }
    }

    if (text) {
        text.textContent = statusText;
    }

    if (delayElement) {
        if (healthy && delay !== undefined) {
            delayElement.textContent = delay;
            delayElement.parentElement.style.display = 'flex';
        } else {
            delayElement.textContent = '';
        }
    }
}

// ========================================
// 模型选择器
// ========================================

async function initModelSelector() {
    try {
        const response = await UserManager.fetchApi('/api/model/providers');
        const result = await response.json();

        if (result.success && result.data.providers) {
            const providers = result.data.providers.length ? result.data.providers : [DEFAULT_MODEL_PROVIDER];
            const defaultProviderName = result.data.default || DEFAULT_MODEL_PROVIDER.name;
            const defaultProvider = providers.find(p => p.name === defaultProviderName) || providers[0];

            AppState.availableProviders = providers;
            AppState.modelProvider = defaultProvider.name;

            // 更新选择器
            if (DOM.modelProvider) {
                DOM.modelProvider.innerHTML = providers.map(provider => `
                    <option value="${provider.name}" ${provider.name === defaultProvider.name ? 'selected' : ''}>
                        ${provider.display_name}
                    </option>
                `).join('');
            }

            // 新版UI适配 (Tailwind 下拉菜单)
            if (DOM.modelDropdownMenu) {
                DOM.modelDropdownMenu.innerHTML = providers.map(provider => `
                    <button class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors" data-provider-name="${provider.name}" data-provider-display="${provider.display_name}">
                        ${provider.display_name}
                    </button>
                `).join('');

                // 绑定下拉菜单点击事件
                const dropdownItems = DOM.modelDropdownMenu.querySelectorAll('button');
                dropdownItems.forEach(item => {
                    item.addEventListener('click', (e) => {
                        e.stopPropagation();
                        const val = item.getAttribute('data-provider-name');
                        const display = item.getAttribute('data-provider-display');

                        // 更新内部状态
                        AppState.modelProvider = val;

                        // 同步到隐藏的 select 并触发 change 事件以进行检查
                        if (DOM.modelProvider) {
                            DOM.modelProvider.value = val;
                        }

                        // 更新 UI
                        if (DOM.selectedModelName) {
                            DOM.selectedModelName.textContent = display;
                        }

                        // 关闭下拉菜单
                        DOM.modelDropdownMenu.classList.add('hidden');

                        // 触发原来绑定的健康检查
                        checkModelHealth();
                    });
                });
            }

            // 初始设置按钮文本
            if (DOM.selectedModelName) {
                DOM.selectedModelName.textContent = defaultProvider.display_name;
            }

            // 检查模型健康状态
            await checkModelHealth();
        }
    } catch (error) {
        console.error('加载模型列表失败:', error);
        if (DOM.modelProvider) {
            DOM.modelProvider.innerHTML = `<option value="${DEFAULT_MODEL_PROVIDER.name}">${DEFAULT_MODEL_PROVIDER.display_name}</option>`;
        }
        if (DOM.modelDropdownMenu) {
            DOM.modelDropdownMenu.innerHTML = `
                <button class="w-full text-left px-4 py-2 text-sm text-slate-700 hover:bg-slate-50 hover:text-blue-600 transition-colors" data-provider-name="${DEFAULT_MODEL_PROVIDER.name}" data-provider-display="${DEFAULT_MODEL_PROVIDER.display_name}">
                    ${DEFAULT_MODEL_PROVIDER.display_name}
                </button>
            `;
        }
        if (DOM.selectedModelName) {
            DOM.selectedModelName.textContent = DEFAULT_MODEL_PROVIDER.display_name;
        }
        AppState.availableProviders = [DEFAULT_MODEL_PROVIDER];
        AppState.modelProvider = DEFAULT_MODEL_PROVIDER.name;
        await checkModelHealth();
    }
}

async function checkModelHealth() {
    const currentProvider = AppState.modelProvider || DEFAULT_MODEL_PROVIDER.name;

    try {
        const response = await UserManager.fetchApi(`/api/model/providers/${encodeURIComponent(currentProvider)}/health`);
        const result = await response.json();

        if (result.success && result.data) {
            if (result.data.healthy) {
                updateModelStatus(true, '在线');
            } else {
                updateModelStatus(false, '离线');
                showWarning('AI模型离线，解题功能可能无法使用');
            }
        } else {
            updateModelStatus(false, '未知');
        }
    } catch (error) {
        console.error('检查模型健康状态失败:', error);
        updateModelStatus(false, '未知');
        showWarning('无法检查AI模型状态，请稍后重试');
    }
}

function updateModelStatus(healthy, statusText) {
    const icon = document.getElementById('model-status-icon');
    const text = document.getElementById('model-status-text');

    if (icon) {
        icon.className = healthy
            ? "w-3.5 h-3.5 text-amber-500"
            : "w-3.5 h-3.5 text-red-500";
    }

    if (text) {
        text.textContent = statusText;
    }
}

function handleModelChange(event) {
    AppState.modelProvider = event.target.value;
    checkModelHealth();
}

// ========================================
// 文字输入处理
// ========================================

function handleTextInput() {
    const text = DOM.textInput.value;
    const count = text.length;

    if (DOM.charCount) {
        DOM.charCount.textContent = count; // Only show current count as per HTML design

        if (count > 2000) {
            DOM.charCount.style.color = '#EF4444'; // Red-500
        } else {
            DOM.charCount.style.color = '#94A3B8'; // Slate-400
        }
    }

    updateSubmitButton();
}

function clearText() {
    DOM.textInput.value = '';
    if (DOM.charCount) {
        DOM.charCount.textContent = '0';
        DOM.charCount.style.color = '#94A3B8';
    }
    updateSubmitButton();
}

// ========================================
// 图片处理
// ========================================

// 存储图片数据
AppState.images = [];

function handlePaste(e) {
    const items = e.clipboardData.items;
    for (let i = 0; i < items.length; i++) {
        if (items[i].type.startsWith('image/')) {
            const file = items[i].getAsFile();
            if (file) {
                processImage(file);
                break;
            }
        }
    }
}

function handleImageSelect(e) {
    const file = e.target.files[0];
    if (file) {
        processImage(file);
    }
    // 重置 input 值，以便可以重复选择同一文件
    e.target.value = '';
}

function processImage(file) {
    // 验证文件类型
    if (!file.type.startsWith('image/')) {
        showError('请选择图片文件');
        return;
    }

    // 验证文件大小 (5MB)
    if (file.size > 5 * 1024 * 1024) {
        showError('图片大小不能超过 5MB');
        return;
    }

    // 显示加载中
    showInfo('正在处理图片...');

    // 读取并压缩图片
    const reader = new FileReader();
    reader.onload = (e) => {
        const img = new Image();
        img.onload = () => {
            compressImage(img, file.type);
        };
        img.src = e.target.result;
    };
    reader.readAsDataURL(file);
}

function compressImage(img, type) {
    const canvas = document.createElement('canvas');
    const ctx = canvas.getContext('2d');

    // 计算压缩后的尺寸
    let width = img.width;
    let height = img.height;
    const maxSize = 1024;

    if (width > maxSize || height > maxSize) {
        if (width > height) {
            height = (height / width) * maxSize;
            width = maxSize;
        } else {
            width = (width / height) * maxSize;
            height = maxSize;
        }
    }

    canvas.width = width;
    canvas.height = height;
    ctx.drawImage(img, 0, 0, width, height);

    // 转换为 Base64 (质量 0.8)
    const compressedData = canvas.toDataURL(type, 0.8);

    // 添加到图片数组
    const imageItem = {
        id: Date.now().toString(),
        data: compressedData,
        type: type
    };
    AppState.images.push(imageItem);

    // 显示预览
    showImagePreviews();
    updateSubmitButton();
}

function showImagePreviews() {
    if (!DOM.imagePreviews) return;

    if (AppState.images.length === 0) {
        DOM.imagePreviews.innerHTML = '';
        return;
    }

    DOM.imagePreviews.innerHTML = AppState.images.map(image => `
        <div class="image-preview-item relative inline-block">
            <img src="${image.data}" alt="图片预览" class="w-16 h-16 object-cover rounded-lg border border-slate-200">
            <button class="remove-image absolute -top-1.5 -right-1.5 w-5 h-5 bg-red-500 text-white rounded-full text-xs flex items-center justify-center hover:bg-red-600" onclick="removeImage('${image.id}')" aria-label="删除图片">×</button>
        </div>
    `).join('');
}

function removeImage(imageId) {
    AppState.images = AppState.images.filter(image => image.id !== imageId);
    showImagePreviews();
    updateSubmitButton();
}

// ========================================
// 提交处理
// ========================================

function updateUserDisplay() {
    if (UserManager.isLoggedIn()) {
        const user = UserManager.getSavedUser();
        AppState.currentUser = user;

        if (DOM.userInfo) DOM.userInfo.style.display = 'flex';
        if (DOM.userName) DOM.userName.textContent = user.username;
        if (DOM.userAvatar) DOM.userAvatar.textContent = user.username.charAt(0).toUpperCase();
    } else {
        AppState.currentUser = null;

        if (DOM.userInfo) DOM.userInfo.style.display = 'none';
    }
}

async function initUserState() {
    try {
        await UserManager.init();
    } catch (error) {
        console.error('初始化用户状态失败:', error);
    }
    updateUserDisplay();
}

function updateSubmitButton() {
    const hasText = DOM.textInput.value.trim().length > 0;
    const hasImages = AppState.images.length > 0;
    const canSubmit = hasText || hasImages;

    DOM.submitBtn.disabled = !canSubmit || AppState.isProcessing;
}

async function handleSubmit() {
    if (AppState.isProcessing) return;

    AppState.isProcessing = true;
    updateSubmitButton();
    showLoading(true);
    showLoadingOverlay(true);
    hideResults();

    try {
        showInfo('正在处理您的请求...');

        const hasText = DOM.textInput.value.trim().length > 0;
        const hasImages = AppState.images.length > 0;

        if (UserManager.isLoggedIn()) {
            // 登录用户使用完整解题流程（自动保存历史记录）
            await solveWithFullPipeline();
        } else {
            // 未登录用户：使用原有流程
            if (hasText && !hasImages) {
                // 只有文字输入
                AppState.recognizedText = DOM.textInput.value.trim();
                await skipRecognitionStep();
            } else if (hasImages) {
                // 有图片输入
                await performRecognition();
            }

            // 执行解析和解答
            await performParsing();
            await performSolving();

            // 保存到历史记录
            saveToHistory();
        }

        showSuccess('解题成功！');

    } catch (error) {
        console.error('处理失败:', error);
        showError(error.message || '处理失败，请重试');
    } finally {
        AppState.isProcessing = false;
        showLoading(false);
        showLoadingOverlay(false);
        updateSubmitButton();
        hideProgress();
    }
}

async function solveWithFullPipeline() {
    const hasText = DOM.textInput.value.trim().length > 0;
    const hasImages = AppState.images.length > 0;

    let requestBody = {};

    if (hasText && hasImages) {
        // 文字和图片混合输入
        requestBody = {
            type: 'mixed',
            text: DOM.textInput.value.trim(),
            images: AppState.images.map(img => img.data)
        };
    } else if (hasText) {
        // 只有文字输入
        requestBody = {
            type: 'text',
            content: DOM.textInput.value.trim()
        };
    } else if (hasImages) {
        // 只有图片输入
        requestBody = {
            type: 'image',
            content: AppState.images[0].data
        };
    }

    showProgress(1);
    showProgress(2);
    showProgress(3);

    // 添加模型提供者参数
    if (AppState.modelProvider) {
        requestBody.provider = AppState.modelProvider;
    }

    const response = await UserManager.fetchApi('/api/solve-problem', {
        method: 'POST',
        headers: UserManager.getHeaders(),
        body: JSON.stringify(requestBody)
    });

    if (!response.ok) {
        throw new Error('解题失败');
    }

    const result = await response.json();

    if (!result.success) {
        throw new Error(result.error || '解题失败');
    }

    // 更新状态
    AppState.recognizedText = result.data.recognizedText;
    AppState.parseResult = result.data.parseResult;
    AppState.solution = result.data.solution;

    // 显示结果
    showRecognitionResult();
    showParseResult();
    showSolutionResult();

    // 刷新历史记录
    loadHistoryFromServer();
}

// ========================================
// 多 Agent 流程
// ========================================

async function performRecognition() {
    showProgress(1);

    // 调用后端 API 进行图像识别
    const response = await UserManager.fetchApi('/api/recognize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: AppState.images[0].data })
    });

    if (!response.ok) throw new Error('识别失败');

    const result = await response.json();
    if (!result.success) throw new Error(result.error || '识别失败');

    AppState.recognizedText = normalizeRecognizedText(result.data.text);

    showRecognitionResult();
}

async function skipRecognitionStep() {
    showProgress(1);
    // 文字输入不需要识别，直接显示
    showRecognitionResult();
}

async function performParsing() {
    showProgress(2);

    // 调用后端 API 进行题目解析
    const response = await UserManager.fetchApi('/api/parse', {
        method: 'POST',
        headers: UserManager.getHeaders(),
        body: JSON.stringify({
            text: AppState.recognizedText,
            provider: AppState.modelProvider
        })
    });

    if (!response.ok) {
        let errorText = '解析失败';
        try {
            const errBody = await response.json();
            errorText = errBody.error || errBody.message || errorText;
        } catch (e) {
            // ignore json parse error
        }
        throw new Error(errorText);
    }

    const result = await response.json();
    if (!result.success) throw new Error(result.error || '解析失败');

    AppState.parseResult = result.data;

    showParseResult();
}

async function performSolving() {
    showProgress(3);

    // 调用后端 API 生成解答
    const response = await UserManager.fetchApi('/api/solve', {
        method: 'POST',
        headers: UserManager.getHeaders(),
        body: JSON.stringify({
            text: AppState.recognizedText,
            parseResult: AppState.parseResult,
            provider: AppState.modelProvider
        })
    });

    if (!response.ok) throw new Error('解答生成失败');

    const result = await response.json();
    if (!result.success) throw new Error(result.error || '解答生成失败');

    AppState.solution = result.data;

    showSolutionResult();
}

// ========================================
// 结果显示
// ========================================

function showRecognitionResult() {
    DOM.recognizedText.textContent = AppState.recognizedText;
    DOM.resultSection.style.display = 'flex';
}

function showParseResult() {
    const result = AppState.parseResult || {};

    DOM.parseType.innerHTML = renderInlineMarkdown(result.type || '-');
    DOM.parseSubject.innerHTML = renderInlineMarkdown(result.subject || '-');

    // 知识点标签
    const knowledgePoints = Array.isArray(result.knowledgePoints) ? result.knowledgePoints : [];
    DOM.parseKnowledge.innerHTML = knowledgePoints
        .map(point => `<span class="parse-tag">${escapeHtml(String(point ?? ''))}</span>`)
        .join('');

    // 难度等级
    const difficultyText = String(result.difficulty ?? '').trim();
    let difficultyClass = '';
    if (difficultyText.includes('简单')) {
        difficultyClass = 'easy';
    } else if (difficultyText.includes('中等')) {
        difficultyClass = 'medium';
    } else if (difficultyText) {
        difficultyClass = 'hard';
    }

    DOM.parseDifficulty.innerHTML = renderInlineMarkdown(difficultyText || '-');
    DOM.parseDifficulty.className = `parse-value difficulty${difficultyClass ? ` ${difficultyClass}` : ''}`;
}

function showSolutionResult() {
    const solution = AppState.solution || {};

    const thinkingText = normalizeSolutionSectionText(solution.thinking, ['解题思路', '思路', 'thinking']);
    DOM.solutionThinking.innerHTML = renderMarkdown(thinkingText || '暂未生成解题思路，请重试。');
    DOM.solutionThinking.classList.add('markdown-content');

    const steps = (Array.isArray(solution.steps) ? solution.steps : [])
        .map(step => normalizeSolutionStepText(step))
        .filter(Boolean);

    let displaySteps = steps.slice();
    if (displaySteps.length === 0 && thinkingText) {
        displaySteps = thinkingText
            .split(/[。！？；;\n]+/)
            .map(item => item.trim())
            .filter(item => item.length > 3)
            .slice(0, 6);
    }

    DOM.solutionSteps.innerHTML = displaySteps.length > 0
        ? displaySteps
            .map((step, index) => `
                <div class="solution-step">
                    <p class="solution-step-title">步骤 ${index + 1}</p>
                    <div class="markdown-content">${renderMarkdown(step)}</div>
                </div>
            `)
            .join('')
        : '<p class="markdown-content">暂未生成详细步骤，请重试或简化题目后再次生成。</p>';

    let answerText = normalizeSolutionSectionText(solution.answer, ['最终答案', '答案', 'answer']);
    if (!answerText && displaySteps.length > 0) {
        answerText = displaySteps[displaySteps.length - 1];
    }

    let summaryText = normalizeSolutionSectionText(solution.summary, ['知识总结', '总结', 'summary']);
    if (!summaryText && thinkingText && thinkingText !== answerText) {
        summaryText = thinkingText;
    }

    DOM.solutionAnswer.innerHTML = renderMarkdown(answerText || '暂未生成最终答案，请重试。');
    DOM.solutionAnswer.classList.add('markdown-content');
    DOM.solutionSummary.innerHTML = renderMarkdown(summaryText || '暂未生成知识总结，请重试。');
    DOM.solutionSummary.classList.add('markdown-content');

    // markdown 渲染完成后，再对数学公式进行排版
    renderMathInContainer(DOM.solutionThinking);
    renderMathInContainer(DOM.solutionSteps);
    renderMathInContainer(DOM.solutionAnswer);
    renderMathInContainer(DOM.solutionSummary);
}

function hideResults() {
    DOM.resultSection.style.display = 'none';
}

// ========================================
// 进度指示器
// ========================================

function showProgress(step) {
    AppState.currentStep = step;
    DOM.progressSection.style.display = 'block';

    DOM.steps.forEach((s, index) => {
        const stepNum = index + 1;
        s.classList.remove('active', 'completed');

        if (stepNum === step) {
            s.classList.add('active');
        } else if (stepNum < step) {
            s.classList.add('completed');
        }
    });
}

function hideProgress() {
    DOM.progressSection.style.display = 'none';
    AppState.currentStep = 0;
}

// ========================================
// 加载状态
// ========================================

function showLoading(show) {
    if (DOM.btnText) DOM.btnText.style.display = show ? 'none' : 'flex';
    if (DOM.btnLoading) DOM.btnLoading.style.display = show ? 'flex' : 'none';

    if (!DOM.btnText && !DOM.btnLoading && DOM.submitBtn) {
        if (show) {
            DOM.submitBtn.innerHTML = `
                <svg class="w-4 h-4 animate-spin" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <line x1="12" y1="2" x2="12" y2="6"></line>
                    <line x1="12" y1="18" x2="12" y2="22"></line>
                    <line x1="4.93" y1="4.93" x2="7.76" y2="7.76"></line>
                    <line x1="16.24" y1="16.24" x2="19.07" y2="19.07"></line>
                    <line x1="2" y1="12" x2="6" y2="12"></line>
                    <line x1="18" y1="12" x2="22" y2="12"></line>
                    <line x1="4.93" y1="19.07" x2="7.76" y2="16.24"></line>
                    <line x1="16.24" y1="7.76" x2="19.07" y2="4.93"></line>
                </svg>
                处理中...
            `;
        } else {
            DOM.submitBtn.innerHTML = `
                开始解答
                <svg class="w-4 h-4 group-hover:translate-x-1 transition-transform" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">
                    <path d="m22 2-7 20-4-9-9-4Z" />
                    <path d="M22 2 11 13" />
                </svg>
            `;
        }
    }
}

// ========================================
// 卡片折叠
// ========================================

function toggleCard(btn) {
    const targetId = btn.dataset.target;
    const target = document.getElementById(targetId);

    btn.classList.toggle('collapsed');
    target.style.display = btn.classList.contains('collapsed') ? 'none' : 'block';
}

// ========================================
// 编辑识别结果
// ========================================

function editRecognition() {
    const newText = prompt('编辑识别的题目内容:', AppState.recognizedText);
    if (newText !== null && newText.trim() !== '') {
        AppState.recognizedText = newText.trim();
        DOM.recognizedText.textContent = AppState.recognizedText;
    }
}

// ========================================
// 历史记录
// ========================================

function loadHistory() {
    if (UserManager.isLoggedIn()) {
        // 登录用户：从后端获取历史记录
        loadHistoryFromServer();
    } else {
        // 未登录用户：从本地存储获取
        try {
            const saved = localStorage.getItem('ai-learning-history');
            if (saved) {
                AppState.history = JSON.parse(saved);
                renderHistory();
            }
        } catch (e) {
            console.error('加载历史记录失败:', e);
        }
    }
}

async function loadHistoryFromServer() {
    try {
        const response = await UserManager.fetchApi('/api/history', {
            method: 'GET',
            headers: UserManager.getHeaders()
        });

        const result = await response.json();

        if (result.success) {
            // 转换为本地格式
            AppState.history = result.data.records.map(record => ({
                id: record.id,
                timestamp: record.createdAt,
                type: 'text',
                content: record.question.substring(0, 50) + (record.question.length > 50 ? '...' : ''),
                recognizedText: record.question,
                parseResult: record.parseResult,
                solution: record.solution,
                fromServer: true
            }));
            renderHistory();
        }
    } catch (error) {
        console.error('加载服务器历史记录失败:', error);
    }
}

function saveToHistory() {
    const hasText = DOM.textInput.value.trim().length > 0;
    const hasImages = AppState.images.length > 0;

    let type = 'text';
    let content = '';

    if (hasText && hasImages) {
        type = 'mixed';
        content = DOM.textInput.value.trim().substring(0, 40) + '... (含图片)';
    } else if (hasText) {
        type = 'text';
        content = DOM.textInput.value.trim().substring(0, 50) + '...';
    } else if (hasImages) {
        type = 'image';
        content = `图片题目 (${AppState.images.length}张)`;
    }

    const item = {
        id: Date.now().toString(),
        timestamp: new Date().toISOString(),
        type: type,
        content: content,
        recognizedText: AppState.recognizedText,
        parseResult: AppState.parseResult,
        solution: AppState.solution
    };

    AppState.history.unshift(item);

    // 限制历史记录数量（最多 50 条）
    if (AppState.history.length > 50) {
        AppState.history = AppState.history.slice(0, 50);
    }

    // 保存到本地存储
    localStorage.setItem('ai-learning-history', JSON.stringify(AppState.history));
    renderHistory();
}

function renderHistory() {
    if (AppState.history.length === 0) {
        DOM.historyList.innerHTML = '<p style="text-align: center; color: var(--text-tertiary); padding: 20px;">暂无历史记录</p>';
        return;
    }

    DOM.historyList.innerHTML = AppState.history.map(item => `
        <div class="history-item" data-id="${item.id}">
            <div class="history-item-title">${escapeHtml(item.content)}</div>
            <div class="history-item-time">${formatTime(item.timestamp)}</div>
        </div>
    `).join('');

    // 绑定点击事件
    DOM.historyList.querySelectorAll('.history-item').forEach(item => {
        item.addEventListener('click', () => loadHistoryItem(parseInt(item.dataset.id)));
    });
}

function loadHistoryItem(id) {
    const item = AppState.history.find(h => h.id === id);
    if (!item) return;

    // 恢复数据
    AppState.recognizedText = item.recognizedText;
    AppState.parseResult = item.parseResult;
    AppState.solution = item.solution;

    // 显示结果
    showRecognitionResult();
    showParseResult();
    showSolutionResult();

    closeHistory();

    // 滚动到结果区域
    DOM.resultSection.scrollIntoView({ behavior: 'smooth' });
}

function openHistory() {
    DOM.historySidebar.classList.add('open');
    DOM.overlay.classList.add('show');
    document.body.style.overflow = 'hidden';
}

function closeHistory() {
    DOM.historySidebar.classList.remove('open');
    DOM.overlay.classList.remove('show');
    document.body.style.overflow = '';
}

// ========================================
// 键盘快捷键
// ========================================

function handleKeyboard(e) {
    // Ctrl/Cmd + Enter 提交
    if ((e.ctrlKey || e.metaKey) && e.key === 'Enter') {
        if (!DOM.submitBtn.disabled) {
            handleSubmit();
        }
    }

    // ESC 关闭历史记录
    if (e.key === 'Escape') {
        closeHistory();
    }
}

// ========================================
// 工具函数
// ========================================

function simulateDelay(ms) {
    return new Promise(resolve => setTimeout(resolve, ms));
}

// Toast 通知系统
function showToast(message, type = 'info', duration = 3000) {
    const container = document.getElementById('toast-container');
    if (!container) return;

    const toast = document.createElement('div');
    toast.className = `toast-item ${type}`;
    toast.innerHTML = `
        <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" style="width: 20px; height: 20px;">
            ${type === 'success' ? '<path d="M22 11.08V12a10 10 0 1 1-5.93-9.14" /><polyline points="22 4 12 14.01 9 11.01" />' : ''}
            ${type === 'error' ? '<circle cx="12" cy="12" r="10" /><line x1="15" y1="9" x2="9" y2="15" /><line x1="9" y1="9" x2="15" y2="15" />' : ''}
            ${type === 'warning' ? '<path d="M10.29 3.86L1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 2 0 0 0-3.42 0z" /><line x1="12" y1="9" x2="12" y2="13" /><line x1="12" y1="17" x2="12.01" y2="17" />' : ''}
            ${type === 'info' ? '<circle cx="12" cy="12" r="10" /><line x1="12" y1="16" x2="12" y2="12" /><line x1="12" y1="8" x2="12.01" y2="8" />' : ''}
        </svg>
        <span>${message}</span>
    `;

    container.appendChild(toast);

    // 自动移除
    setTimeout(() => {
        toast.classList.add('slide-out');
        setTimeout(() => {
            container.removeChild(toast);
        }, 300);
    }, duration);
}

function showError(message) {
    showToast(message, 'error');
}

function showSuccess(message) {
    showToast(message, 'success');
}

function showInfo(message) {
    showToast(message, 'info');
}

function showWarning(message) {
    showToast(message, 'warning');
}

// 加载遮罩
function showLoadingOverlay(show) {
    const overlay = document.getElementById('loading-overlay');
    if (overlay) {
        overlay.style.display = show ? 'flex' : 'none';
    }
}



function normalizeRecognizedText(value) {
    if (typeof value === 'string') {
        return value.trim();
    }

    if (Array.isArray(value)) {
        return value
            .map(item => {
                if (typeof item === 'string') return item;
                if (item && typeof item === 'object') {
                    if (typeof item.text === 'string') return item.text;
                    if (typeof item.content === 'string') return item.content;
                }
                return '';
            })
            .filter(Boolean)
            .join('\n')
            .trim();
    }

    if (value && typeof value === 'object') {
        if (typeof value.text === 'string') return value.text.trim();
        if (typeof value.content === 'string') return value.content.trim();
        try {
            return JSON.stringify(value);
        } catch (e) {
            return String(value);
        }
    }

    return value == null ? '' : String(value).trim();
}

function normalizeSolutionText(value) {
    if (typeof value === 'string') {
        return value.trim();
    }

    if (Array.isArray(value)) {
        return value
            .map(item => normalizeSolutionText(item))
            .filter(Boolean)
            .join('\n')
            .trim();
    }

    if (value && typeof value === 'object') {
        if (typeof value.text === 'string') return value.text.trim();
        if (typeof value.content === 'string') return value.content.trim();
        try {
            return JSON.stringify(value);
        } catch (e) {
            return String(value).trim();
        }
    }

    return value == null ? '' : String(value).trim();
}

function stripLeadingSectionTitle(text, aliases) {
    let normalized = normalizeSolutionText(text);
    if (!normalized || !Array.isArray(aliases) || aliases.length === 0) {
        return normalized;
    }

    const escapedAliases = aliases
        .map(alias => alias.replace(/[.*+?^${}()|[\]\\]/g, '\\$&'))
        .join('|');

    if (!escapedAliases) {
        return normalized;
    }

    const patterns = [
        new RegExp(`^\\s*#{1,6}\\s*(?:${escapedAliases})\\s*[:：]?\\s*`, 'i'),
        new RegExp(`^\\s*(?:${escapedAliases})\\s*[:：]?\\s*`, 'i')
    ];

    let previous = '';
    while (normalized && normalized !== previous) {
        previous = normalized;
        patterns.forEach(pattern => {
            normalized = normalized.replace(pattern, '').trim();
        });
    }

    return normalized;
}

function normalizeSolutionSectionText(value, aliases = []) {
    return stripLeadingSectionTitle(value, aliases);
}

function normalizeSolutionStepText(value) {
    let normalized = stripLeadingSectionTitle(value, ['步骤', '详细步骤', '解题步骤', 'step']);
    normalized = normalized.replace(/^\s*步骤\s*\d+\s*[:：.\-、]?\s*/i, '').trim();
    return normalized;
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function hasRichMarkdownRenderer() {
    return typeof marked !== 'undefined' && typeof DOMPurify !== 'undefined';
}

function hasMathRenderer() {
    return typeof renderMathInElement === 'function';
}

function sanitizeRenderedHtml(html) {
    if (!hasRichMarkdownRenderer()) return html;
    return DOMPurify.sanitize(html, {
        USE_PROFILES: { html: true }
    });
}

function renderMathInContainer(container) {
    if (!container || !hasMathRenderer()) return;
    try {
        renderMathInElement(container, {
            delimiters: [
                { left: '$$', right: '$$', display: true },
                { left: '\\[', right: '\\]', display: true },
                { left: '$', right: '$', display: false },
                { left: '\\(', right: '\\)', display: false }
            ],
            throwOnError: false,
            strict: 'ignore'
        });
    } catch (error) {
        console.warn('LaTeX 渲染失败:', error);
    }
}

function renderInlineMarkdown(text) {
    const source = String(text ?? '').trim();
    if (!source) return '';

    if (hasRichMarkdownRenderer()) {
        marked.setOptions({
            gfm: true,
            breaks: true
        });
        return sanitizeRenderedHtml(marked.parseInline(source));
    }

    let html = escapeHtml(source);

    // fallback: 轻量行内 markdown 规则
    // 行内代码优先处理，避免被其他规则破坏
    html = html.replace(/`([^`\n]+)`/g, '<code>$1</code>');
    html = html.replace(/\[([^\]]+)\]\((https?:\/\/[^\s)]+)\)/g, '<a href="$2" target="_blank" rel="noopener noreferrer">$1</a>');
    html = html.replace(/\*\*([^*]+)\*\*/g, '<strong>$1</strong>');
    html = html.replace(/\*([^*\n]+)\*/g, '<em>$1</em>');
    html = html.replace(/~~([^~\n]+)~~/g, '<del>$1</del>');

    return html;
}

function renderMarkdownBlockFallback(block, codeBlocks) {
    const codeTokenMatch = block.match(/^@@CODE_BLOCK_(\d+)@@$/);
    if (codeTokenMatch) {
        const codeBlock = codeBlocks[Number(codeTokenMatch[1])];
        const languageClass = codeBlock.lang ? ` class="language-${escapeHtml(codeBlock.lang)}"` : '';
        return `<pre><code${languageClass}>${codeBlock.code}</code></pre>`;
    }

    const lines = block.split('\n').map(line => line.replace(/\s+$/, ''));

    if (lines.every(line => /^[-*+]\s+/.test(line.trim()))) {
        const items = lines
            .map(line => line.trim().replace(/^[-*+]\s+/, ''))
            .map(item => `<li>${renderInlineMarkdown(item)}</li>`)
            .join('');
        return `<ul>${items}</ul>`;
    }

    if (lines.every(line => /^\d+\.\s+/.test(line.trim()))) {
        const items = lines
            .map(line => line.trim().replace(/^\d+\.\s+/, ''))
            .map(item => `<li>${renderInlineMarkdown(item)}</li>`)
            .join('');
        return `<ol>${items}</ol>`;
    }

    const headingMatch = block.match(/^(#{1,6})\s+(.+)$/);
    if (headingMatch) {
        const level = headingMatch[1].length;
        return `<h${level}>${renderInlineMarkdown(headingMatch[2])}</h${level}>`;
    }

    if (lines.every(line => /^>\s?/.test(line.trim()))) {
        const quote = lines
            .map(line => line.trim().replace(/^>\s?/, ''))
            .map(line => renderInlineMarkdown(line))
            .join('<br>');
        return `<blockquote>${quote}</blockquote>`;
    }

    return `<p>${lines.map(line => renderInlineMarkdown(line)).join('<br>')}</p>`;
}

function renderMarkdown(text) {
    const source = String(text ?? '').replace(/\r\n?/g, '\n').trim();
    if (!source) return '';

    if (hasRichMarkdownRenderer()) {
        marked.setOptions({
            gfm: true,
            breaks: true
        });
        return sanitizeRenderedHtml(marked.parse(source));
    }

    const codeBlocks = [];
    const withCodeTokens = source.replace(/```([a-zA-Z0-9_-]+)?\n?([\s\S]*?)```/g, (_, lang = '', code = '') => {
        const token = `@@CODE_BLOCK_${codeBlocks.length}@@`;
        codeBlocks.push({
            lang: lang.trim(),
            code: escapeHtml(code.replace(/\n$/, ''))
        });
        return token;
    });

    return withCodeTokens
        .split(/\n{2,}/)
        .map(block => renderMarkdownBlockFallback(block, codeBlocks))
        .join('');
}

function formatTime(timestamp) {
    const date = new Date(timestamp);
    const now = new Date();
    const diff = now - date;

    // 小于 1 分钟
    if (diff < 60000) {
        return '刚刚';
    }

    // 小于 1 小时
    if (diff < 3600000) {
        return `${Math.floor(diff / 60000)} 分钟前`;
    }

    // 小于 24 小时
    if (diff < 86400000) {
        return `${Math.floor(diff / 3600000)} 小时前`;
    }

    // 大于 24 小时
    return date.toLocaleDateString('zh-CN');
}

// ========================================
// API 调用（实际项目中使用）
// ========================================

/*
async function callRecognitionAPI(imageData) {
    const response = await fetch('/api/recognize', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ image: imageData })
    });
    
    if (!response.ok) throw new Error('识别失败');
    
    const data = await response.json();
    return data.text;
}

async function callParseAPI(text) {
    const response = await fetch('/api/parse', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
    });
    
    if (!response.ok) throw new Error('解析失败');
    
    return await response.json();
}

async function callSolveAPI(text, parseResult) {
    const response = await fetch('/api/solve', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text, parseResult })
    });
    
    if (!response.ok) throw new Error('解答生成失败');
    
    return await response.json();
}
*/
