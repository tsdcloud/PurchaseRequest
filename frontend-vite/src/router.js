import { createRouter, createWebHistory } from 'vue-router';
import RecoverPassword from './components/RecoverPassword.vue';
import Purchases from './components/Purchases.vue';
import Inventory from './components/Inventory.vue';
import Suppliers from './components/Suppliers.vue';
import Providers from './components/Providers.vue';

// Define route components
const routes = [
  { path: '/recover_password', component: RecoverPassword },
  { path: '/purchases', component: Purchases },
  { path: '/inventory', component: Inventory },
  { path: '/suppliers', component: Suppliers },
  { path: '/providers', component: Providers },
];

// Create the router instance
const router = createRouter({
  history: createWebHistory(),
  routes, // short for `routes: routes`
});

export default router;