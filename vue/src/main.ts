import { createApp } from 'vue'
import { createPinia } from 'pinia'
import FileViewer from '@file-viewer/vue3'
import router from './router'
import './assets/index.css'
import App from './App.vue'

createApp(App).use(createPinia()).use(router).use(FileViewer).mount('#app')
