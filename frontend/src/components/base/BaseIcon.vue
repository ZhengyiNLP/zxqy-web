<template>
  <component
    :is="iconComp"
    :size="size"
    :color="color"
    :stroke-width="strokeWidth"
    :class="['base-icon', { 'base-icon-clickable': clickable }]"
    @click="$emit('click', $event)"
  />
</template>

<script setup lang="ts">
import { computed, type Component } from 'vue'

// 按需导入项目中用到的 Lucide 图标
import {
  AlertTriangle,
  Archive,
  ArrowUp,
  Bell,
  Bold,
  BookOpen,
  Calendar,
  Check,
  CheckCircle,
  ChevronDown,
  ChevronLeft,
  ChevronRight,
  Circle,
  Clock,
  Code,
  Copy,
  CornerDownLeft,
  Database,
  Download,
  Eye,
  EyeOff,
  ExternalLink,
  FileText,
  HelpCircle,
  Heading1,
  Heading2,
  Heading3,
  Home,
  Image,
  Info,
  Italic,
  LayoutGrid,
  Link,
  List,
  ListOrdered,
  Lock,
  LogOut,
  Maximize2,
  Minus,
  Minimize2,
  Paperclip,
  Pencil,
  PanelLeftClose,
  Pin,
  Plus,
  RefreshCw,
  Rocket,
  RotateCcw,
  Search,
  Send,
  Settings,
  Shield,
  Sigma,
  SlidersHorizontal,
  Sparkles,
  Star,
  Strikethrough,
  TextQuote,
  Trash2,
  User,
  Users,
  UserPlus,
  X,
  XCircle,
  Zap,
} from 'lucide-vue-next'

// 图标名 → 组件映射
const iconMap: Record<string, Component> = {
  'alert-triangle': AlertTriangle,
  'archive': Archive,
  'arrow-up': ArrowUp,
  'bell': Bell,
  'bold': Bold,
  'book-open': BookOpen,
  'calendar': Calendar,
  'check': Check,
  'check-circle': CheckCircle,
  'chevron-down': ChevronDown,
  'chevron-left': ChevronLeft,
  'chevron-right': ChevronRight,
  'circle': Circle,
  'clock': Clock,
  'code': Code,
  'copy': Copy,
  'corner-down-left': CornerDownLeft,
  'database': Database,
  'download': Download,
  'eye': Eye,
  'eye-off': EyeOff,
  'external-link': ExternalLink,
  'file-text': FileText,
  'heading-1': Heading1,
  'heading-2': Heading2,
  'heading-3': Heading3,
  'home': Home,
  'image': Image,
  'info': Info,
  'italic': Italic,
  'layout-grid': LayoutGrid,
  'link': Link,
  'list': List,
  'list-ordered': ListOrdered,
  'lock': Lock,
  'log-out': LogOut,
  'maximize-2': Maximize2,
  'minimize-2': Minimize2,
  'minus': Minus,
  'paperclip': Paperclip,
  'pencil': Pencil,
  'panel-left-close': PanelLeftClose,
  'pin': Pin,
  'plus': Plus,
  'refresh-cw': RefreshCw,
  'rocket': Rocket,
  'rotate-ccw': RotateCcw,
  'search': Search,
  'send': Send,
  'settings': Settings,
  'shield': Shield,
  'sigma': Sigma,
  'sliders-horizontal': SlidersHorizontal,
  'sparkles': Sparkles,
  'star': Star,
  'strikethrough': Strikethrough,
  'text-quote': TextQuote,
  'trash-2': Trash2,
  'user': User,
  'users': Users,
  'user-plus': UserPlus,
  'x': X,
  'x-circle': XCircle,
  'zap': Zap,
}

const props = withDefaults(defineProps<{
  name: string
  size?: number | string
  color?: string
  strokeWidth?: number | string
  clickable?: boolean
}>(), {
  size: 14,
  strokeWidth: 2,
  clickable: false,
})

defineEmits<{
  click: [e: MouseEvent]
}>()

const iconComp = computed(() => iconMap[props.name] || HelpCircle)
</script>

<style scoped>
.base-icon {
  display: inline-flex;
  flex-shrink: 0;
  vertical-align: middle;
}
.base-icon-clickable {
  cursor: pointer;
  transition: opacity 0.15s;
}
.base-icon-clickable:hover {
  opacity: 0.7;
}
</style>
