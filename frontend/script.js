document.getElementById('export-button').addEventListener('click', exportDocument)
async function exportDocument() {
  const wikiUrl = document.getElementById('wiki-url').value
  const docType = document.getElementById('export-type').value

  const statusDisplay = document.getElementById('status')
  statusDisplay.textContent = 'Processing...'

  try {
    const response = await fetch('https://export-wiki-backend-66108743706.us-west1.run.app/export', {
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
      let errorBody
      try {
        errorBody = await response.json()
      } catch {
        errorBody = { message: "Unknown error" }
      }

      const err = new Error(errorBody.message || `HTTP ${response.status}`)
      err.status = response.status
      err.body = errorBody
      throw err
    }
    if (response.headers.get('content-type')?.includes('application/json')) {
      const data = await response.json()
      console.error('Error from server:', data)
      alert(data.message || "Unknown error")
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
    if (error.status === 422) {
      alert("Invalid URL. Please enter a valid GitHub repository or wiki URL.")
      statusDisplay.textContent = 'Invalid URL. Please try again.'
      return
    }
    alert("An unexpected error occurred. Please try again.")
    console.error('Error fetching data', error)
    statusDisplay.textContent = 'Error occurred. Please try again.'
  }
}