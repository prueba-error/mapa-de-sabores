import React, { useState, useRef, useMemo, useCallback } from 'react';
import ForceGraph2D from 'react-force-graph-2d';
import { MOCK_GRAPH_DATA } from './data/mockGraph';
import { Sparkles, Sliders, Info, Eye, Layers } from 'lucide-react';

export default function App() {
  const fgRef = useRef();

  // Estados de control estipulados en SPEC.md (Sección 5)
  const [filterMode, setFilterMode] = useState('all'); // 'best' | 'worst' | 'all'
  const [minScore, setMinScore] = useState(0.0);
  const [selectedNode, setSelectedNode] = useState(null);
  const [hoveredNode, setHoveredNode] = useState(null);
  const [hoveredLink, setHoveredLink] = useState(null);

  // Filtrado reactivo de aristas según controles de usuario
  const filteredData = useMemo(() => {
    let links = MOCK_GRAPH_DATA.links.filter(link => {
      const score = link.affinity_score;
      if (filterMode === 'best') return score >= 0.75;
      if (filterMode === 'worst') return score < 0.45;
      return score >= minScore;
    });

    // Si hay un nodo seleccionado, resaltar solo sus vecinos
    if (selectedNode) {
      links = links.filter(
        link =>
          (link.source.id || link.source) === selectedNode.id ||
          (link.target.id || link.target) === selectedNode.id
      );
    }

    // Incluir nodos asociados a las aristas visibles
    const connectedNodeIds = new Set();
    links.forEach(l => {
      connectedNodeIds.add(l.source.id || l.source);
      connectedNodeIds.add(l.target.id || l.target);
    });

    const nodes = selectedNode
      ? MOCK_GRAPH_DATA.nodes.filter(n => connectedNodeIds.has(n.id) || n.id === selectedNode.id)
      : MOCK_GRAPH_DATA.nodes;

    return { nodes, links };
  }, [filterMode, minScore, selectedNode]);

  // Color de aristas según SPEC.md: verde (>0.75), amarillo (0.45-0.75), rojo (<0.45)
  const getLinkColor = useCallback((link) => {
    if (hoveredLink === link) return '#FFFFFF';
    const s = link.affinity_score;
    if (s >= 0.75) return '#2ECC71'; // Verde sinérgico
    if (s >= 0.45) return '#F39C12'; // Amarillo armónico
    return '#E74C3C'; // Rojo discordante
  }, [hoveredLink]);

  // Manejador de click en nodo para centrado suave
  const handleNodeClick = useCallback((node) => {
    if (selectedNode && selectedNode.id === node.id) {
      setSelectedNode(null);
      if (fgRef.current) fgRef.current.zoomToFit(400);
    } else {
      setSelectedNode(node);
      if (fgRef.current) {
        fgRef.current.centerAt(node.x, node.y, 400);
        fgRef.current.zoom(2.5, 400);
      }
    }
  }, [selectedNode]);

  return (
    <div style={{ display: 'flex', width: '100vw', height: '100vh', background: '#0F172A', color: '#F8FAFC', fontFamily: 'system-ui, sans-serif', overflow: 'hidden' }}>
      {/* Panel Lateral de Controles (Spike de Usabilidad) */}
      <aside style={{ width: '340px', background: '#1E293B', borderRight: '1px solid #334155', padding: '20px', display: 'flex', flexDirection: 'column', gap: '20px', zIndex: 10, overflowY: 'auto' }}>
        <div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '8px', color: '#38BDF8' }}>
            <Sparkles size={22} />
            <h1 style={{ fontSize: '18px', fontWeight: 'bold', margin: 0 }}>Mapa de Sabores</h1>
          </div>
          <p style={{ fontSize: '12px', color: '#94A3B8', marginTop: '4px' }}>
            Spike de Renderizado 2D (Canvas 60 FPS)
          </p>
        </div>

        {/* Filtros de Afinidad */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '10px' }}>
          <label style={{ fontSize: '13px', fontWeight: '600', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Sliders size={16} /> Modo de Exploración
          </label>
          <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '6px' }}>
            {['all', 'best', 'worst'].map((mode) => (
              <button
                key={mode}
                onClick={() => { setFilterMode(mode); setSelectedNode(null); }}
                style={{
                  padding: '8px 4px',
                  borderRadius: '6px',
                  border: filterMode === mode ? '2px solid #38BDF8' : '1px solid #475569',
                  background: filterMode === mode ? '#0284C7' : '#334155',
                  color: '#FFF',
                  fontSize: '12px',
                  fontWeight: '600',
                  cursor: 'pointer',
                  textTransform: 'capitalize'
                }}
              >
                {mode === 'all' ? 'Todas' : mode === 'best' ? 'Mejores' : 'Peores'}
              </button>
            ))}
          </div>
        </div>

        {filterMode === 'all' && (
          <div style={{ display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', fontSize: '12px' }}>
              <span>Piso de afinidad:</span>
              <span style={{ fontWeight: 'bold', color: '#38BDF8' }}>{minScore.toFixed(2)}</span>
            </div>
            <input
              type="range"
              min="0.0"
              max="0.90"
              step="0.05"
              value={minScore}
              onChange={(e) => setMinScore(parseFloat(e.target.value))}
              style={{ width: '100%', cursor: 'pointer' }}
            />
          </div>
        )}

        {/* Leyenda de Aristas según SPEC.md */}
        <div style={{ background: '#0F172A', padding: '12px', borderRadius: '8px', border: '1px solid #334155' }}>
          <span style={{ fontSize: '12px', fontWeight: 'bold', display: 'flex', alignItems: 'center', gap: '6px', marginBottom: '8px' }}>
            <Layers size={14} /> Código de Color de Aristas
          </span>
          <div style={{ display: 'flex', flexDirection: 'column', gap: '6px', fontSize: '12px' }}>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#2ECC71' }}></span>
              <span>Alta sinergia (&gt; 0.75)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#F39C12' }}></span>
              <span>Armonía complementaria (0.45 - 0.75)</span>
            </div>
            <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
              <span style={{ width: '12px', height: '12px', borderRadius: '50%', background: '#E74C3C' }}></span>
              <span>Discordante / Antagónico (&lt; 0.45)</span>
            </div>
          </div>
        </div>

        {/* Ficha Rápida del Nodo Seleccionado */}
        {selectedNode ? (
          <div style={{ background: '#0F172A', padding: '14px', borderRadius: '8px', border: '1px solid #38BDF8', display: 'flex', flexDirection: 'column', gap: '8px' }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
              <span style={{ fontSize: '14px', fontWeight: 'bold', color: selectedNode.color }}>{selectedNode.name}</span>
              <span style={{ fontSize: '11px', background: '#334155', padding: '2px 6px', borderRadius: '4px' }}>{selectedNode.category}</span>
            </div>
            <p style={{ fontSize: '12px', color: '#94A3B8', margin: 0 }}>
              Nodo enfocado. Mostrando vecinos directos en el grafo.
            </p>
            <button
              onClick={() => { setSelectedNode(null); if (fgRef.current) fgRef.current.zoomToFit(400); }}
              style={{ padding: '6px', fontSize: '12px', background: '#334155', border: 'none', borderRadius: '4px', color: '#FFF', cursor: 'pointer', marginTop: '6px' }}
            >
              Restablecer Enfoque
            </button>
          </div>
        ) : (
          <div style={{ fontSize: '12px', color: '#64748B', display: 'flex', alignItems: 'center', gap: '6px' }}>
            <Info size={14} /> Hacé clic en cualquier nodo para centrar y aislar sus conexiones.
          </div>
        )}

        {/* Métricas del Spike */}
        <div style={{ marginTop: 'auto', fontSize: '11px', color: '#64748B', borderTop: '1px solid #334155', paddingTop: '10px' }}>
          <div>Nodos visibles: {filteredData.nodes.length}</div>
          <div>Aristas visibles: {filteredData.links.length}</div>
          <div>Render: Canvas HTML5 @ ~60 FPS</div>
        </div>
      </aside>

      {/* Área del Canvas Interactivo con react-force-graph-2d */}
      <main style={{ flex: 1, position: 'relative', height: '100%' }}>
        <ForceGraph2D
          ref={fgRef}
          graphData={filteredData}
          backgroundColor="#0F172A"
          nodeId="id"
          nodeVal="val"
          nodeLabel={(n) => `${n.name} (${n.category})`}
          nodeColor={(n) => n.color}
          nodeRelSize={4}
          linkColor={getLinkColor}
          linkWidth={(l) => Math.max(1, (l.affinity_score || 0.5) * 3)}
          linkLineDash={(l) => (l.affinity_score < 0.45 ? [3, 2] : null)} // Línea punteada para pares discordantes
          linkDirectionalParticles={1}
          linkDirectionalParticleWidth={(l) => (l.affinity_score >= 0.75 ? 2 : 0)}
          linkDirectionalParticleSpeed={(l) => (l.affinity_score >= 0.75 ? 0.005 : 0)}
          onNodeClick={handleNodeClick}
          onNodeHover={setHoveredNode}
          onLinkHover={setHoveredLink}
          cooldownTicks={100}
          onEngineStop={() => {
            if (fgRef.current && !selectedNode) fgRef.current.zoomToFit(400, 40);
          }}
          nodeCanvasObject={(node, ctx, globalScale) => {
            // Renderizado Canvas personalizado: círculo coloreado + etiqueta legible
            const label = node.name;
            const fontSize = 12 / globalScale;
            const r = 5;

            // Círculo del nodo
            ctx.beginPath();
            ctx.arc(node.x, node.y, r, 0, 2 * Math.PI, false);
            ctx.fillStyle = node.color || '#38BDF8';
            ctx.fill();

            if (selectedNode && selectedNode.id === node.id) {
              ctx.lineWidth = 2 / globalScale;
              ctx.strokeStyle = '#FFFFFF';
              ctx.stroke();
            }

            // Etiqueta del ingrediente
            if (globalScale >= 1.2 || (selectedNode && selectedNode.id === node.id) || (hoveredNode && hoveredNode.id === node.id)) {
              ctx.font = `${fontSize}px system-ui`;
              ctx.textAlign = 'center';
              ctx.textBaseline = 'top';
              ctx.fillStyle = '#F8FAFC';
              ctx.fillText(label, node.x, node.y + r + 2);
            }
          }}
        />

        {/* Tooltip flotante al pasar el mouse por aristas */}
        {hoveredLink && (
          <div style={{
            position: 'absolute',
            bottom: '20px',
            right: '20px',
            background: 'rgba(15, 23, 42, 0.95)',
            border: '1px solid #38BDF8',
            padding: '12px 16px',
            borderRadius: '8px',
            fontSize: '12px',
            maxWidth: '320px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            pointerEvents: 'none'
          }}>
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: '6px' }}>
              <span style={{ fontWeight: 'bold' }}>Maridaje Molecular</span>
              <span style={{ color: '#38BDF8', fontWeight: 'bold' }}>
                Score: {hoveredLink.affinity_score.toFixed(2)}
              </span>
            </div>
            <p style={{ margin: 0, color: '#94A3B8' }}>{hoveredLink.rationale}</p>
          </div>
        )}
      </main>
    </div>
  );
}
