<template>
  <div class="card product fade-in">
    <div class="product-top">
      <span class="pill pill-neutral product-cat">{{ product.category }}</span>
      <span v-if="!product.active" class="pill pill-neutral">Inactive</span>
    </div>
    <h3 class="display product-title">{{ product.title }}</h3>
    <div class="product-tags">
      <span v-for="t in (product.tags || []).slice(0, 3)" :key="t" class="tag">{{ t }}</span>
    </div>
    <div class="product-foot">
      <span class="num product-price">{{ formatMoney(product.price) }}</span>
      <button
        v-if="product.active"
        class="btn btn-primary btn-sm"
        @click="$emit('add', product)"
      >Add to bag</button>
    </div>
  </div>
</template>

<script setup>
import { formatMoney } from '../api/client.js'
defineProps({ product: { type: Object, required: true } })
defineEmits(['add'])
</script>

<style scoped>
.product {
  padding: 20px;
  display: flex;
  flex-direction: column;
  gap: 10px;
  transition: transform 0.15s var(--ease), box-shadow 0.15s var(--ease);
}
.product:hover {
  transform: translateY(-2px);
  box-shadow: var(--shadow-md);
}
.product-top { display: flex; gap: 8px; align-items: center; }
.product-cat { text-transform: none; letter-spacing: 0.02em; }
.product-title { margin: 0; font-size: 19px; flex: 1; }
.product-tags { display: flex; gap: 6px; flex-wrap: wrap; min-height: 22px; }
.tag {
  font-size: 11.5px;
  color: var(--ink-soft);
  background: var(--paper-2);
  border-radius: 999px;
  padding: 3px 9px;
}
.product-foot {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-top: 4px;
}
.product-price { font-size: 17px; font-weight: 500; }
</style>
