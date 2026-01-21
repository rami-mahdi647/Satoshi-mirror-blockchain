diff --git a/docs/qbist-format.md b/docs/qbist-format.md
new file mode 100644
index 0000000000000000000000000000000000000000..45da11a487c938b7536ed04ad220ec09ca55a1ee
--- /dev/null
+++ b/docs/qbist-format.md
@@ -0,0 +1,61 @@
+# Formato QBIST (Quantum Binary Serialization Toolkit)
+
+El formato **QBIST** describe circuitos cuánticos como un JSON autocontenido. Está pensado para
+exportar circuitos de Qiskit o de una estructura propia a una representación común.
+
+## Esquema
+
+El JSON debe contener estos campos principales:
+
+- `qubits`: lista de identificadores de qubits (enteros).
+- `operations`: lista de operaciones aplicadas sobre los qubits.
+- `metadata`: metadatos asociados al circuito.
+
+### Operación
+
+Cada operación es un objeto con los siguientes campos:
+
+- `name`: nombre de la compuerta u operación.
+- `qubits`: lista de índices de qubits involucrados.
+- `clbits`: lista de bits clásicos afectados (puede estar vacía).
+- `params`: lista de parámetros serializados (números o cadenas).
+
+### Metadatos
+
+Los metadatos incluyen:
+
+- `timestamp`: fecha/hora UTC en formato ISO-8601.
+- `seed`: semilla opcional usada para reproducibilidad.
+
+## Ejemplo de entrada (estructura propia)
+
+```json
+{
+  "qubits": [0, 1],
+  "operations": [
+    {"name": "x", "qubits": [1], "clbits": [], "params": []},
+    {"name": "h", "qubits": [0], "clbits": [], "params": []},
+    {"name": "swap", "qubits": [0, 1], "clbits": [], "params": []},
+    {"name": "measure", "qubits": [0, 1], "clbits": [0, 1], "params": []}
+  ],
+  "metadata": {"seed": 42}
+}
+```
+
+## Ejemplo de salida QBIST
+
+```json
+{
+  "qubits": [0, 1],
+  "operations": [
+    {"name": "x", "qubits": [1], "clbits": [], "params": []},
+    {"name": "h", "qubits": [0], "clbits": [], "params": []},
+    {"name": "swap", "qubits": [0, 1], "clbits": [], "params": []},
+    {"name": "measure", "qubits": [0, 1], "clbits": [0, 1], "params": []}
+  ],
+  "metadata": {
+    "timestamp": "2024-01-21T14:10:00+00:00",
+    "seed": 42
+  }
+}
+```
