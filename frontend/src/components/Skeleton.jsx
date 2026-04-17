import React from 'react';

export const SkeletonBox = ({ width = '100%', height = '100%', borderRadius = '8px', className = '', style = {} }) => (
  <div 
    className={`skeleton ${className}`}
    style={{ width, height, borderRadius, ...style }}
  />
);

export const SkeletonText = ({ lines = 1, width = '100%', lastLineWidth = '60%', className = '' }) => (
  <div className={`flex flex-col gap-2 ${className}`}>
    {Array.from({ length: lines }).map((_, i) => (
      <SkeletonBox 
        key={i} 
        height="1rem" 
        width={i === lines - 1 && lines > 1 ? lastLineWidth : width}
        borderRadius="4px"
      />
    ))}
  </div>
);

export const SkeletonCard = ({ className = '' }) => (
  <div className={`p-5 rounded-2xl bg-[#111116] border border-white/5 shadow-xl flex flex-col gap-4 ${className}`}>
    <div className="flex justify-between items-center">
      <SkeletonBox width="40%" height="24px" />
      <SkeletonBox width="32px" height="32px" borderRadius="50%" />
    </div>
    <SkeletonBox width="60%" height="32px" />
    <SkeletonBox width="80%" height="16px" />
  </div>
);

// High end shimmering container for graphs
export const SkeletonGraph = ({ className = '' }) => (
  <div className={`p-6 rounded-2xl bg-[#111116] border border-white/5 shadow-xl ${className}`}>
    <SkeletonBox width="30%" height="24px" className="mb-6" />
    <SkeletonBox width="100%" height="220px" borderRadius="12px" />
  </div>
);
