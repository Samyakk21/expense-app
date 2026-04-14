const BASE = "http://127.0.0.1:8000";

const users = {}; // id → name mapping

// ---------- TOAST ----------
function toast(msg, type = "success") {
  const t = document.getElementById("toast");
  if (!t) return;

  t.textContent = msg;
  t.className = type === "success" ? "toast-success" : "toast-error";
  t.style.display = "block";

  setTimeout(() => {
    t.style.display = "none";
  }, 2000);
}

// ---------- UPDATE DROPDOWN ----------
function updateUserDropdowns() {
  const payer = document.getElementById("payer");
  if (!payer) return;

  payer.innerHTML = "";

  Object.entries(users).forEach(([id, name]) => {
    const opt = document.createElement("option");
    opt.value = id;
    opt.textContent = name;
    payer.appendChild(opt);
  });
}

// ---------- RENDER SPLITS ----------
function renderAllSplits() {
  const container = document.getElementById("splits");
  if (!container) return;

  container.innerHTML = "";

  Object.entries(users).forEach(([id, name]) => {
    const div = document.createElement("div");
    div.className = "split-row";

    div.innerHTML = `
      <input type="checkbox" class="include-user" data-id="${id}" checked>
      <input type="text" value="${name}" disabled>
      <input type="number" placeholder="Amount" data-id="${id}">
    `;

    container.appendChild(div);
  });
}

// ---------- HANDLE CHECKBOX TOGGLE ----------
document.addEventListener("change", (e) => {
  if (e.target.classList.contains("include-user")) {
    const row = e.target.parentElement;
    const amountInput = row.querySelector("input[type='number']");

    amountInput.disabled = !e.target.checked;

    if (!e.target.checked) {
      amountInput.value = "";
    }
  }
});

// ---------- ADD USER ----------
async function addUser() {
  const nameInput = document.getElementById("name");
  const name = nameInput.value.trim();

  if (!name) {
    return toast("Enter a valid name", "error");
  }

  try {
    const res = await fetch(`${BASE}/users`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({ name })
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }

    const data = await res.json();

    users[data.id] = data.name;

    updateUserDropdowns();
    renderAllSplits();

    nameInput.value = "";

    toast("User added");

  } catch (e) {
    console.error(e);
    toast("Failed to add user", "error");
  }
}

// ---------- ADD EXPENSE ----------
async function addExpense() {
  const payerEl = document.getElementById("payer");
  const amountEl = document.getElementById("amount");

  if (!payerEl || !amountEl) {
    console.error("Required input elements missing");
    return;
  }

  const description = document.getElementById("description")?.value || "";
  const payer = parseInt(payerEl.value);
  const amount = parseFloat(amountEl.value);

  if (!payer || !amount || amount <= 0) {
    return toast("Invalid payer or amount", "error");
  }

  const splits = {};

  document.querySelectorAll(".split-row").forEach(row => {
    const checkbox = row.querySelector(".include-user");
    const input = row.querySelector("input[type='number']");

    if (!checkbox.checked) return;

    const id = checkbox.dataset.id;
    const val = parseFloat(input.value);

    if (!isNaN(val) && val > 0) {
      splits[id] = val;
    }
  });

  if (Object.keys(splits).length === 0) {
    return toast("Enter at least one valid split", "error");
  }

  try {
    const res = await fetch(`${BASE}/expenses`, {
      method: "POST",
      headers: {
        "Content-Type": "application/json"
      },
      body: JSON.stringify({
        payer_id: payer,
        amount: amount,
        splits: splits,
        description: description   // ← optional but now actually used
      })
    });

    if (!res.ok) {
      const err = await res.text();
      throw new Error(err);
    }

    toast("Expense added");

    addExpenseCard(payer, amount, splits);

    amountEl.value = "";
    renderAllSplits();

  } catch (e) {
    console.error(e);
    toast("Failed to add expense", "error");
  }
}



// ---------- DISPLAY EXPENSE ----------
function addExpenseCard(payer, amount, splits) {
  const list = document.getElementById("expenseList");
  if (!list) return;

  const div = document.createElement("div");
  div.className = "expense-item";

  const payerName = users[payer] || `User ${payer}`;

  const splitText = Object.entries(splits)
    .map(([id, amt]) => `${users[id] || id}: ${amt}`)
    .join(", ");

  div.textContent = `${payerName} paid Rs. ${amount} → ${splitText}`;

  list.appendChild(div);
}

// ---------- GET BALANCES ----------
async function getBalances() {
  const res = await fetch(`${BASE}/balances`);
  const data = await res.json();

  const formatted = Object.entries(data)
    .map(([name, amt]) => `${name}: ${amt}`)
    .join("\n");

  document.getElementById("output").textContent = formatted;
}

// ---------- GET SETTLEMENTS ----------
async function getSettlements() {
  const res = await fetch(`${BASE}/settlements`);
  const data = await res.json();

  const formatted = data
    .map(t => `${t.from} → ${t.to}: ${t.amount}`)
    .join("\n");

  document.getElementById("output").textContent = formatted;
}