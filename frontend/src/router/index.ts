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
    {
      path: "/:pathMatch(.*)*",
      name: "NotFound",
      component: () => import("../views/NotFoundView.vue"),
    },
  ],
});

router.beforeEach((to, _from) => {
  const auth = useAuthStore();
  const guestToken = localStorage.getItem("guest_token");
  if (to.meta.requiresAuth && !auth.isLoggedIn && !guestToken) {
    return "/login";
  }
});
router.afterEach((to) => {
  const titles: Record<string, string> = {
    Dashboard: "我的旅程 - TravelMate",
    TripDetail: "行程 - TravelMate",
    Login: "登入 - TravelMate",
    Register: "註冊 - TravelMate",
    Admin: "管理後台 - TravelMate",
    GuestJoin: "加入行程 - TravelMate",
    SharedTrip: "分享行程 - TravelMate",
  };
  document.title = titles[to.name as string] || "TravelMate";
});

export default router;
