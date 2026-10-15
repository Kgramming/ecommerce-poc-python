<template>
  <header class="site-head">
    <div class="wrap head-inner">
      <RouterLink to="/" class="brand">
        <span class="brand-mark">M</span>
        <span class="brand-name display">Meridian <em>Supply</em></span>
      </RouterLink>
      <nav class="nav">
        <RouterLink to="/" class="nav-link" active-class="active">Shop</RouterLink>
        <RouterLink to="/admin" class="nav-link" active-class="active">Orders</RouterLink>
        <RouterLink to="/admin/catalog" class="nav-link" active-class="active">Catalog</RouterLink>
      </nav>
      <div class="head-right">
        <span class="acting-as faint" title="Demo user for placing orders">
          {{ userLabel }}
        </span>
        <button class="bag-btn" @click="$emit('open-cart')" aria-label="Open bag">
          <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.8">
            <path d="M6 8h15l-1.5 9h-12z"/><path d="M6 8l-1-4H2"/><circle cx="9" cy="20" r="1.6"/><circle cx="18" cy="20" r="1.6"/>
          </svg>
          <span v-if="count > 0" class="bag-count num">{{ count }}</span>
        </button>
      </div>
    </div>
  </header>
</template>

<script setup>
import { computed } from 'vue'
import { useCart } from '../stores/cart.js'

defineEmits(['open-cart'])
const { count } = useCart()
/* Fixed demo user for order placement (matches seed user #2). */
const userLabel = computed(() => 'Signed in as Jane Smith')
</script>

<style scoped>
.site-head {
  position: sticky;
  top: 0;
  z-index: 100;
  background: rgba(250, 249, 246, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--line);
}
.head-inner {
  display: flex;
  align-items: center;
  gap: 32px;
  height: 64px;
}
.brand { display: flex; align-items: center; gap: 10px; text-decoration: none; }
.brand-mark {
  width: 32px; height: 32px;
  background: var(--ink); color: var(--paper);
  border-radius: 8px;
  display: flex; align-items: center; justify-content: center;
  font-family: var(--font-display); font-weight: 700; font-size: 18px;
}
.brand-name { font-size: 18px; }
.brand-name em { font-style: normal; color: var(--ink-faint); font-weight: 500; }
.nav { display: flex; gap: 4px; }
.nav-link {
  text-decoration: none;
  font-size: 14px; font-weight: 500;
  color: var(--ink-soft);
  padding: 8px 14px;
  border-radius: 999px;
}
.nav-link:hover { background: var(--paper-2); color: var(--ink); }
.nav-link.active { background: var(--ink); color: #fff; }
.head-right { margin-left: auto; display: flex; align-items: center; gap: 16px; }
.acting-as { font-size: 12.5px; }
.bag-btn {
  position: relative;
  border: 1px solid var(--line);
  background: var(--card);
  border-radius: 999px;
  width: 40px; height: 40px;
  display: flex; align-items: center; justify-content: center;
  cursor: pointer; color: var(--ink);
  transition: border-color 0.12s;
}
.bag-btn:hover { border-color: var(--ink-soft); }
.bag-count {
  position: absolute;
  top: -6px; right: -6px;
  background: var(--accent); color: #fff;
  font-size: 11px; font-weight: 600;
  min-width: 20px; height: 20px;
  border-radius: 999px;
  display: flex; align-items: center; justify-content: center;
  padding: 0 5px;
}
@media (max-width: 760px) {
  .acting-as { display: none; }
  .head-inner { gap: 16px; }
}
</style>
