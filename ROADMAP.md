# Roadmap

Mejoras pendientes de revisar y aplicar.

---

## Pendiente

### `provision.yml` — quitar `--force` en galaxy install

Los tres comandos `ansible-galaxy install` y `collection install` usan `--force`, lo que fuerza la descarga de roles y colecciones en cada ejecución aunque las versiones ya estén instaladas. Hace el playbook más lento y requiere conexión a Galaxy siempre.

**Fix:** eliminar `--force` y dejar que Galaxy gestione las versiones por sí solo. Usar `--force` solo cuando se quiera actualizar explícitamente.

---

### `defaults/main.yml` — Tailscale GPG key hardcodeada a `jammy`

La URL de la clave GPG de Tailscale está fijada a `jammy.noarmor.gpg`, pero el repositorio usa `ansible_facts['distribution_release']` de forma dinámica. En Ubuntu 24.04 (Noble) u otras releases se añade el repo correcto pero con la clave incorrecta.

**Fix:** hacer la URL de la clave dinámica usando `distribution_release`, igual que la URL del repo.

---

### `tests/test.yml` — `remote_user: root`

El fichero de tests está configurado con `remote_user: root`. Si se ejecuta directamente sobre localhost aplicaría todas las tareas con privilegios completos sin prompt de sudo.

**Fix:** cambiar a `remote_user: "{{ lookup('env', 'USER') }}"` y añadir `become: true` donde sea necesario, igual que el playbook principal.

---

### `tasks/opencode.yml` — `curl | bash` sin verificación de integridad

El instalador de OpenCode se descarga y ejecuta directamente sin verificar checksum ni firma. Aceptable en máquinas personales, pero un riesgo si el endpoint se ve comprometido.

**Fix:** descargar una release concreta de GitHub con `get_url` + `checksum:`, o al menos pintar la versión instalada en los logs para detectar cambios inesperados.

---

### `defaults/main.yml` — `nodejs_version` definida pero no usada

La variable `nodejs_version: "24.14.0"` está declarada pero ningún task la referencia. El gestor `n` instala la versión `lts` en lugar de la versión pinada.

**Fix:** usar `nodejs_version` en el task de instalación de Node (`/tmp/n {{ nodejs_version }}`), igual que se hace con `sdkman_default_java_version` para Java.
