document.getElementById('export-button').addEventListener('click', exportDocument)
async function exportDocument() {
  const entryDisplay = document.getElementById('entry')

  const wikiUrl = document.getElementById('wiki-url').value
  const docType = document.getElementById('export-type').value

  const statusDisplay = document.getElementById('status')
  statusDisplay.textContent = 'Processing...'

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
    if (response.headers.get('content-type')?.includes('application/json')) {
      const data = await response.json()
      statusDisplay.textContent = `Error: ${JSON.stringify(data)}`
    } else {
      const blob = await response.blob()
      const url = window.URL.createObjectURL(blob)
      const a = document.createElement('a')
      a.href = url
      a.download = `export.${docType.toLowerCase()}`
      document.body.appendChild(a)
      a.click()
      a.remove()
      window.URL.revokeObjectURL(url)

      document.getElementById('wiki-url').value = ''
      statusDisplay.textContent = 'Download complete!'
    }
  } catch (error) {
    statusDisplay.textContent = `Error: ${error.message}`
    console.error('Error fetching data', error)
  }
}