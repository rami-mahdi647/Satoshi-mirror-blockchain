diff --git a/public/app.js b/public/app.js
new file mode 100644
index 0000000000000000000000000000000000000000..7a5e20ec959ecfaaaac8d22fde387a50677dafe5
--- /dev/null
+++ b/public/app.js
@@ -0,0 +1,142 @@
+const elements = {
+  botCount: document.getElementById("botCount"),
+  simulator: document.getElementById("simulator"),
+  isRunning: document.getElementById("isRunning"),
+  applyConfig: document.getElementById("applyConfig"),
+  executionStatus: document.getElementById("executionStatus"),
+  lastUpdated: document.getElementById("lastUpdated"),
+  dataMode: document.getElementById("dataMode"),
+  txCount: document.getElementById("txCount"),
+  latency: document.getElementById("latency"),
+  accuracy: document.getElementById("accuracy"),
+  blocks: document.getElementById("blocks"),
+  eventLog: document.getElementById("eventLog"),
+};
+
+const state = {
+  config: {
+    botCount: 24,
+    simulator: "quantum",
+    status: "running",
+  },
+  metrics: {
+    txCount: 0,
+    latency: 0,
+    accuracy: 0,
+    blocks: 0,
+  },
+  events: [],
+  dataMode: "demo",
+};
+
+const demoGenerator = (() => {
+  let txBase = 1200;
+  let blockBase = 38;
+
+  const statuses = ["running", "paused", "stopped"];
+  const messages = [
+    "Bot conectado a la red principal.",
+    "Simulación sincronizada con el nodo 02.",
+    "Ajuste de latencia aplicado.",
+    "Nueva ronda de consenso completada.",
+    "Carga de trabajo redistribuida.",
+  ];
+
+  return (config) => {
+    const jitter = () => Math.random() * 0.2 - 0.1;
+    txBase += Math.floor(20 + 40 * Math.random());
+    blockBase += Math.random() > 0.6 ? 1 : 0;
+
+    return {
+      status: config.status || statuses[Math.floor(Math.random() * statuses.length)],
+      metrics: {
+        txCount: txBase,
+        latency: Math.max(20, 140 + jitter() * 100 + config.botCount * 1.2),
+        accuracy: Math.min(99.9, 95 + Math.random() * 4),
+        blocks: blockBase,
+      },
+      events: [
+        `Bots activos: ${config.botCount}.`,
+        `${messages[Math.floor(Math.random() * messages.length)]}`,
+        `Simulador: ${config.simulator}.`,
+      ],
+    };
+  };
+})();
+
+const formatTimestamp = () =>
+  new Date().toLocaleTimeString("es-ES", {
+    hour: "2-digit",
+    minute: "2-digit",
+    second: "2-digit",
+  });
+
+const render = () => {
+  elements.executionStatus.textContent =
+    state.config.status === "running"
+      ? "En ejecución"
+      : state.config.status === "paused"
+      ? "Pausado"
+      : "Detenido";
+  elements.lastUpdated.textContent = `Última actualización: ${formatTimestamp()}`;
+  elements.dataMode.textContent = state.dataMode === "live" ? "En vivo" : "Modo demo";
+
+  elements.txCount.textContent = state.metrics.txCount.toLocaleString("es-ES");
+  elements.latency.textContent = `${state.metrics.latency.toFixed(1)} ms`;
+  elements.accuracy.textContent = `${state.metrics.accuracy.toFixed(2)} %`;
+  elements.blocks.textContent = state.metrics.blocks.toLocaleString("es-ES");
+
+  elements.eventLog.innerHTML = "";
+  state.events.slice(0, 5).forEach((event) => {
+    const item = document.createElement("li");
+    item.textContent = event;
+    elements.eventLog.appendChild(item);
+  });
+};
+
+const updateFromApi = async () => {
+  try {
+    const response = await fetch("/api/status", { cache: "no-store" });
+    if (!response.ok) {
+      throw new Error("Respuesta no válida");
+    }
+    const data = await response.json();
+
+    state.dataMode = "live";
+    state.config.status = data.status || state.config.status;
+    state.metrics = {
+      txCount: data.txCount ?? state.metrics.txCount,
+      latency: data.latency ?? state.metrics.latency,
+      accuracy: data.accuracy ?? state.metrics.accuracy,
+      blocks: data.blocks ?? state.metrics.blocks,
+    };
+    state.events = data.events?.length ? data.events : state.events;
+  } catch (error) {
+    const demo = demoGenerator(state.config);
+    state.dataMode = "demo";
+    state.config.status = demo.status;
+    state.metrics = demo.metrics;
+    state.events = demo.events;
+  }
+
+  render();
+};
+
+const applyConfig = () => {
+  state.config.botCount = Number(elements.botCount.value) || 1;
+  state.config.simulator = elements.simulator.value;
+  state.config.status = elements.isRunning.value;
+  state.events = [
+    `Configuración aplicada: ${state.config.botCount} bots.`,
+    `Simulador seleccionado: ${state.config.simulator}.`,
+    `Estado establecido en: ${state.config.status}.`,
+  ];
+  render();
+};
+
+applyConfig();
+updateFromApi();
+
+setInterval(updateFromApi, 4000);
+
+elements.applyConfig.addEventListener("click", applyConfig);
