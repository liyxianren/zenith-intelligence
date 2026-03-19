import React from 'react';
import Card from '../ui/Card';

interface SolutionDisplayProps {
  solution: string;
}

const SolutionDisplay: React.FC<SolutionDisplayProps> = ({ solution }) => {
  return (
    <Card header={<h3 className="text-lg font-semibold text-dark">解答</h3>}>
      <div className="whitespace-pre-wrap text-gray-800 leading-relaxed">{solution}</div>
    </Card>
  );
};

export default SolutionDisplay;