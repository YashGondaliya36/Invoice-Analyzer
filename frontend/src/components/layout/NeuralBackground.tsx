import React, { useEffect, useRef } from 'react';

const NeuralBackground: React.FC = () => {
    const canvasRef = useRef<HTMLCanvasElement>(null);

    useEffect(() => {
        const canvas = canvasRef.current;
        if (!canvas) return;

        const ctx = canvas.getContext('2d');
        if (!ctx) return;

        let width = canvas.width = window.innerWidth;
        let height = canvas.height = window.innerHeight;

        // Configuration
        const particleCount = 80;
        const connectionDistance = 180;
        const mouseDistance = 250;

        // Particles
        const particles: { x: number; y: number; vx: number; vy: number; size: number }[] = [];
        // Traffic (Data Packets)
        const packets: { p1: number; p2: number; progress: number; speed: number }[] = [];

        for (let i = 0; i < particleCount; i++) {
            particles.push({
                x: Math.random() * width,
                y: Math.random() * height,
                vx: (Math.random() - 0.5) * 0.3,
                vy: (Math.random() - 0.5) * 0.3,
                size: Math.random() * 2 + 1
            });
        }

        let mouse = { x: -1000, y: -1000 };

        const handleMouseMove = (e: MouseEvent) => {
            const rect = canvas.getBoundingClientRect();
            mouse.x = e.clientX - rect.left;
            mouse.y = e.clientY - rect.top;
        };

        const handleResize = () => {
            width = canvas.width = window.innerWidth;
            height = canvas.height = window.innerHeight;
        };

        window.addEventListener('mousemove', handleMouseMove);
        window.addEventListener('resize', handleResize);

        // Animation Loop
        const animate = () => {
            ctx.clearRect(0, 0, width, height);

            // Randomly spawn packets
            if (Math.random() < 0.05) {
                const p1 = Math.floor(Math.random() * particleCount);
                // Find close neighbor
                let closest = -1;
                let minDist = connectionDistance;

                for (let j = 0; j < particleCount; j++) {
                    if (p1 === j) continue;
                    const d = Math.hypot(particles[p1].x - particles[j].x, particles[p1].y - particles[j].y);
                    if (d < minDist) {
                        closest = j;
                        minDist = d;
                    }
                }

                if (closest !== -1) {
                    packets.push({
                        p1,
                        p2: closest,
                        progress: 0,
                        speed: 0.02 + Math.random() * 0.03
                    });
                }
            }


            // Update and draw particles
            particles.forEach((p, i) => {
                p.x += p.vx;
                p.y += p.vy;

                // Bounce off edges
                if (p.x < 0 || p.x > width) p.vx *= -1;
                if (p.y < 0 || p.y > height) p.vy *= -1;

                // Mouse interaction
                const dx = mouse.x - p.x;
                const dy = mouse.y - p.y;
                const dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < mouseDistance) {
                    const force = (mouseDistance - dist) / mouseDistance;
                    p.x -= dx * force * 0.03; // Repel slightly for "organic" feel
                    p.y -= dy * force * 0.03;
                }

                // Draw Particle
                ctx.beginPath();
                ctx.arc(p.x, p.y, p.size, 0, Math.PI * 2);
                ctx.fillStyle = `rgba(168, 162, 158, ${0.2 + (Math.random() * 0.1)})`;
                ctx.fill();

                // Connections
                for (let j = i + 1; j < particles.length; j++) {
                    const p2 = particles[j];
                    const dx2 = p.x - p2.x;
                    const dy2 = p.y - p2.y;
                    const dist2 = Math.sqrt(dx2 * dx2 + dy2 * dy2);

                    if (dist2 < connectionDistance) {
                        ctx.beginPath();
                        ctx.strokeStyle = `rgba(87, 83, 78, ${0.15 * (1 - dist2 / connectionDistance)})`; // Stone-600
                        ctx.lineWidth = 1;
                        ctx.moveTo(p.x, p.y);
                        ctx.lineTo(p2.x, p2.y);
                        ctx.stroke();
                    }
                }
            });

            // Update and draw packets
            for (let i = packets.length - 1; i >= 0; i--) {
                const pkt = packets[i];
                pkt.progress += pkt.speed;

                if (pkt.progress >= 1) {
                    packets.splice(i, 1);
                    continue;
                }

                const p1 = particles[pkt.p1];
                const p2 = particles[pkt.p2];

                // Recalculate distance to ensure link still exists visually (optional, but good for cleanliness)
                const dist = Math.hypot(p1.x - p2.x, p1.y - p2.y);
                if (dist > connectionDistance) {
                    packets.splice(i, 1);
                    continue;
                }

                const x = p1.x + (p2.x - p1.x) * pkt.progress;
                const y = p1.y + (p2.y - p1.y) * pkt.progress;

                ctx.beginPath();
                ctx.arc(x, y, 2, 0, Math.PI * 2);
                ctx.fillStyle = '#f97316'; // Orange Accent (packets)
                ctx.shadowBlur = 4;
                ctx.shadowColor = '#f97316';
                ctx.fill();
                ctx.shadowBlur = 0;
            }

            requestAnimationFrame(animate);
        };

        animate();

        return () => {
            window.removeEventListener('mousemove', handleMouseMove);
            window.removeEventListener('resize', handleResize);
        };
    }, []);

    return (
        <canvas
            ref={canvasRef}
            className="absolute inset-0 pointer-events-none z-0 opacity-40"
            style={{ mixBlendMode: 'screen' }}
        />
    );
};

export default NeuralBackground;
