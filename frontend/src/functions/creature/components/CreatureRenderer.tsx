import { Application, extend } from "@pixi/react";
import { useCallback, useRef } from "react";
import { Container, Graphics } from "pixi.js";
import type { Graphics as PixiGraphics } from "pixi.js";

extend({ Container, Graphics });

const BIOME_COLORS: Record<string, number> = {
  mountain: 0x4a5568,
  forest: 0x2d6a4f,
  ocean: 0x1a4a7a,
  marine: 0x0d7377,
  plains: 0x7a6a2d,
};
const DEFAULT_BG = 0x2a2a4a;

interface Props {
  biomeId: string | null;
  bodyColor?: number;
}

export function CreatureRenderer({ biomeId, bodyColor = 0xe94560 }: Props) {
  const containerRef = useRef<HTMLDivElement>(null);

  const drawBg = useCallback(
    (g: PixiGraphics) => {
      const color = biomeId !== null ? (BIOME_COLORS[biomeId] ?? DEFAULT_BG) : DEFAULT_BG;
      g.clear();
      g.rect(0, 0, 800, 800);
      g.fill({ color });
    },
    [biomeId],
  );

  const drawBody = useCallback(
    (g: PixiGraphics) => {
      g.clear();
      g.ellipse(0, 0, 70, 90);
      g.fill({ color: bodyColor });
    },
    [bodyColor],
  );

  const drawEyes = useCallback((g: PixiGraphics) => {
    g.clear();
    g.circle(-18, -20, 10);
    g.circle(18, -20, 10);
    g.fill({ color: 0xffffff });
    g.circle(-18, -20, 5);
    g.circle(18, -20, 5);
    g.fill({ color: 0x111111 });
  }, []);

  return (
    <div ref={containerRef} className="creature-canvas">
      <Application
        resizeTo={containerRef as React.RefObject<HTMLElement>}
        backgroundAlpha={0}
        antialias
      >
        {/* Ambiance layer */}
        <pixiGraphics draw={drawBg} />

        {/* Body */}
        <pixiContainer x={400} y={400}>
          <pixiGraphics draw={drawBody} />
          <pixiGraphics draw={drawEyes} />
        </pixiContainer>
      </Application>
    </div>
  );
}
