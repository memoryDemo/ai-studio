import type React from "react";
import { forwardRef } from "react";
import meyoIcon from "./meyo-icon-square.png";

const MeyoLogo = forwardRef<
  HTMLImageElement,
  React.ImgHTMLAttributes<HTMLImageElement>
>(({ alt = "Meyo", draggable = false, ...props }, ref) => {
  return (
    <img ref={ref} src={meyoIcon} alt={alt} draggable={draggable} {...props} />
  );
});

MeyoLogo.displayName = "MeyoLogo";

export default MeyoLogo;
