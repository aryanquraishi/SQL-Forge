"use client";

import { useEffect, useRef } from 'react';

interface ConfettiPiece {
  x: number; y: number; z: number;
  velocityX: number; velocityY: number; velocityZ: number;
  rotation: number; rotationSpeed: number;
  baseSize: number; opacity: number;
  shape: 'rectangle' | 'circle' | 'star' | 'diamond';
  color: string;
  floatPhase: number; swayAmplitude: number; bobAmplitude: number;
  isFading: boolean;
}

export default function ConfettiBackground() {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const animationRef = useRef<number | null>(null);
  const confettiRef = useRef<ConfettiPiece[]>([]);

  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;
    const ctx = canvas.getContext('2d');
    if (!ctx) return;

    const resizeCanvas = () => {
      const parent = canvas.parentElement;
      if (parent) {
        canvas.width = parent.clientWidth;
        canvas.height = parent.clientHeight;
      } else {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
      }
    };
    resizeCanvas();
    window.addEventListener('resize', resizeCanvas);

    const getColors = () => {
      const isDark = document.documentElement.classList.contains('dark');
      return isDark
        ? ['rgba(212,105,30,0.12)', 'rgba(232,137,74,0.08)', 'rgba(255,255,255,0.06)', 'rgba(168,77,18,0.10)', 'rgba(255,200,150,0.05)']
        : ['rgba(212,105,30,0.10)', 'rgba(232,137,74,0.07)', 'rgba(180,170,158,0.08)', 'rgba(168,77,18,0.06)', 'rgba(120,113,108,0.05)'];
    };

    const createPiece = (): ConfettiPiece => {
      const colors = getColors();
      return {
        x: -canvas.width * 0.2 + Math.random() * canvas.width * 1.4,
        y: -Math.random() * canvas.height * 0.3,
        z: Math.random() * 1500 + 800,
        velocityX: (Math.random() - 0.5) * 0.4,
        velocityY: Math.random() * 0.2 + 0.08,
        velocityZ: -(Math.random() * 0.4 + 0.2),
        rotation: Math.random() * Math.PI * 2,
        rotationSpeed: (Math.random() - 0.5) * 0.03,
        baseSize: Math.random() * 10 + 5,
        opacity: 1,
        shape: (['rectangle', 'circle', 'star', 'diamond'] as const)[Math.floor(Math.random() * 4)],
        color: colors[Math.floor(Math.random() * colors.length)],
        floatPhase: Math.random() * Math.PI * 2,
        swayAmplitude: Math.random() * 0.4 + 0.15,
        bobAmplitude: Math.random() * 0.2 + 0.08,
        isFading: false,
      };
    };

    confettiRef.current = Array.from({ length: 100 }, createPiece);

    const drawPiece = (p: ConfettiPiece) => {
      const perspective = 800;
      const scale = perspective / (perspective + p.z);
      if (scale <= 0.01 || scale > 2) return;
      const px = p.x + (p.x - canvas.width / 2) * (1 - scale);
      const py = p.y + (p.y - canvas.height / 2) * (1 - scale);
      const size = p.baseSize * scale;
      ctx.save();
      ctx.translate(px, py);
      ctx.rotate(p.rotation);
      ctx.globalAlpha = Math.min(p.opacity * scale * 1.5, 1);
      ctx.fillStyle = p.color;
      switch (p.shape) {
        case 'rectangle': ctx.fillRect(-size * 0.75, -size * 0.4, size * 1.5, size * 0.8); break;
        case 'circle': ctx.beginPath(); ctx.arc(0, 0, size * 0.5, 0, Math.PI * 2); ctx.fill(); break;
        case 'star':
          ctx.beginPath();
          for (let i = 0; i < 6; i++) {
            const a = (i * Math.PI) / 3, ia = ((i + 0.5) * Math.PI) / 3;
            if (i === 0) ctx.moveTo(Math.cos(a) * size * 0.6, Math.sin(a) * size * 0.6);
            else ctx.lineTo(Math.cos(a) * size * 0.6, Math.sin(a) * size * 0.6);
            ctx.lineTo(Math.cos(ia) * size * 0.3, Math.sin(ia) * size * 0.3);
          }
          ctx.closePath(); ctx.fill(); break;
        case 'diamond':
          ctx.beginPath();
          ctx.moveTo(0, -size * 0.7); ctx.lineTo(size * 0.4, 0);
          ctx.lineTo(0, size * 0.7); ctx.lineTo(-size * 0.4, 0);
          ctx.closePath(); ctx.fill(); break;
      }
      ctx.restore();
    };

    const animate = () => {
      ctx.clearRect(0, 0, canvas.width, canvas.height);
      confettiRef.current.forEach(p => {
        p.floatPhase += 0.015;
        p.x += p.velocityX + Math.sin(p.floatPhase) * p.swayAmplitude * 0.2;
        p.y += p.velocityY + Math.cos(p.floatPhase * 0.7) * p.bobAmplitude * 0.15;
        p.z += p.velocityZ;
        p.rotation += p.rotationSpeed;
        p.velocityX += (Math.random() - 0.5) * 0.003;
        p.velocityY += 0.0003;
        p.velocityX *= 0.999; p.velocityY *= 0.999;
        if (!p.isFading && (p.z <= 200 || p.x < -100 || p.x > canvas.width + 100 || p.y > canvas.height + 100)) p.isFading = true;
        if (p.isFading) p.opacity -= 0.015;
        if (p.opacity <= 0) Object.assign(p, createPiece());
        drawPiece(p);
      });
      animationRef.current = requestAnimationFrame(animate);
    };
    animate();

    return () => { window.removeEventListener('resize', resizeCanvas); if (animationRef.current) cancelAnimationFrame(animationRef.current); };
  }, []);

  return <canvas ref={canvasRef} className="absolute inset-0 pointer-events-none z-0" style={{ background: 'transparent' }} />;
}
