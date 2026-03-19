import React from 'react';
import type { ButtonHTMLAttributes } from 'react';

interface ButtonProps extends ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: 'primary' | 'secondary' | 'accent' | 'outline' | 'ghost';
  size?: 'sm' | 'md' | 'lg';
  fullWidth?: boolean;
  loading?: boolean;
  icon?: React.ReactNode;
  iconPosition?: 'left' | 'right';
  asChild?: boolean;
}

const Button: React.FC<ButtonProps> = ({
  children,
  variant = 'primary',
  size = 'md',
  fullWidth = false,
  loading = false,
  icon,
  iconPosition = 'left',
  className = '',
  asChild = false,
  ...props
}) => {
  const buttonClasses = `
    btn
    btn-${variant}
    btn-${size}
    ${fullWidth ? 'btn-full-width' : ''}
    ${loading ? 'btn-loading' : ''}
    ${className}
    group
  `;

  const buttonContent = (
    <>
      {loading ? (
        <div className="flex items-center justify-center">
          <div className="w-4 h-4 border-2 border-white border-t-transparent rounded-full animate-spin mr-2"></div>
          {children}
        </div>
      ) : (
        <div className="flex items-center justify-center gap-2 group-hover:gap-3 transition-all duration-300">
          {icon && iconPosition === 'left' && (
            <span className="group-hover:scale-110 transition-transform duration-300">
              {icon}
            </span>
          )}
          <span className="group-hover:scale-105 transition-transform duration-300">
            {children}
          </span>
          {icon && iconPosition === 'right' && (
            <span className="group-hover:scale-110 transition-transform duration-300">
              {icon}
            </span>
          )}
        </div>
      )}
    </>
  );

  if (asChild && React.isValidElement(children)) {
    const childElement = children as React.ReactElement<{ className?: string }>;
    return React.cloneElement(childElement, {
      className: `${childElement.props.className || ''} ${buttonClasses}`.trim(),
      ...props
    });
  }

  return (
    <button
      className={buttonClasses}
      disabled={loading}
      {...props}
    >
      {buttonContent}
    </button>
  );
};

export default Button;