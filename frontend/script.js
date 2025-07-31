async function convert() {
  const code = document.getElementById("code").value;
  const res = await fetch("http://localhost:5000/to_qasm", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ code }),
  });

  const data = await res.json();
  const output = document.getElementById("output");
  if (data.success) {
    output.textContent = data.qasm;
  } else {
    output.textContent = `Error: ${data.error}`;
  }
}
