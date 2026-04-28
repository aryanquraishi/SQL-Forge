export function SQLForgeLogo({ size = 40 }: { size?: number }) {
  return (
    <svg width={size} height={size} viewBox="0 0 60 60" xmlns="http://www.w3.org/2000/svg">
      <polygon points="30,2 55,16 55,44 30,58 5,44 5,16" fill="#D4691E"/>
      <path d="M33 11 L26 24 L31 24 L27 33 L37 20 L32 20 Z" fill="white"/>
      <path d="M19 36 Q30 39 41 36" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
      <line x1="19" y1="36" x2="19" y2="46" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
      <line x1="41" y1="36" x2="41" y2="46" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
      <path d="M19 41 Q30 44 41 41" fill="none" stroke="white" strokeWidth="1.4" strokeLinecap="round"/>
      <path d="M19 46 Q30 49 41 46" fill="none" stroke="white" strokeWidth="1.8" strokeLinecap="round"/>
    </svg>
  );
}
