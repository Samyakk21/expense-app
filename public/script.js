/* ==========================================================================
   Expense Splitter Toolkit — Frontend Logic
   ========================================================================== */

// API base URL.
// - On Vercel / same-origin deployments, this is "" (calls the API on the same domain).
// - When opening the frontend locally (file:// or a separate static server),
//   fall back to the local backend at http://127.0.0.1:8000.
const isLocalHost = ["localhost", "127.0.0.1"].includes(window.location.hostname);
const BASE =
  window.location.protocol === "file:" || (isLocalHost && window.location.port !== "8000")
    ? "http://127.0.0.1:8000"
    : "";

let splitMode = "equal"; // 'equal' | 'exact'
let nextUserId = 1;

// ---------------------------------------------------------------------------
// Init
// ---------------------------------------------------------------------------
document.addEventListener("DOMContentLoaded", () => {
  loadData();
  initSplitMode();
});

// ---------------------------------------------------------------------------
// API helpers
// ---------------------------------------------------------------------------
async function api(path, options = {}) {
  const res = await fetch(`${BASE}${path}`, {
    headers: { "Content-Type": "application/json", ...options.headers },
    ...options,
  });
  if (!res.ok) {
    const err = await res.json().catch(() => ({ detail: res.statusText }));
    throw new Error(err.detail || `Request failed (${res.status})`);
  }
  if (res.status === 204) return null;
  return res.json();
}

function toast(msg, type = "success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = `toast ${type}`;
  t.style.display = "block";
  setTimeout(() => (t.style.display = "none"), 3000);
}

function setStatus(connected) {
  const el = document.getElementById("sync-status");
  if (connected) {
    el.textContent = "Connected";
    el.className = "status-badge status-connected";
  } else {
    el.textContent = "Offline";
    el.className = "status-badge status-disconnected";
  }
}

// ---------------------------------------------------------------------------
// Load all data
// ---------------------------------------------------------------------------
async function loadData() {
  try {
    await Promise.all([loadUsers(), loadExpenses()]);
    setStatus(true);
  } catch (err) {
    console.error(err);
    setStatus(false);
    toast("Could not connect to the backend. Is the server running?", "error");
  }
}

async function loadUsers() {
  const users = await api("/users");
  nextUserId = users.length ? Math.max(...users.map((u) => u.id)) + 1 : 1;
  renderUsers(users);
  populateUserSelects(users);
}

async function loadExpenses() {
  const expenses = await api("/expenses");
  renderExpenses(expenses);
  updateStats(expenses);
}

// ---------------------------------------------------------------------------
// Users
// ---------------------------------------------------------------------------
function renderUsers(users) {
  const container = document.getElementById("users-list");
  container.innerHTML = "";
  if (!users.length) {
    container.innerHTML = '<p class="empty-msg">👥 Nobody here yet</p>';
    return;
  }
  users.forEach((u) => {
    const chip = document.createElement("div");
    chip.className = "user-chip";
    chip.innerHTML = `
      <span class="user-avatar" aria-hidden="true">${escapeHtml(u.name.trim().charAt(0).toUpperCase())}</span>
      <span>${escapeHtml(u.name)}</span>
      <button class="chip-remove" title="Remove" onclick="event.stopPropagation(); deleteUser(${u.id})">&times;</button>
    `;
    container.appendChild(chip);
  });
}

async function deleteUser(userId) {
  if (!confirm("Remove this person? (Only allowed if they have no expenses.)")) return;
  try {
    await api(`/users/${userId}`, { method: "DELETE" });
    toast("Person removed");
    loadData();
  } catch (err) {
    toast(err.message, "error");
  }
}

function openUserModal() {
  document.getElementById("user-modal").style.display = "block";
  document.getElementById("modal-user-name").value = "";
  document.getElementById("modal-user-id").value = "";
  document.getElementById("modal-user-name").focus();
}

function closeUserModal() {
  document.getElementById("user-modal").style.display = "none";
}

async function handleAddUser(e) {
  e.preventDefault();
  const name = document.getElementById("modal-user-name").value.trim();
  const idInput = document.getElementById("modal-user-id").value.trim();
  const userId = idInput ? parseInt(idInput, 10) : nextUserId;

  if (!name) return toast("Please enter a name", "error");

  try {
    await api("/users", {
      method: "POST",
      body: JSON.stringify({ user_id: userId, name: name }),
    });
    toast(`Added ${name}`);
    closeUserModal();
    loadUsers();
    nextUserId = Math.max(nextUserId, userId + 1);
  } catch (err) {
    toast(err.message, "error");
  }
}

