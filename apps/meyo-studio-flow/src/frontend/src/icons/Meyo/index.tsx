import type React from "react";
import { forwardRef } from "react";
import meyoIcon from "./meyo-icon-square.png";

type MeyoIconProps = React.ImgHTMLAttributes<HTMLImageElement> & {
  isDark?: boolean;
};

export const MeyoIcon = forwardRef<HTMLImageElement, MeyoIconProps>(
  ({ alt = "Meyo", draggable = false, isDark: _isDark, ...props }, ref) => {
    return (
      <img
        ref={ref}
        src={meyoIcon}
        alt={alt}
        draggable={draggable}
        {...props}
      />
    );
  },
);

MeyoIcon.displayName = "MeyoIcon";
