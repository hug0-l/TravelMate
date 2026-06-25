import { ref } from "vue";
import api from "../api/client";
import { useToast } from "./useToast";

interface BudgetSummary {
  total_expenses: number;
  by_category: Record<string, number>;
  per_person: Record<string, number>;
  balances: Array<{ user_id: string; name: string; paid: number; share: number; balance: number }>;
}

interface ExpenseItem {
  id: string;
  title: string;
  amount: number;
  category: string;
  paid_by: string;
  paid_by_name: string;
  splits: Array<{ user_id: string; name: string }>;
}

interface SettleUpData {
  transactions: Array<{ from_user_id: string; from_user_name: string; to_user_id: string; to_user_name: string; amount: number }>;
  total_balance: Record<string, number>;
}

export function useTripBudget(tripId: string) {
  const { add: addToast } = useToast();
  const budgetData = ref<BudgetSummary | null>(null);
  const budgetLoading = ref(false);
  const expenses = ref<ExpenseItem[]>([]);
  const expensesLoading = ref(false);
  const showAddExpense = ref(false);
  const showSettleUp = ref(false);
  const settleUpData = ref<SettleUpData | null>(null);
  const settleLoading = ref(false);

  const newExpenseTitle = ref("");
  const newExpenseAmount = ref<number | null>(null);
  const newExpenseCategory = ref<string>("other");
  const newExpensePaidBy = ref("");
  const newExpenseSplitWith = ref<string[]>([]);
  const creatingExpense = ref(false);

  async function fetchExpenses() {
    expensesLoading.value = true;
    try {
      const res = await api.get(`/trips/${tripId}/expenses`);
      expenses.value = res.data;
    } catch {
      expenses.value = [];
    } finally {
      expensesLoading.value = false;
    }
  }

  async function fetchBudget() {
    budgetLoading.value = true;
    try {
      const res = await api.get(`/trips/${tripId}/budget-summary`);
      budgetData.value = res.data;
    } catch {
      budgetData.value = null;
    } finally {
      budgetLoading.value = false;
    }
  }

  async function handleDeleteExpense(expenseId: string) {
    try {
      await api.delete(`/expenses/${expenseId}`);
      await fetchExpenses();
      await fetchBudget();
    } catch {
      addToast("error", "刪除支出失敗");
    }
  }

  function openAddExpense(payerId?: string) {
    newExpenseTitle.value = "";
    newExpenseAmount.value = null;
    newExpenseCategory.value = "other";
    newExpensePaidBy.value = payerId || "";
    newExpenseSplitWith.value = [];
    showAddExpense.value = true;
  }

  async function handleAddExpense(paidBy: string) {
    if (!newExpenseTitle.value || newExpenseAmount.value === null || !paidBy || creatingExpense.value) return;
    creatingExpense.value = true;
    try {
      await api.post(`/trips/${tripId}/expenses`, {
        title: newExpenseTitle.value.trim(),
        amount: newExpenseAmount.value,
        category: newExpenseCategory.value,
        paid_by: paidBy,
        split_with: newExpenseSplitWith.value,
      });
      showAddExpense.value = false;
      newExpenseTitle.value = "";
      newExpenseAmount.value = null;
      newExpenseCategory.value = "other";
      newExpensePaidBy.value = "";
      newExpenseSplitWith.value = [];
      await fetchExpenses();
      await fetchBudget();
    } catch {
      addToast("error", "新增支出失敗");
    } finally {
      creatingExpense.value = false;
    }
  }

  async function fetchSettleUp() {
    settleLoading.value = true;
    try {
      const res = await api.get(`/trips/${tripId}/settle-up`);
      settleUpData.value = res.data;
      showSettleUp.value = true;
    } catch {
      addToast("error", "計算結算失敗");
    } finally {
      settleLoading.value = false;
    }
  }

  function copySettleUp() {
    if (!settleUpData.value) return;
    let text = "💰 結算計畫\n";
    for (const t of settleUpData.value.transactions) {
      text += `${t.from_user_name} → 轉 $${t.amount} → ${t.to_user_name}\n`;
    }
    if (navigator.clipboard) {
      navigator.clipboard.writeText(text);
    }
  }

  return {
    budgetData, budgetLoading,
    expenses, expensesLoading,
    showAddExpense, showSettleUp,
    settleUpData, settleLoading,
    newExpenseTitle, newExpenseAmount, newExpenseCategory, newExpensePaidBy, newExpenseSplitWith, creatingExpense,
    fetchExpenses, fetchBudget, handleDeleteExpense,
    openAddExpense, handleAddExpense,
    fetchSettleUp, copySettleUp,
  };
}