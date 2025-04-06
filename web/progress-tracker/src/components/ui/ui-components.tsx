// 苹果风格UI组件库
// 这个文件包含了符合苹果设计语言的UI组件

'use client';

import React from 'react';
import { cva } from 'class-variance-authority';
import { twMerge } from 'tailwind-merge';

// 按钮组件
export const buttonVariants = cva(
  "inline-flex items-center justify-center rounded-md text-sm font-medium transition-colors focus-visible:outline-none focus-visible:ring-2 focus-visible:ring-offset-2 disabled:opacity-50 disabled:pointer-events-none",
  {
    variants: {
      variant: {
        primary: "bg-blue-600 text-white hover:bg-blue-700 focus-visible:ring-blue-500",
        secondary: "bg-gray-100 text-gray-900 hover:bg-gray-200 focus-visible:ring-gray-500",
        outline: "border border-gray-300 bg-transparent hover:bg-gray-50 focus-visible:ring-gray-500",
        ghost: "hover:bg-gray-50 focus-visible:ring-gray-500",
        link: "text-blue-600 underline-offset-4 hover:underline focus-visible:ring-blue-500",
        danger: "bg-red-600 text-white hover:bg-red-700 focus-visible:ring-red-500",
      },
      size: {
        sm: "h-8 px-3 text-xs",
        md: "h-10 px-4",
        lg: "h-12 px-6 text-lg",
      },
    },
    defaultVariants: {
      variant: "primary",
      size: "md",
    },
  }
);

export const Button = React.forwardRef(
  ({ className, variant, size, ...props }, ref) => {
    return (
      <button
        className={twMerge(buttonVariants({ variant, size, className }))}
        ref={ref}
        {...props}
      />
    );
  }
);
Button.displayName = "Button";

// 卡片组件
export const Card = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge("bg-white rounded-xl shadow-sm overflow-hidden", className)}
        {...props}
      />
    );
  }
);
Card.displayName = "Card";

export const CardHeader = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge("p-6", className)}
        {...props}
      />
    );
  }
);
CardHeader.displayName = "CardHeader";

export const CardTitle = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <h3
        ref={ref}
        className={twMerge("text-lg font-semibold text-gray-900", className)}
        {...props}
      />
    );
  }
);
CardTitle.displayName = "CardTitle";

export const CardDescription = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={twMerge("text-sm text-gray-500", className)}
        {...props}
      />
    );
  }
);
CardDescription.displayName = "CardDescription";

export const CardContent = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge("p-6 pt-0", className)}
        {...props}
      />
    );
  }
);
CardContent.displayName = "CardContent";

export const CardFooter = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge("bg-gray-50 px-6 py-3 flex items-center", className)}
        {...props}
      />
    );
  }
);
CardFooter.displayName = "CardFooter";

// 输入框组件
export const Input = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <input
        className={twMerge(
          "flex h-10 w-full rounded-md border border-gray-300 bg-white px-3 py-2 text-sm placeholder:text-gray-400 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:border-blue-500 disabled:cursor-not-allowed disabled:opacity-50",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Input.displayName = "Input";

// 标签组件
export const Label = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <label
        className={twMerge(
          "text-sm font-medium text-gray-700",
          className
        )}
        ref={ref}
        {...props}
      />
    );
  }
);
Label.displayName = "Label";

// 徽章组件
export const badgeVariants = cva(
  "inline-flex items-center rounded-full px-2 py-1 text-xs font-semibold",
  {
    variants: {
      variant: {
        default: "bg-gray-100 text-gray-800",
        primary: "bg-blue-100 text-blue-800",
        secondary: "bg-gray-100 text-gray-800",
        success: "bg-green-100 text-green-800",
        warning: "bg-yellow-100 text-yellow-800",
        danger: "bg-red-100 text-red-800",
      },
    },
    defaultVariants: {
      variant: "default",
    },
  }
);

export const Badge = React.forwardRef(
  ({ className, variant, ...props }, ref) => {
    return (
      <span
        ref={ref}
        className={twMerge(badgeVariants({ variant }), className)}
        {...props}
      />
    );
  }
);
Badge.displayName = "Badge";

// 进度条组件
export const Progress = React.forwardRef(
  ({ className, value = 0, max = 100, ...props }, ref) => {
    const percentage = (value / max) * 100;
    
    return (
      <div
        ref={ref}
        className={twMerge("w-full bg-gray-200 rounded-full h-2", className)}
        {...props}
      >
        <div
          className="bg-blue-600 h-2 rounded-full"
          style={{ width: `${percentage}%` }}
        />
      </div>
    );
  }
);
Progress.displayName = "Progress";

// 头像组件
export const Avatar = React.forwardRef(
  ({ className, src, alt, initials, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge(
          "relative flex h-10 w-10 shrink-0 overflow-hidden rounded-full",
          className
        )}
        {...props}
      >
        {src ? (
          <img
            src={src}
            alt={alt}
            className="h-full w-full object-cover"
          />
        ) : (
          <div className="flex h-full w-full items-center justify-center bg-blue-500 text-white">
            {initials || "U"}
          </div>
        )}
      </div>
    );
  }
);
Avatar.displayName = "Avatar";

// 导航链接组件
export const NavLink = React.forwardRef(
  ({ className, active, ...props }, ref) => {
    return (
      <a
        ref={ref}
        className={twMerge(
          "inline-flex items-center px-4 py-2 text-sm font-medium transition-colors",
          active
            ? "text-blue-600"
            : "text-gray-700 hover:text-blue-600",
          className
        )}
        {...props}
      />
    );
  }
);
NavLink.displayName = "NavLink";

// 分隔线组件
export const Separator = React.forwardRef(
  ({ className, orientation = "horizontal", ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge(
          "shrink-0 bg-gray-200",
          orientation === "horizontal" ? "h-[1px] w-full" : "h-full w-[1px]",
          className
        )}
        {...props}
      />
    );
  }
);
Separator.displayName = "Separator";

// 容器组件
export const Container = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <div
        ref={ref}
        className={twMerge("mx-auto max-w-7xl px-4 sm:px-6 lg:px-8", className)}
        {...props}
      />
    );
  }
);
Container.displayName = "Container";

// 页面标题组件
export const PageTitle = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <h1
        ref={ref}
        className={twMerge("text-2xl font-semibold text-gray-900", className)}
        {...props}
      />
    );
  }
);
PageTitle.displayName = "PageTitle";

// 页面描述组件
export const PageDescription = React.forwardRef(
  ({ className, ...props }, ref) => {
    return (
      <p
        ref={ref}
        className={twMerge("text-gray-500", className)}
        {...props}
      />
    );
  }
);
PageDescription.displayName = "PageDescription";

// 警告提示组件
export const Alert = React.forwardRef(
  ({ className, variant = "default", children, ...props }, ref) => {
    const variantClasses = {
      default: "bg-gray-50 border-gray-500 text-gray-700",
      info: "bg-blue-50 border-blue-500 text-blue-700",
      success: "bg-green-50 border-green-500 text-green-700",
      warning: "bg-yellow-50 border-yellow-500 text-yellow-700",
      error: "bg-red-50 border-red-500 text-red-700",
    };
    
    return (
      <div
        ref={ref}
        className={twMerge(
          "border-l-4 p-4",
          variantClasses[variant],
          className
        )}
        {...props}
      >
        {children}
      </div>
    );
  }
);
Alert.displayName = "Alert";
