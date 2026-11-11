import type { ButtonHTMLAttributes, ReactNode } from "react";

/** A dark pill button with two glowing "stars" that drift along its top and bottom border. */
export default function StarButton({ children, className = "", ...rest }: { children: ReactNode } & ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <span className={`star-btn ${rest.disabled ? "off" : ""} ${className}`}>
      <span className="star star-bottom" aria-hidden="true" />
      <span className="star star-top" aria-hidden="true" />
      <button {...rest} className="star-inner">{children}</button>
    </span>
  );
}
