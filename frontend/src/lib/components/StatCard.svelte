<script>
  let { title = '', value = 0, color = 'blue', onclick = null, children } = $props();

  const colorMap = {
    blue: { bg: '#3b82f6', text: '#2563eb', light: '#eff6ff' },
    green: { bg: '#10b981', text: '#059669', light: '#ecfdf5' },
    yellow: { bg: '#f59e0b', text: '#d97706', light: '#fffbeb' },
    red: { bg: '#ef4444', text: '#dc2626', light: '#fef2f2' },
    purple: { bg: '#8b5cf6', text: '#7c3aed', light: '#f5f3ff' },
  };

  const selectedColor = $derived(colorMap[color] || colorMap.blue);
</script>

<div class="stat-card" role={onclick ? 'button' : undefined} {onclick} style={onclick ? 'cursor: pointer;' : ''}>
  <div class="stat-icon" style="background-color: {selectedColor.bg};">
    {@render children?.()}
  </div>
  <div class="stat-info">
    <h3>{value}</h3>
    <p>{title}</p>
  </div>
</div>

<style>
  .stat-card {
    transition: transform 0.15s, box-shadow 0.15s;
  }
  .stat-card:hover {
    transform: translateY(-2px);
    box-shadow: var(--shadow);
  }
</style>
