document.getElementById('searchButton').addEventListener('click', function() {
    var input = document.querySelector('input[name="query"]');
    
    // Toggle input pencarian, tampilkan jika tersembunyi
    if (input.style.display === 'none' || input.style.display === '') {
      input.style.display = 'inline-block'; // Menampilkan input
      input.focus(); // Fokuskan input
    } else {
      input.style.display = 'none'; // Menyembunyikan input lagi
    }
  });

  
  document.addEventListener("DOMContentLoaded", function () {
    // Menginisialisasi tooltip di seluruh elemen yang memiliki atribut 'data-bs-toggle="tooltip"'
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));
  
    const fields = ["nama_lengkap", "email", 'jenis_kelamin', 'tgl_lahir']; // List ID dari semua input dan display fields
    const editBtn = document.getElementById("personal-edit-btn");
    const saveBtn = document.getElementById("save-btn");
  
    let originalValues = {}; // Menyimpan nilai asli dari setiap field
    let isEditing = false; // Menyimpan status apakah sedang dalam mode edit
  
    // Menyimpan nilai asli saat pertama kali halaman dimuat
    fields.forEach(id => {
      const inputField = document.getElementById(id);
      originalValues[id] = inputField.value;
    });
  
    // Fungsi untuk toggle antara tampilan edit dan tampilkan
    function toggleEditMode(isEditing) {
      fields.forEach(id => {
        const displayField = document.getElementById(`${id}_display`);
        const inputField = document.getElementById(id);
  
        if (isEditing) {
          // Mode edit: sembunyikan text dan tampilkan input
          displayField.classList.add("d-none");
          inputField.classList.remove("d-none");
        } else {
          // Mode tampil: sembunyikan input dan tampilkan text
          displayField.textContent = inputField.value || "Data tidak tersedia"; // Update display text
          inputField.classList.add("d-none");
          displayField.classList.remove("d-none");
        }
      });
  
      // Menampilkan atau menyembunyikan tombol simpan
      saveBtn.classList.toggle("d-none", !isEditing);
  
      // Toggle icon pada tombol edit (pencil <-> close)
      editBtn.classList.toggle("lni-pencil", !isEditing);
      editBtn.classList.toggle("lni-cross-circle", isEditing);
  
      // Update tooltip untuk tombol edit
      editBtn.setAttribute('data-bs-original-title', isEditing ? 'Klik untuk membatalkan aksi' : 'Klik untuk edit data');
    }
  
    // Menangani event klik pada tombol edit
    editBtn.addEventListener("click", function () {
      isEditing = !isEditing;
  
      if (!isEditing) {
        // Simpan nilai baru hanya jika dalam mode edit
        fields.forEach(id => {
          const inputField = document.getElementById(id);
          originalValues[id] = inputField.value; // Simpan nilai baru saat selesai edit
        });
      }
  
      // Toggle mode edit/tampil
      toggleEditMode(isEditing);
    });
  });
  

  document.addEventListener("DOMContentLoaded", function () {
    // Tooltip
    const tooltipTriggerList = document.querySelectorAll('[data-bs-toggle="tooltip"]');
    tooltipTriggerList.forEach(tooltipTriggerEl => new bootstrap.Tooltip(tooltipTriggerEl));

    // Field IDs untuk Account Information
    const accountFields = ["username", "password", "old_password"];
    const accountEditBtn = document.getElementById("account-edit-btn");
    const accountSaveBtn = document.getElementById("account-save-btn");

    let isAccountEditing = false;

    function toggleAccountEditMode(isEditing) {
      accountFields.forEach(id => {
        const displayField = document.getElementById(`${id}_display`);
        const inputField = document.getElementById(id);

        // Tampilkan atau sembunyikan display/input field
        if (isEditing) {
          if (displayField) displayField.classList.add("d-none");
          inputField.classList.remove("d-none");

          // Khusus old_password, tampilkan wrapper-nya
          if (id === "old_password") {
            const groupWrapper = document.getElementById("old_password_group");
            if (groupWrapper) groupWrapper.classList.remove("d-none");
          }
        } else {
          if (displayField) {
            if (id === "password") {
              displayField.textContent = "******";
            } else {
              displayField.textContent = inputField.value || "Data tidak tersedia";
            }
            displayField.classList.remove("d-none");
          }
          inputField.classList.add("d-none");

          if (id === "old_password") {
            const groupWrapper = document.getElementById("old_password_group");
            if (groupWrapper) groupWrapper.classList.add("d-none");
          }
        }
      });

      // Toggle tombol simpan
      accountSaveBtn.classList.toggle("d-none", !isEditing);

      // Toggle ikon dan tooltip tombol edit
      accountEditBtn.classList.toggle("lni-pencil", !isEditing);
      accountEditBtn.classList.toggle("lni-cross-circle", isEditing);
      accountEditBtn.setAttribute('data-bs-original-title', isEditing ? 'Klik untuk membatalkan aksi' : 'Klik untuk edit data');
    }

    // Tombol edit diklik
    accountEditBtn.addEventListener("click", function () {
      isAccountEditing = !isAccountEditing;
      toggleAccountEditMode(isAccountEditing);
    });
  });
