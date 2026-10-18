import { type CSSProperties, type ReactNode, useEffect, useRef, useState } from "react"

type Props = {
  children: ReactNode
}

export function ShopWindow({ children }: Props) {
  const sceneRef = useRef<HTMLDivElement>(null)
  const dragging = useRef(false)
  const last = useRef({ x: 0, y: 0 })
  const [rot, setRot] = useState({ x: -10, y: 18 })
  const [grabbing, setGrabbing] = useState(false)
  const [enter, setEnter] = useState(0)

  useEffect(() => {
    const scene = sceneRef.current
    if (!scene) return
    const reduced = window.matchMedia?.("(prefers-reduced-motion: reduce)")
    const onScroll = () => {
      if (reduced?.matches) {
        setEnter(0)
        return
      }
      const rect = scene.getBoundingClientRect()
      const span = Math.max(rect.height * 0.55, 1)
      setEnter(Math.min(Math.max(-rect.top / span, 0), 1))
    }
    onScroll()
    window.addEventListener("scroll", onScroll, { passive: true })
    window.addEventListener("resize", onScroll)
    return () => {
      window.removeEventListener("scroll", onScroll)
      window.removeEventListener("resize", onScroll)
    }
  }, [])

  return (
    <div
      className="shop-scene"
      data-testid="shop-window"
      ref={sceneRef}
      style={{ "--enter": String(enter) } as CSSProperties}
    >
      <div className="shop-sticky">
        <p className="shop-kicker">Sykes shops with you</p>
        <h1 className="shop-title font-heading">Find a deal you can actually pay for</h1>
        <div
          className={grabbing ? "shop-orb is-dragging" : "shop-orb"}
          data-testid="shop-orb"
          role="img"
          aria-label="Shop globe. Drag to turn."
          style={{
            transform: `rotateX(${rot.x + enter * 42}deg) rotateY(${rot.y}deg) translateZ(${enter * 80}px)`,
          }}
          onPointerDown={(event) => {
            dragging.current = true
            setGrabbing(true)
            last.current = { x: event.clientX, y: event.clientY }
            event.currentTarget.setPointerCapture(event.pointerId)
          }}
          onPointerMove={(event) => {
            if (!dragging.current) return
            const dx = event.clientX - last.current.x
            const dy = event.clientY - last.current.y
            last.current = { x: event.clientX, y: event.clientY }
            setRot((value) => ({
              x: Math.max(-38, Math.min(32, value.x - dy * 0.38)),
              y: value.y + dx * 0.5,
            }))
          }}
          onPointerUp={() => {
            dragging.current = false
            setGrabbing(false)
          }}
          onPointerCancel={() => {
            dragging.current = false
            setGrabbing(false)
          }}
        >
          <div className="shop-orb-scene">
            <span className="shop-orb-ring" />
            <span className="shop-orb-ring shop-orb-ring-b" />
            <span className="shop-orb-sphere">
              <span className="shop-orb-glint" />
              <span className="shop-orb-store">
                <span className="shop-orb-awning" />
                <span className="shop-orb-facade">
                  <span className="shop-orb-pane" />
                  <span className="shop-orb-door" />
                </span>
              </span>
            </span>
          </div>
        </div>
        <div className="shop-counter">{children}</div>
        <p className="shop-hint">Drag to turn the shop. Keep scrolling.</p>
      </div>
    </div>
  )
}
