document.getElementById('fetchCount').addEventListener('click', fetchCount)
async function fetchCount() {
  const dataDisplay = document.getElementById('dataDisplay')
  dataDisplay.innerHTML = 'Loading...'

  try {
    const response = await fetch('http://127.0.0.1:8000/count/')

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    dataDisplay.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`
  } catch (error) {
    dataDisplay.innerHTML = `Error: ${error.message}`
    console.error('Error fetching data', error)
  }
}

document.getElementById('incrementCount').addEventListener('click', incrementCount)
async function incrementCount() {
  const dataDisplay = document.getElementById('dataDisplay')
  dataDisplay.innerHTML = 'Loading...'

  try {
    const response = await fetch('http://127.0.0.1:8000/count/increment', {
      method: 'PUT'
    })

    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`)
    }
    const data = await response.json()

    dataDisplay.innerHTML = `<pre>${JSON.stringify(data, null, 2)}</pre>`
  } catch (error) {
    dataDisplay.innerHTML = `Error: ${error.message}`
    console.error('Error fetching data', error)
  }
}