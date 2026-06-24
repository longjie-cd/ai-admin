<script setup lang="ts">
import { computed } from 'vue'

const props = withDefaults(defineProps<{
  variant?: 'primary' | 'default' | 'secondary' | 'destructive' | 'outline' | 'ghost' | 'link'
  size?: 'sm' | 'md' | 'lg' | 'icon'
  disabled?: boolean
  class?: string
}>(), { variant: 'primary', size: 'md' })

const base = 'ds-btn inline-flex items-center justify-center gap-1.5 whitespace-nowrap select-none focus-visible:outline-none disabled:pointer-events-none disabled:opacity-45'

const variants: Record<string, string> = {
  primary:     'ds-btn--primary',
  default:     'ds-btn--primary',
  secondary:   'ds-btn--secondary',
  destructive: 'ds-btn--destructive',
  outline:     'ds-btn--outline',
  ghost:       'ds-btn--ghost',
  link:        'ds-btn--link',
}

const sizes: Record<string, string> = {
  sm:   'ds-btn--sm',
  md:   'ds-btn--md',
  lg:   'ds-btn--lg',
  icon: 'ds-btn--icon',
}

const classes = computed(() =>
  [base, variants[props.variant], sizes[props.size], props.class].filter(Boolean).join(' ')
)
</script>

<template>
  <button :class="classes" :disabled="disabled">
    <slot />
  </button>
</template>

<style>
.ds-btn {
  border-radius: var(--btn-radius);
  font-size: var(--btn-font-size);
  font-weight: var(--btn-font-weight);
  transition: background var(--btn-transition), color var(--btn-transition),
              box-shadow var(--btn-transition), border-color var(--btn-transition),
              transform var(--transition-fast);
}
.ds-btn:active:not(:disabled) { transform: scale(0.98); }

.ds-btn--sm   { height: var(--btn-h-sm); padding: 0 var(--btn-px-sm); font-size: 0.8125rem; border-radius: var(--radius-sm); }
.ds-btn--md   { height: var(--btn-h-md); padding: 0 var(--btn-px-md); }
.ds-btn--lg   { height: var(--btn-h-lg); padding: 0 var(--btn-px-lg); font-size: 0.9375rem; border-radius: var(--radius-lg); }
.ds-btn--icon { height: var(--btn-h-md); width: var(--btn-h-md); padding: 0; }

.ds-btn--primary {
  background: hsl(var(--primary));
  color: hsl(var(--primary-foreground));
  box-shadow: 0 1px 2px hsl(var(--primary) / 0.25);
}
.ds-btn--primary:hover:not(:disabled) { background: hsl(var(--primary) / 0.88); box-shadow: 0 2px 8px hsl(var(--primary) / 0.3); }
.ds-btn--primary:focus-visible        { box-shadow: 0 0 0 3px hsl(var(--primary) / 0.25); }

.ds-btn--secondary {
  background: hsl(var(--bg-sunken));
  color: hsl(var(--text-1));
  border: 1px solid hsl(var(--border-default));
}
.ds-btn--secondary:hover:not(:disabled) { background: hsl(var(--bg-active)); border-color: hsl(var(--border-strong)); }
.ds-btn--secondary:focus-visible        { box-shadow: 0 0 0 3px hsl(var(--border-strong) / 0.4); }

.ds-btn--destructive {
  background: hsl(var(--red-500));
  color: #fff;
}
.ds-btn--destructive:hover:not(:disabled) { background: hsl(var(--red-600)); }
.ds-btn--destructive:focus-visible        { box-shadow: 0 0 0 3px hsl(var(--red-500) / 0.25); }

.ds-btn--outline {
  background: transparent;
  color: hsl(var(--text-1));
  border: 1px solid hsl(var(--border-default));
}
.ds-btn--outline:hover:not(:disabled) { background: hsl(var(--bg-hover)); border-color: hsl(var(--border-strong)); }
.ds-btn--outline:focus-visible        { box-shadow: 0 0 0 3px hsl(var(--border-strong) / 0.35); }

.ds-btn--ghost {
  background: transparent;
  color: hsl(var(--text-2));
}
.ds-btn--ghost:hover:not(:disabled) { background: hsl(var(--bg-hover)); color: hsl(var(--text-1)); }

.ds-btn--link {
  background: transparent;
  color: hsl(var(--primary));
  padding: 0; height: auto;
  font-weight: 400;
  text-decoration: underline;
  text-underline-offset: 3px;
}
.ds-btn--link:hover:not(:disabled) { opacity: 0.75; }
</style>
