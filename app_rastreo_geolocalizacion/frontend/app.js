// GeoTracker Safe - Lógica del Dashboard y Mapa Leaflet.js
// Universidad Distrital Francisco José de Caldas - 2026

document.addEventListener("DOMContentLoaded", () => {
    // 1. Inicializar Mapa Leaflet
    const defaultCoords = [4.628031, -74.065120]; // UD Sede Calle 40
    const map = L.map('map').setView(defaultCoords, 15);

    // Capa de CartoDB Dark Matter / OSM
    L.tileLayer('https://{s}.basemaps.cartocdn.com/rastertiles/voyager/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    let deviceMarkers = {};
    let geofenceLayers = [];
    let activeTrailPolyline = null;
    let selectedDeviceId = null;

    // 2. Cargar Geocercas
    async function loadGeofences() {
        try {
            const resp = await fetch("/api/v1/geofence");
            const data = await resp.json();
            
            // Limpiar capas previas
            geofenceLayers.forEach(l => map.removeLayer(l));
            geofenceLayers = [];

            data.geofences.forEach(g => {
                const circle = L.circle([g.center_lat, g.center_lon], {
                    color: '#10b981',
                    fillColor: '#10b981',
                    fillOpacity: 0.15,
                    radius: g.radius_meters,
                    dashArray: '5, 5',
                    weight: 2
                }).addTo(map);

                circle.bindPopup(`<strong>${g.name}</strong><br>Radio seguro: ${g.radius_meters}m`);
                geofenceLayers.push(circle);
            });
        } catch (e) {
            console.error("Error cargando geocercas:", e);
        }
    }

    // 3. Cargar Dispositivos
    async function loadDevices() {
        try {
            const resp = await fetch("/api/v1/devices");
            const data = await resp.json();
            const listEl = document.getElementById("device-list");
            listEl.innerHTML = "";

            let countInside = 0;

            data.devices.forEach(dev => {
                const hasLoc = dev.latitude !== null && dev.longitude !== null;
                const isInside = dev.address && dev.address.includes("Campus UD");
                if (isInside) countInside++;

                const card = document.createElement("div");
                card.className = `device-card ${selectedDeviceId === dev.device_id ? 'active' : ''}`;
                card.innerHTML = `
                    <div class="device-header">
                        <span class="device-name">${dev.device_name}</span>
                        <span class="badge ${isInside ? 'badge-success' : 'badge-danger'}">
                            ${isInside ? 'En Zona' : 'Fuera/Sin Señal'}
                        </span>
                    </div>
                    <div class="device-details">
                        <div><i class="fa-solid fa-phone"></i> ${dev.phone_number}</div>
                        <div><i class="fa-solid fa-gauge"></i> Velocidad: ${dev.speed ? dev.speed.toFixed(1) : '0.0'} km/h</div>
                        <div><i class="fa-solid fa-battery-half"></i> Batería: ${dev.battery_level ? dev.battery_level.toFixed(0) : '100'}%</div>
                        <div style="font-size:0.72rem; margin-top:4px;"><i class="fa-solid fa-location-dot"></i> ${dev.address || 'Ubicación no reportada'}</div>
                    </div>
                `;

                card.addEventListener("click", () => selectDevice(dev));
                listEl.appendChild(card);

                // Actualizar o crear marcador en el mapa
                if (hasLoc) {
                    const pos = [dev.latitude, dev.longitude];
                    if (deviceMarkers[dev.device_id]) {
                        deviceMarkers[dev.device_id].setLatLng(pos);
                    } else {
                        const marker = L.marker(pos, {
                            title: dev.device_name
                        }).addTo(map);

                        marker.bindPopup(`
                            <strong>${dev.device_name}</strong><br>
                            Tel: ${dev.phone_number}<br>
                            Velocidad: ${dev.speed} km/h<br>
                            Último reporte: ${dev.recorded_at}
                        `);
                        deviceMarkers[dev.device_id] = marker;
                    }
                }
            });

            // Actualizar contadores navbar
            document.getElementById("count-devices").textContent = data.devices.length;
            document.getElementById("count-inside").textContent = countInside;

            // Auto-seleccionar el primer dispositivo si no hay ninguno seleccionado
            if (!selectedDeviceId && data.devices.length > 0) {
                selectDevice(data.devices[0]);
            }
        } catch (e) {
            console.error("Error cargando dispositivos:", e);
        }
    }

    // 4. Seleccionar Dispositivo y Dibujar Ruta
    async function selectDevice(dev) {
        selectedDeviceId = dev.device_id;
        
        // Resaltar en UI
        document.querySelectorAll(".device-card").forEach(c => c.classList.remove("active"));

        if (dev.latitude && dev.longitude) {
            map.flyTo([dev.latitude, dev.longitude], 16);
        }

        // Cargar historial para dibujar la ruta
        try {
            const resp = await fetch(`/api/v1/history/${dev.device_id}`);
            const data = await resp.json();
            
            if (activeTrailPolyline) {
                map.removeLayer(activeTrailPolyline);
            }

            if (data.trail && data.trail.length > 0) {
                const latlngs = data.trail.map(p => [p.latitude, p.longitude]);
                activeTrailPolyline = L.polyline(latlngs, {
                    color: '#2563eb',
                    weight: 3.5,
                    opacity: 0.85,
                    dashArray: '6, 6'
                }).addTo(map);
            }

            // Actualizar panel de telemetría flotante
            const teleEl = document.getElementById("telemetry-content");
            teleEl.innerHTML = `
                <div style="font-size:0.82rem; line-height:1.5;">
                    <div><strong>Dispositivo:</strong> ${dev.device_name}</div>
                    <div><strong>Número:</strong> ${dev.phone_number}</div>
                    <div><strong>Coordenadas:</strong> ${dev.latitude ? dev.latitude.toFixed(6) : '-'}, ${dev.longitude ? dev.longitude.toFixed(6) : '-'}</div>
                    <div><strong>Precisión GPS:</strong> ${dev.accuracy || 5} metros</div>
                    <div><strong>Velocidad actual:</strong> ${dev.speed ? dev.speed.toFixed(1) : 0} km/h</div>
                    <div><strong>Batería:</strong> ${dev.battery_level || 100}%</div>
                    <div><strong>Dirección:</strong> ${dev.address || 'Consultando...'}</div>
                    <div style="margin-top:6px; color:#10b981;"><i class="fa-solid fa-lock"></i> Canal Cifrado TLS / Token Activo</div>
                </div>
            `;
        } catch (e) {
            console.error("Error cargando historial de ruta:", e);
        }
    }

    // 5. Cargar Alertas
    async function loadAlerts() {
        try {
            const resp = await fetch("/api/v1/alerts");
            const data = await resp.json();
            const listEl = document.getElementById("alerts-list");
            document.getElementById("count-alerts").textContent = data.alerts.length;

            if (data.alerts.length === 0) {
                listEl.innerHTML = '<p class="empty-state">No se registran violaciones de seguridad.</p>';
                return;
            }

            listEl.innerHTML = "";
            data.alerts.forEach(al => {
                const item = document.createElement("div");
                item.className = "alert-item";
                item.innerHTML = `
                    <div style="font-weight:600; color:#ef4444;"><i class="fa-solid fa-triangle-exclamation"></i> ${al.alert_type}</div>
                    <div>${al.description}</div>
                    <div class="alert-time">${al.created_at} | Dispositivo: ${al.phone_number}</div>
                `;
                listEl.appendChild(item);
            });
        } catch (e) {
            console.error("Error cargando alertas:", e);
        }
    }

    // 6. Modal de Registro
    const modal = document.getElementById("register-modal");
    document.getElementById("btn-register-modal").onclick = () => modal.style.display = "flex";
    document.getElementById("btn-close-modal").onclick = () => modal.style.display = "none";
    document.getElementById("btn-cancel-modal").onclick = () => modal.style.display = "none";

    document.getElementById("btn-submit-register").onclick = async () => {
        const phone = document.getElementById("input-phone").value.trim();
        const name = document.getElementById("input-name").value.trim();
        const consent = document.getElementById("check-consent").checked;

        if (!phone || !name) {
            alert("Por favor complete el número telefónico y el nombre del dispositivo.");
            return;
        }

        try {
            const resp = await fetch("/api/v1/devices/register", {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({ phone_number: phone, device_name: name, consent_accepted: consent })
            });
            const res = await resp.json();
            if (resp.ok) {
                alert(`Dispositivo registrado con éxito.\nDevice ID: ${res.device_id}\nToken: ${res.auth_token}`);
                modal.style.display = "none";
                document.getElementById("input-phone").value = "";
                document.getElementById("input-name").value = "";
                loadDevices();
            } else {
                alert("Error: " + (res.detail || "No se pudo registrar"));
            }
        } catch (e) {
            alert("Fallo de conexión al registrar.");
        }
    };

    document.getElementById("btn-refresh").onclick = () => {
        loadDevices();
        loadAlerts();
    };

    // Inicialización y Polling periódico cada 5 segundos
    loadGeofences();
    loadDevices();
    loadAlerts();
    setInterval(() => {
        loadDevices();
        loadAlerts();
    }, 5000);
});
