// ==========================================
// 1. EFEK MATRIX DIGITAL RAIN - VERSI NAMA KELOMPOK
// ==========================================
const canvas = document.getElementById("matrixCanvas");
const ctx = canvas.getContext("2d");

// Bikin canvas seukuran layar penuh
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

const names = [
  "ABDURRAHMAN",
  "IQBAL CHAIRUL",
  "ANNISA MUFLIHA",
  "TORU SETIA PUTRA",
  "TEKNIK_TELEKOMUNIKASI",
];

const fontSize = 16;
const columns = Math.floor(canvas.width / fontSize);
const drops = [];
const columnNames = [];

// Inisialisasi: Tentukan posisi jatuh dan tugaskan nama untuk setiap kolom
for (let x = 0; x < columns; x++) {
  // Posisi awal jatuh acak di atas layar agar tidak serentak
  drops[x] = Math.floor((Math.random() * canvas.height) / fontSize);
  // Tugaskan nama secara berurutan
  columnNames[x] = x % names.length;
}

function drawMatrix() {
  // Menimpa background dengan warna hitam transparan biar efeknya memudar pelan-pelan
  ctx.fillStyle = "rgba(0, 0, 0, 0.05)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);

  ctx.fillStyle = "#0f0"; // Hijau neon
  ctx.font = fontSize + "px monospace";

  for (let i = 0; i < drops.length; i++) {
    const nameIndex = columnNames[i];
    const currentName = names[nameIndex];
    const charIndex = drops[i] % currentName.length;
    const text = currentName[charIndex];

    ctx.fillText(text, i * fontSize, drops[i] * fontSize);

    if (drops[i] * fontSize > canvas.height && Math.random() > 0.975) {
      drops[i] = 0;
    }
    drops[i]++;
  }
}

// Jalankan animasi Matrix setiap 33 milidetik
setInterval(drawMatrix, 33);

// Handle resize layar
window.addEventListener("resize", () => {
  canvas.width = window.innerWidth;
  canvas.height = window.innerHeight;
});

// ==========================================
// 2. LOGIKA INTERAKSI CLI TERMINAL
// ==========================================
const terminalBody = document.getElementById("terminal-body");
const cmdInput = document.getElementById("cmd-input");
const commandHistory = document.getElementById("command-history");

const csrfToken = document.querySelector("[name=csrfmiddlewaretoken]").value;

// Daftar endpoint yang valid (sudah diubah ke 'predict')
const validPages = ["predict"];

terminalBody.addEventListener("click", () => {
  cmdInput.focus();
});

cmdInput.addEventListener("keypress", function (e) {
  if (e.key === "Enter") {
    const command = this.value.trim();
    if (command === "") return;

    // Cetak perintah ke layar
    commandHistory.innerHTML += `<br><span class="prompt">root@ubuntu-server:~# </span>${command}`;
    this.value = "";

    // 1. LOGIKA AUTH (Memasukkan Key)
    if (command.startsWith("auth ")) {
      const args = command.split(" ");
      const keyInput = args[1];

      if (keyInput) {
        commandHistory.innerHTML += `<br>> Verifying security key...`;

        // Kirim request ke backend Django
        fetch("/api/auth/", {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": csrfToken,
          },
          body: JSON.stringify({ key: keyInput }),
        })
          .then((response) => response.json())
          .then((data) => {
            if (data.status === "success") {
              commandHistory.innerHTML += `<br>> <span style="color: #27c93f;">${data.message}</span>`;
              commandHistory.innerHTML += `<br>> You may now use 'sudo predict' to access the module.`;
            } else {
              commandHistory.innerHTML += `<br>> <span style="color: #ff5f56;">${data.message}</span>`;
            }
            terminalBody.scrollTop = terminalBody.scrollHeight;
          })
          .catch((error) => {
            commandHistory.innerHTML += `<br>> <span style="color: #ff5f56;">Error connecting to server.</span>`;
          });
      } else {
        commandHistory.innerHTML += `<br>auth: missing key. Usage: auth {key}`;
      }
    }

    // 2. LOGIKA NAVIGASI (Redirect)
    else if (command.startsWith("sudo ")) {
      const args = command.split(" ");
      const targetView = args[1];

      if (targetView) {
        if (validPages.includes(targetView)) {
          commandHistory.innerHTML += `<br>> Requesting access to /${targetView}/...`;

          setTimeout(() => {
            window.location.href = `/${targetView}/`;
          }, 800);
        } else {
          commandHistory.innerHTML += `<br>page not found, "help --list" for more information`;
        }
      } else {
        commandHistory.innerHTML += `<br>sudo: missing target view. Usage: sudo {view_name}`;
      }
    }

    // 3. LOGIKA LAINNYA
    else if (command === "help --list") {
      commandHistory.innerHTML += `<br>Available commands:`;
      commandHistory.innerHTML += `<br>  [+] auth {key}  - Unlock system modules`;
      commandHistory.innerHTML += `<br>  [+] sudo {view} - Navigate to module (e.g., sudo predict)`;
      commandHistory.innerHTML += `<br>  [+] clear       - Clear terminal screen`;
    } else if (command === "clear") {
      commandHistory.innerHTML = "";
    } else {
      commandHistory.innerHTML += `<br>bash: ${command}: command not found.`;
    }

    // Pastikan scroll selalu ke paling bawah
    setTimeout(() => {
      terminalBody.scrollTop = terminalBody.scrollHeight;
    }, 50);
  }
});
