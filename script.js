document.getElementById('export-button').addEventListener('click', exportDocument)
async function exportDocument() {
  const entryDisplay = document.getElementById('entry')
  entryDisplay.innerHTML = 'Processing...'

  const wikiUrl = document.getElementById('wiki-url').value
  const docType = document.getElementById('export-type').value

  try {
    const response = await fetch('http://127.0.0.1:8000/export', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        wiki_url: wikiUrl,
        doc_type: docType
      })
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }

    const data = await response.json()
    entryDisplay.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`
  } catch (error) {
    entryDisplay.innerHTML = `Error: ${error.message}`
    console.error('Error fetching data', error)
  }
}