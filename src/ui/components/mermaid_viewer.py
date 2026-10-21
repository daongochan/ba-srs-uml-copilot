"""Mermaid SVG Interactive Viewer Component.

Nhúng thư viện Mermaid.js từ CDN và render sơ đồ tương tác (Interactive SVG Canvas)
với thanh công cụ nổi (Zoom In, Zoom Out, Reset, Download SVG), hỗ trợ kéo rê (Pan)
và phóng to thu nhỏ (Zoom), kết hợp cơ chế Lazy Visibility Rendering để tránh lỗi khi tab đang ẩn.
"""

import json
import streamlit.components.v1 as components
from src.validators.syntax_validator import clean_and_validate_mermaid


def render_mermaid(mermaid_code: str, height: int = 560, diagram_type: str = "") -> None:
    """Nhúng thư viện Mermaid.js từ CDN và render sơ đồ tương tác (Interactive SVG Canvas)
    với thanh công cụ nổi (Zoom In, Zoom Out, Reset, Download SVG), hỗ trợ kéo rê (Pan)
    và phóng to thu nhỏ (Zoom), kết hợp cơ chế Lazy Visibility Rendering để tránh lỗi khi tab đang ẩn.
    """
    try:
        clean_code = clean_and_validate_mermaid(mermaid_code, diagram_type=diagram_type)
    except Exception:
        clean_code = mermaid_code.strip()

    code_json = json.dumps(clean_code)

    html_content = f"""
    <!DOCTYPE html>
    <html lang="vi">
    <head>
        <meta charset="utf-8">
        <script src="https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.min.js"></script>
        <style>
            * {{
                box-sizing: border-box;
            }}
            body {{
                margin: 0;
                padding: 0;
                background-color: #f8fafc;
                font-family: 'Inter', system-ui, -apple-system, sans-serif;
                overflow: hidden;
                width: 100vw;
                height: 100vh;
            }}
            #viewport {{
                position: relative;
                width: 100%;
                height: 100%;
                overflow: hidden;
                background: #ffffff;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                box-shadow: 0 1px 3px rgba(0,0,0,0.05);
                cursor: grab;
                user-select: none;
            }}
            #viewport.dragging {{
                cursor: grabbing;
            }}
            #canvas {{
                position: absolute;
                top: 0;
                left: 0;
                transform-origin: 0 0;
                will-change: transform;
            }}
            #mermaid-container {{
                padding: 32px;
                display: inline-block;
                min-width: 300px;
                min-height: 200px;
            }}
            #toolbar {{
                position: absolute;
                top: 12px;
                right: 12px;
                display: flex;
                gap: 6px;
                background: rgba(255, 255, 255, 0.95);
                backdrop-filter: blur(8px);
                border: 1px solid #cbd5e1;
                border-radius: 6px;
                padding: 4px;
                box-shadow: 0 2px 6px rgba(0,0,0,0.08);
                z-index: 1000;
            }}
            .tool-btn {{
                background: transparent;
                border: 1px solid transparent;
                border-radius: 4px;
                padding: 6px 10px;
                font-size: 13px;
                font-weight: 500;
                color: #334155;
                cursor: pointer;
                transition: all 0.15s ease;
                display: flex;
                align-items: center;
                gap: 4px;
            }}
            .tool-btn:hover {{
                background: #f1f5f9;
                border-color: #cbd5e1;
                color: #0f172a;
            }}
            .tool-btn:active {{
                background: #e2e8f0;
            }}
            .mermaid-error {{
                padding: 16px;
                background-color: #fff1f2;
                border: 1px solid #fecdd3;
                border-radius: 6px;
                color: #be123c;
                font-family: monospace;
                font-size: 12px;
                white-space: pre-wrap;
            }}
            #zoom-label {{
                font-size: 11px;
                font-weight: 600;
                color: #64748b;
                display: flex;
                align-items: center;
                padding: 0 6px;
                border-left: 1px solid #e2e8f0;
            }}
        </style>
    </head>
    <body>
        <div id="viewport">
            <div id="toolbar">
                <button class="tool-btn" id="btn-zoom-in" title="Phóng to (+)">🔍 +</button>
                <button class="tool-btn" id="btn-zoom-out" title="Thu nhỏ (-)">🔍 -</button>
                <button class="tool-btn" id="btn-reset" title="Đặt lại góc nhìn chuẩn">↺ Reset</button>
                <button class="tool-btn" id="btn-download" title="Tải xuống ảnh Vector SVG">💾 SVG</button>
                <span id="zoom-label">100%</span>
            </div>
            <div id="canvas">
                <div id="mermaid-container">
                    <div style="color: #64748b; font-size: 13px; padding: 20px;">Đang khởi tạo sơ đồ...</div>
                </div>
            </div>
        </div>

        <script>
            mermaid.initialize({{
                startOnLoad: false,
                theme: 'neutral',
                securityLevel: 'strict',
                fontFamily: 'Inter, system-ui, sans-serif',
                er: {{ useMaxWidth: false }},
                sequence: {{ useMaxWidth: false }},
                flowchart: {{ useMaxWidth: false }},
                state: {{ useMaxWidth: false }}
            }});

            let scale = 1.0;
            let pointX = 0;
            let pointY = 0;
            let startX = 0;
            let startY = 0;
            let isPanning = false;
            let rendered = false;
            let resizeObserver = null;
            let intersectionObserver = null;

            const canvas = document.getElementById('canvas');
            const zoomLabel = document.getElementById('zoom-label');

            function updateTransform() {{
                canvas.style.transform = `translate(${{pointX}}px, ${{pointY}}px) scale(${{scale}})`;
                zoomLabel.textContent = `${{Math.round(scale * 100)}}%`;
            }}

            function zoom(factor, clientX = null, clientY = null) {{
                const newScale = Math.min(Math.max(0.2, scale * factor), 4.0);
                if (clientX !== null && clientY !== null) {{
                    const viewportRect = document.getElementById('viewport').getBoundingClientRect();
                    const mouseX = clientX - viewportRect.left;
                    const mouseY = clientY - viewportRect.top;
                    pointX = mouseX - (mouseX - pointX) * (newScale / scale);
                    pointY = mouseY - (mouseY - pointY) * (newScale / scale);
                }} else {{
                    const viewport = document.getElementById('viewport');
                    const cx = viewport.offsetWidth / 2;
                    const cy = viewport.offsetHeight / 2;
                    pointX = cx - (cx - pointX) * (newScale / scale);
                    pointY = cy - (cy - pointY) * (newScale / scale);
                }}
                scale = newScale;
                updateTransform();
            }}

            function resetView() {{
                const viewport = document.getElementById('viewport');
                const container = document.getElementById('mermaid-container');
                const svg = container.querySelector('svg');
                if (!svg || !viewport) return;
                svg.style.maxWidth = 'none';

                const vWidth = viewport.offsetWidth || 800;
                const vHeight = viewport.offsetHeight || 500;
                const sWidth = svg.getBoundingClientRect().width || (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.width) || 600;
                const sHeight = svg.getBoundingClientRect().height || (svg.viewBox && svg.viewBox.baseVal && svg.viewBox.baseVal.height) || 400;

                const pad = 48;
                const scaleX = (vWidth - pad) / Math.max(sWidth, 100);
                const scaleY = (vHeight - pad) / Math.max(sHeight, 100);
                const fitScale = Math.min(scaleX, scaleY);
                // Ensure initial scale remains clear and legible without requiring 400% zoom
                scale = Math.min(Math.max(fitScale, 0.85), 1.15);

                if (sWidth * scale > vWidth) {{
                    pointX = 24;
                }} else {{
                    pointX = Math.max(20, (vWidth - sWidth * scale) / 2);
                }}
                pointY = Math.max(20, (vHeight - sHeight * scale) / 2);
                updateTransform();
            }}

            function downloadSVG() {{
                const svg = document.querySelector('#mermaid-container svg');
                if (!svg) {{
                    alert('Sơ đồ chưa sẵn sàng để tải xuống!');
                    return;
                }}
                const serializer = new XMLSerializer();
                const source = '<?xml version="1.0" standalone="no"?>\\r\\n' + serializer.serializeToString(svg);
                const blob = new Blob([source], {{ type: 'image/svg+xml;charset=utf-8' }});
                const url = URL.createObjectURL(blob);
                const link = document.createElement('a');
                link.href = url;
                link.download = 'diagram_' + new Date().toISOString().slice(0, 19).replace(/[:T]/g, '_') + '.svg';
                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);
                URL.revokeObjectURL(url);
            }}

            async function renderDiagram() {{
                const container = document.getElementById('mermaid-container');
                const rawCode = {code_json};
                const renderId = 'mermaid_svg_' + Math.random().toString(36).substring(2, 9);
                try {{
                    const {{ svg }} = await mermaid.render(renderId, rawCode);
                    container.innerHTML = svg;
                    const renderedSvg = container.querySelector('svg');
                    if (renderedSvg) {{
                        renderedSvg.style.maxWidth = 'none';
                    }}
                    setTimeout(resetView, 60);
                }} catch (err) {{
                    console.error("Mermaid Render Error:", err);
                    const safeErr = document.createElement('div');
                    safeErr.className = 'mermaid-error';
                    safeErr.innerHTML = '<strong>⚠️ Lỗi hiển thị Mermaid:</strong><br>';
                    const msgSpan = document.createElement('span');
                    msgSpan.textContent = (err && err.message) ? err.message : String(err);
                    safeErr.appendChild(msgSpan);
                    container.innerHTML = '';
                    container.appendChild(safeErr);
                }}
            }}

            function cleanupObservers() {{
                if (resizeObserver) {{
                    resizeObserver.disconnect();
                    resizeObserver = null;
                }}
                if (intersectionObserver) {{
                    intersectionObserver.disconnect();
                    intersectionObserver = null;
                }}
            }}

            function checkAndRender() {{
                if (rendered) return;
                const viewport = document.getElementById('viewport');
                const container = document.getElementById('mermaid-container');
                if (!viewport || !container) return;

                if (document.body.offsetWidth > 0 && viewport.offsetWidth > 0) {{
                    rendered = true;
                    cleanupObservers();
                    renderDiagram();
                }}
            }}

            // Gắn sự kiện Pan kéo thả chuột
            const viewport = document.getElementById('viewport');
            viewport.addEventListener('mousedown', (e) => {{
                if (e.target.closest('#toolbar')) return;
                isPanning = true;
                startX = e.clientX - pointX;
                startY = e.clientY - pointY;
                viewport.classList.add('dragging');
            }});

            window.addEventListener('mousemove', (e) => {{
                if (!isPanning) return;
                pointX = e.clientX - startX;
                pointY = e.clientY - startY;
                updateTransform();
            }});

            window.addEventListener('mouseup', () => {{
                if (isPanning) {{
                    isPanning = false;
                    viewport.classList.remove('dragging');
                }}
            }});

            // Phóng to thu nhỏ bằng con lăn chuột (Wheel Zoom / Ctrl + Wheel)
            viewport.addEventListener('wheel', (e) => {{
                e.preventDefault();
                const factor = e.deltaY < 0 ? 1.15 : 0.87;
                zoom(factor, e.clientX, e.clientY);
            }}, {{ passive: false }});

            // Gắn sự kiện thanh công cụ
            document.getElementById('btn-zoom-in').addEventListener('click', (e) => {{
                e.stopPropagation();
                zoom(1.2);
            }});
            document.getElementById('btn-zoom-out').addEventListener('click', (e) => {{
                e.stopPropagation();
                zoom(1 / 1.2);
            }});
            document.getElementById('btn-reset').addEventListener('click', (e) => {{
                e.stopPropagation();
                resetView();
            }});
            document.getElementById('btn-download').addEventListener('click', (e) => {{
                e.stopPropagation();
                downloadSVG();
            }});

            // 1. Nếu đang ở Tab hiển thị sẵn -> gọi render ngay
            if (document.body.offsetWidth > 0 && viewport && viewport.offsetWidth > 0) {{
                rendered = true;
                renderDiagram();
            }} else {{
                // 2. Nếu nằm trong Tab ẩn của Streamlit -> theo dõi khi Tab được click mở
                if (window.ResizeObserver) {{
                    resizeObserver = new ResizeObserver(() => {{
                        checkAndRender();
                    }});
                    resizeObserver.observe(document.body);
                    if (viewport) {{
                        resizeObserver.observe(viewport);
                    }}
                }}

                if (window.IntersectionObserver && viewport) {{
                    intersectionObserver = new IntersectionObserver((entries) => {{
                        for (const entry of entries) {{
                            if (entry.isIntersecting || entry.intersectionRatio > 0) {{
                                checkAndRender();
                            }}
                        }}
                    }});
                    intersectionObserver.observe(viewport);
                }}

                window.addEventListener('resize', checkAndRender);
            }}
        </script>
    </body>
    </html>
    """
    components.html(html_content, height=height, scrolling=False)
