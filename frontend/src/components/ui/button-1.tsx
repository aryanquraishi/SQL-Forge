'use client';

import type { HTMLAttributes } from 'react';

interface GradientButtonProps extends HTMLAttributes<HTMLDivElement> {
  children?: React.ReactNode;
  width?: string;
  height?: string;
  onClick?: () => void;
  disabled?: boolean;
}

const GradientButton = ({
  children,
  width = '600px',
  height = '100px',
  className = '',
  onClick,
  disabled = false,
  ...props
}: GradientButtonProps) => {
  const handleKeyDown = (e: React.KeyboardEvent<HTMLDivElement>) => {
    if (disabled) return;
    if (e.key === 'Enter' || e.key === ' ') {
      e.preventDefault();
      onClick?.();
    }
  };

  return (
    <div className="text-center">
      <div
        role="button"
        tabIndex={disabled ? -1 : 0}
        className={`
          relative rounded-[50px] cursor-pointer
          after:content-[""] after:block after:absolute after:bg-[var(--color-background,hsl(var(--background)))]
          after:inset-[3px] after:rounded-[47px] after:z-[1]
          after:transition-opacity after:duration-300 after:ease-linear
          flex items-center justify-center
          rotatingGradient
          ${disabled ? 'opacity-50 cursor-not-allowed' : ''}
          ${className}
        `}
        style={{
          '--r': '0deg',
          minWidth: width,
          height: height,
        } as React.CSSProperties}
        onClick={disabled ? undefined : onClick}
        onKeyDown={handleKeyDown}
        aria-disabled={disabled}
        {...props}
      >
        <span className="relative z-10 flex items-center justify-center gap-2 font-bold text-sm">
          {children}
        </span>
      </div>
    </div>
  );
};

export default GradientButton;
