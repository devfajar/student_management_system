<script>
  import { X } from 'lucide-svelte';

  let { show = false, title = '', onclose, children } = $props();
</script>

{#if show}
  <div class="modal-backdrop" onclick={onclose} role="presentation">
    <div class="modal-content" onclick={(e) => e.stopPropagation()} role="dialog" aria-modal="true" tabindex="-1">
      <div class="modal-header">
        <h3 class="modal-title">{title}</h3>
        <button class="modal-close-btn" onclick={onclose} aria-label="Close modal">
          <X size={18} />
        </button>
      </div>
      <div class="modal-body">
        {@render children?.()}
      </div>
    </div>
  </div>
{/if}

<style>
  .modal-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding-bottom: 16px;
    border-bottom: 1px solid var(--border);
    margin-bottom: 20px;
  }

  .modal-title {
    font-size: 16px;
    font-weight: 600;
    color: var(--text-main);
  }

  .modal-close-btn {
    background: transparent;
    border: none;
    cursor: pointer;
    color: var(--text-muted);
    display: flex;
    align-items: center;
    padding: 4px;
    border-radius: var(--radius-sm);
  }

  .modal-close-btn:hover {
    background: #f1f5f9;
    color: var(--text-main);
  }
</style>