// ---------------------------------------------------------------------------
// Split mode & split rows
// ---------------------------------------------------------------------------
function initSplitMode() {
  document.getElementById("mode-equal").addEventListener("click", () => setSplitMode("equal"));
  document.getElementById("mode-exact").addEventListener("click", () => setSplitMode("exact"));
}

function setSplitMode(mode) {
  splitMode = mode;
  document.getElementById("mode-equal").classList.toggle("active", mode === "equal");
  document.getElementById("mode-exact").classList.toggle("active", mode === "exact");
  rebuildSplits();
}

function populateUserSelects(users) {
  const payerSelect = document.getElementById("expense-payer");
  const current = payerSelect.value;
  payerSelect.innerHTML = users.map((u) => `<option value="${u.id}">${escapeHtml(u.name)}</option>`).join("");
  if (users.find((u) => u.id == current)) payerSelect.value = current;
  // Keep the Add Expense split rows in sync with the people list.
  rebuildSplits();
}

function rebuildSplits() {
  const container = document.getElementById("splits-container");
  const payerSelect = document.getElementById("expense-payer");
  const payerId = parseInt(payerSelect.value, 10);

  // Collect existing user IDs from current split rows
  const existing = [];
  document.querySelectorAll(".split-row").forEach((row) => {
    const sel = row.querySelector("select");
    if (sel) existing.push(parseInt(sel.value, 10));
  });

  container.innerHTML = "";
  // Use all users as default split participants
  const users = Array.from(document.getElementById("expense-payer").options).map((o) => ({
    id: parseInt(o.value, 10),
    name: o.text,
  }));

  users.forEach((u) => {
    const row = document.createElement("div");
    row.className = "split-row";
    let amountInput = "";
    if (splitMode === "exact") {
      amountInput = `<input type="number" step="0.01" min="0" placeholder="0.00" class="split-amount" />`;
    }
    row.innerHTML = `
      <select class="split-user">${users
        .map((x) => `<option value="${x.id}" ${x.id === u.id ? "selected" : ""}>${escapeHtml(x.name)}</option>`)
        .join("")}</select>
      ${amountInput}
      <button type="button" class="remove-split" onclick="this.closest('.split-row').remove()">&times;</button>
    `;
    container.appendChild(row);
  });

  // If equal mode, pre-select all users; if exact, start empty amounts
  if (splitMode === "equal") {
    // all rows already show all users
  }
}

// ---------------------------------------------------------------------------
// Add Expense
// ---------------------------------------------------------------------------
async function addExpense() {
  const payerId = parseInt(document.getElementById("expense-payer").value, 10);
  const amountVal = parseFloat(document.getElementById("expense-amount").value);

  if (!payerId || !amountVal || amountVal <= 0) {
    return toast("Please enter a valid amount", "error");
  }

  const rows = document.querySelectorAll(".split-row");
  const splitsObj = {};

  rows.forEach((row) => {
    const userSel = row.querySelector(".split-user");
    const amtInput = row.querySelector(".split-amount");
    const userId = parseInt(userSel.value, 10);

    let share;
    if (splitMode === "equal") {
      share = amountVal / rows.length;
    } else {
      share = parseFloat(amtInput.value);
      if (!share || share < 0) {
        throw new Error("Please enter valid split amounts");
      }
    }

    splitsObj[userId] = (splitsObj[userId] || 0) + share;
  });

  // Validate sum
  const total = Object.values(splitsObj).reduce((a, b) => a + b, 0);
  if (Math.abs(total - amountVal) > 0.01) {
    return toast(`Splits (₹${total.toFixed(2)}) must equal amount (₹${amountVal.toFixed(2)})`, "error");
  }

  try {
    await api("/expenses", {
      method: "POST",
      body: JSON.stringify({ payer_id: payerId, amount: amountVal, splits: splitsObj }),
    });
    toast("Expense added");
    document.getElementById("expense-amount").value = "";
    loadExpenses();
    loadUsers();
  } catch (err) {
    toast(err.message, "error");
  }
}

