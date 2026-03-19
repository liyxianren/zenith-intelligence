import React from 'react';

interface Model {
  id: string;
  name: string;
  description: string;
}

interface ModelSelectorProps {
  onSelectModel: (modelId: string) => void;
  selectedModelId: string;
}

const ModelSelector: React.FC<ModelSelectorProps> = ({ onSelectModel, selectedModelId }) => {
  const models: Model[] = [
    {
      id: 'MiniMax-M2.7-highspeed',
      name: 'MiniMax-M2.7-highspeed',
      description: '统一文本模型，适合高并发问答、解题和复杂推理任务',
    },
  ];

  return (
    <div className="model-selector">
      <label className="model-selector-label">
        选择模型
      </label>
      <div className="model-selector-grid">
        {models.map((model) => (
          <div
            key={model.id}
            className={`
              model-selector-item
              ${selectedModelId === model.id ? 'model-selector-item-selected' : ''}
            `}
            onClick={() => onSelectModel(model.id)}
          >
            <h4 className="model-selector-item-title">{model.name}</h4>
            <p className="model-selector-item-description">{model.description}</p>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModelSelector;
