import { ref } from "vue";
import api from "../api/client";
import { useToast } from "./useToast";

interface Member {
  id: string;
  user_id: string;
  name: string;
  email: string;
  role: string;
}

export function useTripMembers(tripId: string) {
  const { add: addToast } = useToast();
  const showMemberModal = ref(false);
  const members = ref<Member[]>([]);
  const membersLoading = ref(false);
  const inviteEmail = ref("");
  const inviteMsg = ref("");

  async function fetchMembers() {
    membersLoading.value = true;
    try {
      const res = await api.get(`/trips/${tripId}/members`);
      members.value = res.data;
    } catch {
      members.value = [];
    } finally {
      membersLoading.value = false;
    }
  }

  async function handleInvite() {
    try {
      await api.post(`/trips/${tripId}/members/invite`, { email: inviteEmail.value.trim() });
      inviteMsg.value = "✅ 邀請成功！";
      inviteEmail.value = "";
      fetchMembers();
    } catch (e: any) {
      inviteMsg.value = e.response?.data?.detail || "邀請失敗";
    }
  }

  return {
    showMemberModal, members, membersLoading,
    inviteEmail, inviteMsg,
    fetchMembers, handleInvite,
  };
}