// ---------------------------------------------------------------------------
// Expenses list
// ---------------------------------------------------------------------------
function renderExpenses(expenses) {
  const container = document.getElementById("expenses-list");
  container.innerHTML = "";
  if (!expenses.length) {
    container.innerHTML = '<p class="empty-msg">🧾 No expenses. suspiciously cheap.</p>';
    return;
  }
  expenses.forEach((exp) => {
    const splitsText = Object.entries(exp.splits)
      .map(([uid, amt]) => `${uid}: ₹${parseFloat(amt).toFixed(2)}`)
      .join(", ");

    const item = document.createElement("div");
    item.className = "expense-item";
    item.innerHTML = `
      <span class="expense-avatar" aria-hidden="true">${escapeHtml(exp.payer_name.trim().charAt(0).toUpperCase())}</span>
      <div class="expense-info">
        <div class="expense-payer">${escapeHtml(exp.payer_name)} paid</div>
        <div class="expense-detail">Splits → ${escapeHtml(splitsText)}</div>
      </div>
      <div class="expense-amount">₹${parseFloat(exp.amount).toFixed(2)}</div>
      <span class="status-stamp status-pending">Pending</span>
      <div class="expense-actions">
        <button class="btn btn-outline btn-danger" onclick="deleteExpense(${exp.id})" title="Delete">Delete</button>
      </div>
    `;
    container.appendChild(item);
  });
}

async function deleteExpense(expenseId) {
  if (!confirm("Delete this expense?")) return;
  try {
    await api(`/expenses/${expenseId}`, { method: "DELETE" });
    toast("Expense deleted");
    loadExpenses();
    loadUsers();
  } catch (err) {
    toast(err.message, "error");
  }
}

function updateStats(expenses) {
  const totalCount = expenses.length;
  const totalAmount = expenses.reduce((s, e) => s + parseFloat(e.amount), 0);
  document.getElementById("stat-expenses").textContent = totalCount;
  document.getElementById("stat-amount").textContent = `₹${totalAmount.toFixed(2)}`;

  // Settled vs pending — use current balances to derive pending
  // (simple heuristic: sum of absolute debtor amounts = pending)
  computeBalancesForStats();
}

// ---------------------------------------------------------------------------
// Balances & Settlements
// ---------------------------------------------------------------------------
async function loadBalances() {
  try {
    const balances = await api("/balances");
    renderBalances(balances);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function loadSettlements() {
  try {
    const settlements = await api("/settlements");
    renderSettlements(settlements);
  } catch (err) {
    toast(err.message, "error");
  }
}

async function computeBalancesForStats() {
  try {
    const balances = await api("/balances");
    const pending = balances
      .filter((b) => b.balance < 0)
      .reduce((s, b) => s + Math.abs(b.balance), 0);
    document.getElementById("stat-pending").textContent = `₹${pending.toFixed(2)}`;
    const settled = Math.max(0, 0); // placeholder; real settlement tracking would need history
    document.getElementById("stat-settled").textContent = `₹${settled.toFixed(2)}`;
  } catch (e) {
    // ignore
  }
}

function renderBalances(balances) {
  const container = document.getElementById("balances-output");
  container.innerHTML = "";
  if (!balances.length) {
    container.innerHTML = '<p class="hint">No balances to show.</p>';
    return;
  }
  const list = document.createElement("div");
  list.className = "balance-list";
  balances.forEach((b) => {
    const cls = b.balance > 0.01 ? "positive" : b.balance < -0.01 ? "negative" : "zero";
    const sign = b.balance > 0 ? "+" : b.balance < 0 ? "−" : "";
    const item = document.createElement("div");
    item.className = `balance-item ${cls}`;
    item.innerHTML = `
      <span class="balance-name">${escapeHtml(b.user)}</span>
      <span class="balance-amount ${cls}">${sign}₹${Math.abs(b.balance).toFixed(2)}</span>
    `;
    list.appendChild(item);
  });
  container.appendChild(list);
}

function renderSettlements(settlements) {
  const container = document.getElementById("balances-output");
  container.innerHTML = "";
  if (!settlements.length) {
    container.innerHTML = '<div class="all-square">All square. go have a samosa 🎉</div>';
    return;
  }
  const list = document.createElement("div");
  list.className = "settlement-list";
  settlements.forEach((s) => {
    const item = document.createElement("div");
    item.className = "settlement-item";
    item.innerHTML = `
      <div class="settlement-flow">
        <span class="settlement-from">${escapeHtml(s.from_user)}</span>
        <span class="settlement-verb">owes</span>
        <span class="settlement-arrow">→</span>
        <span class="settlement-to">${escapeHtml(s.to_user)}</span>
      </div>
      <span class="settlement-amount">₹${s.amount.toFixed(2)}</span>
    `;
    list.appendChild(item);
  });
  container.appendChild(list);
}

// ---------------------------------------------------------------------------
// Utils
// ---------------------------------------------------------------------------
function escapeHtml(text) {
  const div = document.createElement("div");
  div.textContent = text;
  return div.innerHTML;
}
