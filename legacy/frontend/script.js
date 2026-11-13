const BASE = "http://127.0.0.1:8000";

// ---------- TOAST ----------
function toast(msg, type="success") {
  const t = document.getElementById("toast");
  t.textContent = msg;
  t.className = type === "success" ? "toast-success" : "toast-error";
  t.style.display = "block";
  setTimeout(() => t.style.display = "none", 2000);
}

// ---------- USER ----------
async function addUser() {
  const id = parseInt(user_id.value);
  const nameVal = name.value;

  if (!id || !nameVal) return toast("Fill all fields", "error");

  try {
    await fetch(`${BASE}/users`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ user_id: id, name: nameVal })
    });

    toast("User added");
    user_id.value = "";
    name.value = "";

  } catch {
    toast("Error adding user", "error");
  }
}

// ---------- SPLITS ----------
function addSplit() {
  const div = document.createElement("div");
  div.className = "split-row";

  div.innerHTML = `
    <input type="number" placeholder="User ID">
    <input type="number" placeholder="Amount">
    <button onclick="this.parentElement.remove()">X</button>
  `;

  splits.appendChild(div);
}

// ---------- EXPENSE ----------
async function addExpense() {
  const payer = parseInt(payer_id.value);
  const amountVal = parseFloat(amount.value);

  if (!payer || !amountVal) return toast("Invalid input", "error");

  const rows = document.querySelectorAll(".split-row");
  const splitsObj = {};

  rows.forEach(r => {
    const inputs = r.querySelectorAll("input");
    if (inputs[0].value && inputs[1].value) {
      splitsObj[inputs[0].value] = parseFloat(inputs[1].value);
    }
  });

  try {
    await fetch(`${BASE}/expenses`, {
      method: "POST",
      headers: {"Content-Type": "application/json"},
      body: JSON.stringify({ payer_id: payer, amount: amountVal, splits: splitsObj })
    });

    toast("Expense added");

    addExpenseRow(payer, amountVal, splitsObj);

    payer_id.value = "";
    amount.value = "";
    splits.innerHTML = "";

  } catch {
    toast("Error adding expense", "error");
  }
}

// ---------- TABLE ----------
function addExpenseRow(payer, amount, splits) {
  const row = document.createElement("tr");

  row.innerHTML = `
    <td>${payer}</td>
    <td>${amount}</td>
    <td>${JSON.stringify(splits)}</td>
  `;

  expenseTable.appendChild(row);
}

// ---------- OUTPUT ----------
async function getBalances() {
  const res = await fetch(`${BASE}/balances`);
  const data = await res.json();
  output.textContent = JSON.stringify(data, null, 2);
}

async function getSettlements() {
  const res = await fetch(`${BASE}/settlements`);
  const data = await res.json();
  output.textContent = JSON.stringify(data, null, 2);
}