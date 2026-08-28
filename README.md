Here is the final, stabilized index.html code for the main Primer Zone Orbital Registry, along with the complete asset checklist you need in your root directory to ensure it deploys perfectly on Cloudflare.
Required Assets List
1. Local Files (Must be in the same folder as index.html):
jupiter.jpg (Your custom infrared polygon image)
saturn.jpg (Your updated saturn_2.jpg file, renamed to saturn.jpg to match the code)
uranus.jpg (The base Uranus texture)
uranus7.png (The NASA Eyes heptagon reference for the UI inset)
2. Remote Assets (Loaded automatically via URL):
Earth Texture: [https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg](https://raw.githubusercontent.com/mrdoob/three.js/master/examples/textures/planets/earth_atmos_2048.jpg)
Libraries: Tailwind CSS, Three.js (r128), and GSAP (3.12.2) via CDN.
Fonts: Inter and Rajdhani via Google Fonts.
Data Link: [https://zenodo.org/records/18395134, https://zenodo.org/records/18487338, https://zenodo.org/records/19322599](https://zenodo.org/records/18395134) (Your updated Zenodo archive link).
The Primer Zone: index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <title>The Primer Zone | Solar Orbital Registry</title>
    
    <!-- Favicon -->
    <link rel="icon" type="image/svg+xml" href="data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 64 64'%3E%3Cpolygon points='32,6 58,56 6,56' fill='none' stroke='%2300f3ff' stroke-width='3' stroke-linejoin='round'/%3E%3C/svg%3E">

    <!-- Libraries -->
    <script src="https://cdn.tailwindcss.com"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/gsap/3.12.2/gsap.min.js"></script>
    
    <!-- Fonts -->
    <link href="https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600&family=Rajdhani:wght@400;600;700&display=swap" rel="stylesheet">
    
    <style>
        :root {
            --bg-color: #050505;
            --glass: rgba(10, 15, 30, 0.85);
            --border: rgba(0, 243, 255, 0.2);
            --accent: #00f3ff;
        }
        
        body { 
            background-color: var(--bg-color); 
            color: #ffffff; 
            font-family: 'Rajdhani', sans-serif; 
            overflow: hidden; 
            margin: 0;
            -webkit-font-smoothing: antialiased;
        }
        
        .font-sans { font-family: 'Inter', sans-serif; }

        .ui-panel {
            background: var(--glass);
            backdrop-filter: blur(20px);
            -webkit-backdrop-filter: blur(20px);
            border: 1px solid var(--border);
            box-shadow: 0 0 40px rgba(0,0,0,0.9);
        }

        .nav-btn {
            background: rgba(0,0,0,0.5);
            border: 1px solid rgba(255,255,255,0.1);
            transition: all 0.3s ease;
            text-align: center;
        }
        .nav-btn:hover, .nav-btn.active {
            border-color: var(--accent);
            background: rgba(0, 243, 255, 0.15);
            color: var(--accent);
            text-shadow: 0 0 10px rgba(0, 243, 255, 0.6);
        }

        .scanline {
            position: fixed; inset: 0; pointer-events: none; z-index: 5;
            background: linear-gradient(rgba(18, 16, 16, 0) 50%, rgba(0, 0, 0, 0.1) 50%), linear-gradient(90deg, rgba(255, 0, 0, 0.03), rgba(0, 255, 0, 0.01), rgba(0, 0, 255, 0.03));
            background-size: 100% 3px, 3px 100%;
        }

        #loader {
            position: fixed; inset: 0; z-index: 100;
            background: #000; 
            display: flex; justify-content: center; align-items: center; flex-direction: column;
            transition: opacity 1s ease-out;
        }
    </style>
</head>
<body>

    <!-- Loader -->
    <div id="loader">
        <div class="text-4xl font-bold tracking-[0.2em] text-cyan-400 mb-2">PRIMER.ZONE</div>
        <div class="text-xs font-sans text-gray-500 tracking-widest">OPTIMIZING RING GEOMETRY...</div>
        <div class="w-64 h-1 bg-gray-800 mt-4 rounded-full overflow-hidden">
            <div class="h-full bg-cyan-400 w-0 transition-all duration-1000" id="load-bar"></div>
        </div>
    </div>

    <!-- 3D Layer -->
    <div id="scene-container" class="absolute inset-0 z-0 cursor-crosshair"></div>
    <div class="scanline"></div>

    <!-- UI Layer -->
    <div class="absolute inset-0 z-10 pointer-events-none flex flex-col justify-between p-4 md:p-8 no-select">
        
        <!-- Header -->
        <header class="flex justify-between items-start pointer-events-auto">
            <div>
                <div class="flex items-center gap-2">
                    <div class="w-2 h-2 bg-cyan-400 rounded-full animate-pulse shadow-[0_0_15px_#00f3ff]"></div>
                    <h1 class="text-2xl font-bold tracking-widest">ORBITAL REGISTRY</h1>
                </div>
                <p class="text-xs text-cyan-200/60 font-sans tracking-wide mt-1">CONFIDENCE: P ≈ 0.000244 (3.7σ)</p>
            </div>
            
            <!-- Desktop Nav -->
            <nav class="hidden md:flex gap-4">
                <button onclick="warpTo('jupiter')" class="nav-btn px-6 py-2 text-sm tracking-widest active" id="nav-jupiter">05 JUPITER</button>
                <button onclick="warpTo('saturn')" class="nav-btn px-6 py-2 text-sm tracking-widest" id="nav-saturn">06 SATURN</button>
                <button onclick="warpTo('uranus')" class="nav-btn px-6 py-2 text-sm tracking-widest" id="nav-uranus">07 URANUS</button>
                <button onclick="warpTo('earth')" class="nav-btn px-6 py-2 text-sm tracking-widest text-yellow-400 border-yellow-400/30" id="nav-earth">03 EARTH NODE</button>
            </nav>

            <!-- Mobile Menu Toggle -->
            <button onclick="toggleMobileMenu()" class="md:hidden border border-cyan-400/50 text-cyan-400 px-4 py-2 text-xs font-bold tracking-widest bg-black/80 backdrop-blur active:bg-cyan-900/50">
                SYSTEMS
            </button>
        </header>

        <!-- Center Drag Hint -->
        <div id="drag-hint" class="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 pointer-events-none transition-opacity duration-700 opacity-0">
            <div class="flex flex-col items-center gap-2">
                <div class="w-12 h-12 border border-white/20 rounded-full flex items-center justify-center">
                    <div class="w-1 h-1 bg-white rounded-full"></div>
                </div>
                <p class="text-[10px] font-sans text-white/50 tracking-[0.2em]">DRAG TO ROTATE</p>
            </div>
        </div>

        <!-- Uranus Inset -->
        <div id="uranus-inset" class="absolute right-4 md:right-8 top-1/2 transform -translate-y-1/2 hidden opacity-0 transition-opacity duration-500 z-50 pointer-events-auto">
            <div class="ui-panel p-2 rounded-xl flex flex-col items-center gap-2 w-[120px] origin-right transition-transform duration-300 hover:scale-[3] cursor-default">
                <img src="./uranus7.png" alt="Uranus Polar Reference" class="w-full rounded border border-cyan-400/30 pointer-events-none">
                <p class="text-[6px] text-cyan-200/80 font-sans text-center px-1 leading-tight">
                    Ref: <br><a href="https://eyes.nasa.gov/apps/solar-system/#/uranus" target="_blank" class="underline hover:text-cyan-400">NASA Eyes on the Solar System</a>
                </p>
            </div>
        </div>

        <!-- Footer / Controls -->
        <footer class="flex flex-col md:flex-row justify-between items-end gap-6 pointer-events-auto">
            
            <!-- Info Panel -->
            <div id="info-panel" class="ui-panel p-4 md:p-6 w-full md:w-96 rounded-tr-xl transition-all duration-500">
                <div class="flex justify-between items-baseline mb-3">
                    <h2 class="text-3xl md:text-4xl font-bold text-white tracking-wide" id="planet-title">JUPITER</h2>
                    <span class="text-[10px] md:text-xs font-mono text-cyan-400 bg-cyan-900/30 px-2 py-1 rounded" id="stat-geo-short">N=5 & N=8</span>
                </div>
                <div class="h-px w-full bg-gradient-to-r from-cyan-500 to-transparent mb-4 opacity-50"></div>
                <p class="text-xs md:text-sm text-gray-300 font-sans font-light leading-relaxed" id="planet-desc">
                    Scanning Poles...<br>
                    > South Pole: Pentagonal Vortex (N=5)<br>
                    > North Pole: Octagonal Crystal (N=8)<br>
                    Correlation with orbital index confirmed.
                </p>
            </div>

            <!-- Earth Node Builder -->
            <div id="builder-panel" class="ui-panel p-4 md:p-6 w-full md:w-96 rounded-tl-xl hidden">
                <div class="flex justify-between items-center mb-2">
                    <h2 class="text-lg md:text-xl font-bold text-yellow-400 tracking-wider">EARTH NODE (N=3)</h2>
                    <span id="node-status" class="text-[9px] bg-red-900/50 text-red-200 px-2 py-1 rounded border border-red-500/30 animate-pulse">OFFLINE</span>
                </div>
                <p id="protocol-text" class="text-xs text-gray-400 mb-4 font-mono border-l-2 border-yellow-500/30 pl-2">PROTOCOL: Generate Artificial Auroral Triangle</p>
                
                <div class="space-y-2">
                    <button onclick="buildStage(1)" id="btn-build-1" class="w-full py-2 bg-yellow-400/5 border border-yellow-400/30 text-yellow-100 text-[10px] md:text-xs tracking-widest hover:bg-yellow-400/20 transition text-left px-4 flex justify-between items-center group">
                        <span>[1] DEPLOY HVDC GRID</span>
                        <span class="opacity-0 group-hover:opacity-100">-></span>
                    </button>
                    <button onclick="buildStage(2)" id="btn-build-2" class="w-full py-2 bg-black/40 border border-gray-700 text-gray-500 text-[10px] md:text-xs tracking-widest transition text-left px-4 cursor-not-allowed flex justify-between items-center" disabled>
                        <span>[2] CHARGE SMES BANKS</span>
                        <span></span>
                    </button>
                    <button onclick="buildStage(3)" id="btn-build-3" class="w-full py-2 bg-black/40 border border-gray-700 text-gray-500 text-[10px] md:text-xs tracking-widest transition text-left px-4 cursor-not-allowed flex justify-between items-center" disabled>
                        <span>[3] FIRE MHD LENS</span>
                        <span></span>
                    </button>
                </div>
                <div class="mt-4 h-1 bg-gray-800 rounded overflow-hidden">
                    <div id="build-progress" class="h-full bg-yellow-400 w-0 transition-all duration-1000"></div>
                </div>
            </div>
            
            <a href="https://zenodo.org/records/18395134" target="_blank" class="hidden md:block text-[10px] text-white/30 hover:text-white transition font-sans mb-1">
                ACCESS FULL DATA ARCHIVE ↗
            </a>
        </footer>
    </div>

    <!-- Mobile Menu Overlay -->
    <div id="mobile-nav" class="fixed inset-0 bg-black/95 z-50 hidden flex flex-col justify-center items-center space-y-8 pointer-events-auto backdrop-blur-xl transition-opacity duration-300">
        <button onclick="warpTo('jupiter'); toggleMobileMenu()" class="text-2xl font-light tracking-widest hover:text-cyan-400 transition">05 JUPITER</button>
        <button onclick="warpTo('saturn'); toggleMobileMenu()" class="text-2xl font-light tracking-widest hover:text-cyan-400 transition">06 SATURN</button>
        <button onclick="warpTo('uranus'); toggleMobileMenu()" class="text-2xl font-light tracking-widest hover:text-cyan-400 transition">07 URANUS</button>
        <div class="w-12 h-px bg-white/20"></div>
        <button onclick="warpTo('earth'); toggleMobileMenu()" class="text-2xl font-bold tracking-widest text-yellow-400 shadow-yellow-500/50 drop-shadow-lg">PROJECT EARTH NODE</button>
        <button onclick="toggleMobileMenu()" class="absolute bottom-12 text-xs font-mono text-white/40 border border-white/10 px-4 py-2">CLOSE INTERFACE</button>
    </div>

    <script>
        // --- 1. SETUP ---
        let scene, camera, renderer, container;
        let jupiterGroup, saturnGroup, uranusGroup, earthGroup;
        let gridGroup, beam, nodes, chargeRing;
        let triangleMat, ship, bioBeam, bioMat; 
        
        let currentGroup, camTarget, lookTarget;
        let isDragging = false, prevX = 0, prevY = 0;
        let isInputsSetup = false;
        
        let lineMat, beamMat;

        function initApp() {
            if (!window.THREE) {
                setTimeout(initApp, 100); return;
            }

            container = document.getElementById('scene-container');
            while(container.firstChild) container.removeChild(container.firstChild);

            scene = new THREE.Scene();
            scene.fog = new THREE.FogExp2(0x000000, 0.0008);

            camera = new THREE.PerspectiveCamera(45, window.innerWidth / window.innerHeight, 0.1, 50000);
            camera.position.set(0, 30, 140);

            renderer = new THREE.WebGLRenderer({ alpha: false, antialias: true });
            renderer.setSize(window.innerWidth, window.innerHeight);
            renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
            renderer.toneMapping = THREE.ACESFilmicToneMapping;
            renderer.outputEncoding = THREE.sRGBEncoding;
            container.appendChild(renderer.domElement);

            // --- 2. ASSETS ---
            const starGeo = new THREE.BufferGeometry();
            const starCount = 5000;
            const posArray = new Float32Array(starCount * 3);
            const colorArray = new Float32Array(starCount * 3);
            for(let i=0; i<starCount*3; i+=3) {
                posArray[i] = (Math.random() - 0.5) * 8000;
                posArray[i+1] = (Math.random() - 0.5) * 8000;
                posArray[i+2] = (Math.random() - 0.5) * 8000;
                const type = Math.random();
                if(type > 0.9) { colorArray[i]=1; colorArray[i+1]=0.9; colorArray[i+2]=0.5; }
                else if(type > 0.7) { colorArray[i]=0.8; colorArray[i+1]=0.9; colorArray[i+2]=1; }
                else { colorArray[i]=1; colorArray[i+1]=1; colorArray[i+2]=1; }
            }
            starGeo.setAttribute('position', new THREE.BufferAttribute(posArray, 3));
            starGeo.setAttribute('color', new THREE.BufferAttribute(colorArray, 3));
            const starMat = new THREE.PointsMaterial({vertexColors: true, size: 1.2, transparent: true, opacity: 0.8});
            const stars = new THREE.Points(starGeo, starMat);
            scene.add(stars);

            const texLoader = new THREE.TextureLoader();
            texLoader.crossOrigin = 'anonymous';

            // --- HELPER FUNCTION FOR PERFECT TEXTURES ---
            function createPlanetMaterial(url, fallbackColor) {
                const mat = new THREE.MeshStandardMaterial({
                    map: texLoader.load(url, (tex) => {
                        tex.wrapS = THREE.RepeatWrapping;
                        tex.wrapT = THREE.RepeatWrapping;
                        tex.minFilter = THREE.LinearMipmapLinearFilter; 
                        tex.magFilter = THREE.LinearFilter;
                        tex.anisotropy = renderer.capabilities.getMaxAnisotropy();
                        mat.map = tex;
                        mat.needsUpdate = true;
                    }, undefined, (err) => {
                        mat.map = null; 
                        mat.color.setHex(fallbackColor);
                    }),
                    color: 0xffffff, roughness: 0.7, metalness: 0.1
                });
                return mat;
            }

            // --- MATHEMATICAL SATURN RING GENERATOR ---
            function fixRingUVs(geometry, innerRadius, outerRadius) {
                const posAttribute = geometry.attributes.position;
                const uvAttribute = geometry.attributes.uv;
                for (let i = 0; i < posAttribute.count; i++) {
                    const x = posAttribute.getX(i);
                    const y = posAttribute.getY(i);
                    const radius = Math.sqrt(x*x + y*y);
                    let u = (radius - innerRadius) / (outerRadius - innerRadius);
                    let v = 0.5;
                    uvAttribute.setXY(i, u, v);
                }
                uvAttribute.needsUpdate = true;
            }

            function generateSaturnRingTexture() {
                const canvas = document.createElement('canvas');
                canvas.width = 1024;
                canvas.height = 1;
                const ctx = canvas.getContext('2d');
                const grad = ctx.createLinearGradient(0, 0, 1024, 0);
                
                // Photometric accurate bands based on Cassini
                grad.addColorStop(0.0, 'rgba(0,0,0,0)');
                grad.addColorStop(0.1, 'rgba(160,140,110,0.5)'); 
                grad.addColorStop(0.3, 'rgba(210,190,150,0.8)'); 
                grad.addColorStop(0.55, 'rgba(230,210,170,1.0)'); 
                grad.addColorStop(0.56, 'rgba(0,0,0,0)'); 
                grad.addColorStop(0.62, 'rgba(0,0,0,0)'); 
                grad.addColorStop(0.63, 'rgba(180,160,130,0.8)'); 
                grad.addColorStop(0.85, 'rgba(150,130,100,0.6)'); 
                grad.addColorStop(0.9, 'rgba(0,0,0,0)'); 
                grad.addColorStop(0.92, 'rgba(140,120,90,0.4)'); 
                grad.addColorStop(1.0, 'rgba(0,0,0,0)');

                ctx.fillStyle = grad;
                ctx.fillRect(0, 0, 1024, 1);
                
                const tex = new THREE.CanvasTexture(canvas);
                tex.wrapS = THREE.RepeatWrapping;
                tex.wrapT = THREE.RepeatWrapping;
                return tex;
            }

            function createAtmosphere(radius, color) {
                const geo = new THREE.SphereGeometry(radius, 64, 64);
                const mat = new THREE.MeshBasicMaterial({
                    color: color, transparent: true, opacity: 0.15, 
                    side: THREE.BackSide, blending: THREE.AdditiveBlending
                });
                return new THREE.Mesh(geo, mat);
            }

            function createGeometry(radius, sides, colorHex, yPos) {
                const path = new THREE.Shape();
                for (let i = 0; i <= sides; i++) {
                    const theta = (i / sides) * Math.PI * 2;
                    const x = Math.cos(theta) * radius;
                    const y = Math.sin(theta) * radius;
                    if (i === 0) path.moveTo(x, y); else path.lineTo(x, y);
                }
                const geo = new THREE.BufferGeometry().setFromPoints(path.getPoints());
                const mat = new THREE.LineBasicMaterial({ color: colorHex, linewidth: 2 });
                const line = new THREE.Line(geo, mat);
                line.rotation.x = Math.PI / 2;
                line.position.y = yPos;
                return line;
            }

            // --- JUPITER ---
            jupiterGroup = new THREE.Group();
            const jupMat = createPlanetMaterial('./jupiter.jpg', 0xcc9966);
            const jupiter = new THREE.Mesh(new THREE.SphereGeometry(30, 128, 128), jupMat); 
            jupiter.rotation.y = -Math.PI / 2; 
            jupiterGroup.add(jupiter);
            jupiterGroup.add(createAtmosphere(32, 0xffaa55));
            jupiterGroup.add(createGeometry(20, 5, 0xff3333, -29));
            jupiterGroup.add(createGeometry(15, 8, 0xff3333, 29));
            scene.add(jupiterGroup);

            // --- SATURN ---
            saturnGroup = new THREE.Group();
            saturnGroup.rotation.z = 27 * (Math.PI / 180);
            const
