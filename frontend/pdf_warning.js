document.getElementById('export-type').addEventListener('change', function() {
  var selectedValue = this.value;
  if (selectedValue === 'PDF') {
    document.getElementById('status').textContent = 'Warning: PDF export may not preserve all formatting or images.';
    document.getElementById('status').style.color = 'red';
  }
  else {
    document.getElementById('status').textContent = 'Enter a valid github wiki URL and select the export format.';
    document.getElementById('status').style.color = 'black';
  }
});