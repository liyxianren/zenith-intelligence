import React from 'react';
import type { ReactNode } from 'react';

interface CardProps {
  children: ReactNode;
  className?: string;
  header?: ReactNode;
  footer?: ReactNode;
  shadow?: 'sm' | 'md' | 'lg' | 'xl';
  border?: boolean;
  hover?: boolean;
  padding?: 'sm' | 'md' | 'lg';
  style?: React.CSSProperties;
}

const Card: React.FC<CardProps> = ({
  children,
  className = '',
  header,
  footer,
  shadow = 'md',
  border = true,
  hover = true,
  padding = 'md',
  style,
}) => {
  const shadowClasses = {
    sm: 'shadow-sm',
    md: 'shadow-md',
    lg: 'shadow-lg',
    xl: 'shadow-xl',
  };

  const paddingClasses = {
    sm: 'p-4',
    md: 'p-6',
    lg: 'p-8',
  };

  return (
    <div 
      className={`
        bg-white
        rounded-xl
        ${border ? 'border border-gray-200' : ''}
        ${shadowClasses[shadow]}
        ${hover ? 'card-hover transition-all duration-300 hover:border-primary/50 hover:shadow-lg' : ''}
        ${className}
        group
      `}
      style={style}
    >
      {header && (
        <div className={`border-b border-gray-200 ${paddingClasses[padding]} group-hover:border-gray-300 transition-colors duration-300`}>
          {header}
        </div>
      )}
      <div className={paddingClasses[padding]}>
        {children}
      </div>
      {footer && (
        <div className={`border-t border-gray-200 ${paddingClasses[padding]} group-hover:border-gray-300 transition-colors duration-300`}>
          {footer}
        </div>
      )}
    </div>
  );
};

export default Card;