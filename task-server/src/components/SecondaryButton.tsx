import React from 'react';

interface SecondaryButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  children: React.ReactNode;
}

const SecondaryButton: React.FC<SecondaryButtonProps> = ({ children, disabled, style, ...props }) => {
  const [hovered, setHovered] = React.useState(false);
  let backgroundColor = '#eeeeee';
  if (disabled) {
    backgroundColor = '#e0e0e0'; // distinct disabled color
  } else if (hovered) {
    backgroundColor = '#e0e0e0';
  }

  const baseStyle: React.CSSProperties = {
    padding: '8px 16px',
    backgroundColor,
    color: '#222222',
    border: 'none',
    borderRadius: 8,
    fontSize: '1rem',
    fontWeight: 'bold',
    cursor: disabled ? 'not-allowed' : 'pointer',
    boxShadow: 'none',
    transition: 'all 0.2s ease',
    ...style,
  };

  return (
    <button
      {...props}
      disabled={disabled}
      style={baseStyle}
      onMouseOver={() => !disabled && setHovered(true)}
      onMouseOut={() => setHovered(false)}
    >
      {children}
    </button>
  );
};

export default SecondaryButton;
