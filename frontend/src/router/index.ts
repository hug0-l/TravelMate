import { createRouter, createWebHistory } from "vue-router";
import { useAuthStore } from "../stores/auth";

const router = createRouter({
  history: createWebHistory(),
  routes: [
    {
      path: "/login",
      name: "Login",
      component: () => import("../views/LoginView.vue"),
    },
    {
      path: "/register",
      name: "Register",
      component: () => import("../views/RegisterView.vue"),
    },
    {
      path: "/",
      name: "Dashboard",
      component: () => import("../views/DashboardView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/trips/:id",
      name: "TripDetail",
      component: () => import("../views/TripView.vue"),
      meta: { requiresAuth: true },
    },
    {
      path: "/share/:code",
      name: "SharedTrip",
      component: () => import("../views/SharedTripView.vue"),
    },
    {
      path: "/join",
      name: "GuestJoin",
      component: () => import("../views/GuestJoinView.vue"),
    },
    {
      path: "/admin",
      name: "Admin",
      component: () => import("../views/AdminView.vue"),
      meta: { requiresAuth: true },
    },
  ],
});

router.beforeEach((to, _from) => {
  const auth = useAuthStore();
  if (to.meta.requiresAuth && !auth.isLoggedIn) {
    return "/login";
  }
});

export default router;
