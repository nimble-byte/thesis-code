import React from 'react';

interface PrimaryButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}


const PrimaryButton: React.FC<PrimaryButtonProps> = ({ children, disabled, style, ...props }) => {
  const [hovered, setHovered] = React.useState(false);
  let backgroundColor = '#0070f3';
  if (disabled) {
    backgroundColor = '#b3c6e6';
  } else if (hovered) {
    backgroundColor = '#0051cc';
  }

  const baseStyle: React.CSSProperties = {
    padding: '12px 12px',
    backgroundColor,
    color: 'white',
    border: 'none',
    borderRadius: '8px',
    fontSize: '1rem',
    fontWeight: 'bold',
    cursor: disabled ? 'not-allowed' : 'pointer',
    boxShadow: '0 4px 12px rgba(0, 112, 243, 0.3)',
    transition: 'all 0.2s ease',
    ...style,
  };

  return (
    <button
      {...props}
      disabled={disabled}
      style={{
        ...baseStyle,
        transform: hovered && !disabled ? 'translateY(-2px)' : 'translateY(0)',
      }}
      onMouseOver={() => !disabled && setHovered(true)}
      onMouseOut={() => setHovered(false)}
    >
      {children}
    </button>
  );
};

export default PrimaryButton;
