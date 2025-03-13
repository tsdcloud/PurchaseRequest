import { createWebHistory, createRouter } from "vue-router"
import SignIn from "./views/SignIn.vue"
import RecoverPassword from './views/RecoverPassword.vue'
import Inventory from "./views/Inventory.vue"
import Providers from "./views/Providers.vue"
import Provisioning from "./views/Provisioning.vue"
import Purchases from "./views/Purchases.vue"
import Suppliers from "./views/Suppliers.vue"
import PageNotFound from "./views/404.vue"

const routes = [
  {
    path: "/recover_password",
    name: "RecoverPassword",
    component: RecoverPassword,
  },
  {
    path: "/providers",
    name: "Providers",
    component: Providers,
  },
  {
    path: "/inventory",
    name: "Inventory",
    component: Inventory,
  },
  {
    path: "/provisioning",
    name: "Provisioning",
    component: Provisioning,
  },
  {
    path: "/purchases",
    name: "Purchases",
    component: Purchases,
  },
  {
    path: "/suppliers",
    name: "Suppliers",
    component: Suppliers,
  },
  {
    path: '/:catchAll(.*)*',
    name: "PageNotFound",
    component: PageNotFound,
  },
]

const router = createRouter({
  history: createWebHistory(),
  routes
})

export default router