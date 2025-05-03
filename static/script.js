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